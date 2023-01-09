from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.core.cache import cache
from django_redis import get_redis_connection

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

import logging
from datetime import datetime, timedelta
import pytz
import json
from decimal import Decimal

from api.alteration import get_player_detail_top_day_info, get_day_game_status, get_interval_game_status, \
    get_game_type_from_info
from api.permission import HasAnyGroupPermission
from dao.maria import statistic_user_, alert

# Create your views here.

logger = logging.getLogger(__name__)


class GetOrderAlert(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        on_page
        page_size
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; data: {self.request.data})')

        query_dict = self.request.query_params
        _on_page: str = query_dict.get('on_page')
        _page_size: str = query_dict.get('page_size')
        if any(map(lambda i: i in ['', None], [_on_page, _page_size])):
            return Response('Request parameters not sufficient for GetOrderAlert!', status.HTTP_400_BAD_REQUEST)

        try:
            on_page = int(_on_page)
            page_size = int(_page_size)
            redis = get_redis_connection()
            _now = datetime.utcnow().strftime('%Y%m%dT%H%M')
            _key_prefix = f'risk:order:alert:{_now}:p' + '{on_page}'
            _key = _key_prefix.format(on_page=on_page)
            _mx_p_key = f'risk:order:alert:{_now}:maxp'
            logger.info(f'Get request: {self.request} with key: {_key}')
            _mx_page = redis.get(_mx_p_key)
            _res = redis.get(_key)
            if _res is None:
                logger.debug(f'Generate for {_key}')
                alerts = alert.get_recent_order_alert()
                _mx_p = 0
                for _p in range(0, len(alerts), page_size):
                    _page_user_info = alerts[_p:(_p+page_size)]
                    _p_key = _key_prefix.format(on_page=_p // page_size)
                    redis.setex(_p_key, 60, json.dumps(_page_user_info, cls=SupplyJsonEncoder))
                    _mx_p += 1

                redis.setex(_mx_p_key, 60, _mx_p)
                _res = redis.get(_key)
                _mx_page = redis.get(_mx_p_key)

            logger.debug('--- order alert with page ---')
            logger.debug(_res)
            logger.debug('--- order alert with page ---')
            _resp_data = {'alerts': [], 'max_page': 0}
            if _res is None:
                return Response(_resp_data)
            else:
                _resp_data['alerts'] = json.loads(_res.decode())
                _resp_data['max_page'] = json.loads(_mx_page.decode())
                return Response(_resp_data)

        except Exception:
            logger.exception(f'GetOrderAlert API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get order alert error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateAPIKey(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'POST': ['DA', 'rmsys'],
    }

    def post(self, request, format=None):
        """
        Get API key.
        """
        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        req_data = self.request.data
        key_name: [str, None] = req_data.get('key_name')
        secret: [str, None] = req_data.get('secret')
        if any(map(lambda i: i in ['', None], [key_name, secret, ])):
            return Response('Request parameters not sufficient for GenerateAPIKey!', status.HTTP_400_BAD_REQUEST)

        try:
            logger.debug(f'get secret: {secret}')
            if secret != 'RM_SYS_API_KEY_GENERATE':
                return Response('Request secret not match for GenerateAPIKey!', status.HTTP_403_FORBIDDEN)

            api_key, key = APIKey.objects.create_key(name=key_name)
            return Response({'message': f'Generate API key for {api_key.name} SUCCESS!', 'key': key})
        except Exception:
            logger.exception(f'GenerateAPIKey API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response(f'Generate API key error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBroadcastMessage(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, format=None):
        """
        Get message and broadcast to ws-channels.
        """
        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        req_data = self.request.data
        message: [str, None] = req_data.get('message')
        if any(map(lambda i: i in ['', None], [message, ])):
            return Response('Request parameters not sufficient for GetBroadcastMessage!', status.HTTP_400_BAD_REQUEST)

        try:
            logger.debug(f'get message: {message}')
            channel_layer = get_channel_layer()
            logger.debug(channel_layer)
            async_to_sync(channel_layer.group_send)(
                'risk_online', {'type': 'broadcast', 'message': json.loads(message)})
            return Response('Broadcast Success!')
        except Exception:
            logger.exception(f'GetBroadcastMessage API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response(f'Get broadcast message error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserLiveHedgeInfo(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        userid: str
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = self.request.query_params
        userid: [str, None] = query_dict.get('userid')
        if any(map(lambda i: i in ['', None], [userid,])):
            return Response('Request parameters not sufficient for GetUserLiveHedgeInfo!', status.HTTP_400_BAD_REQUEST)

        try:
            user_hedge_info = {'order': [], 'hedges': []}
            redis = get_redis_connection()
            _res_info = redis.get(f'risk:table:hedge:{userid}:info')
            _res_hedges = redis.get(f'risk:table:hedge:{userid}:hedges')
            if _res_info is not None:
                user_hedge_info['order'] = json.loads(_res_info.decode())
            if _res_hedges is not None:
                user_hedge_info['hedges'] = json.loads(_res_hedges.decode())
            logger.debug('--- user_hedge_info by game ---')
            logger.debug(user_hedge_info)
            logger.debug('--- user_hedge_info by game ---')
            return Response(user_hedge_info)

        except Exception:
            logger.exception(f'GetUserLiveHedgeInfo API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response(f'Get user({userid}) live hedge info error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetRecentLiveHedgeInfo(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        No params!
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        try:
            redis = get_redis_connection()
            _res = redis.get('risk:table:hedge:recent:info')
            if _res is None:
                live_hedge_info = []
            else:
                live_hedge_info = json.loads(_res.decode())
            logger.debug('--- live_hedge_info by game ---')
            logger.debug(live_hedge_info)
            logger.debug('--- live_hedge_info by game ---')
            return Response(live_hedge_info)

        except Exception:
            logger.exception(f'GetRecentLiveHedgeInfo API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get recent live hedge info error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserSummaryByGame(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        date: YYYY-MM-DD
        game_codes: '51' or '51,52'(example)
        on_page
        page_size
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = self.request.query_params
        date: str = query_dict.get('date')
        game_codes: str = query_dict.get('game_codes')
        _on_page: str = query_dict.get('on_page')
        _page_size: str = query_dict.get('page_size')
        if any(map(lambda i: i in ['', None], [game_codes, date, _on_page, _page_size])):
            return Response('Request parameters not sufficient for GetUserSummaryByGame!', status.HTTP_400_BAD_REQUEST)
        query_games = [_g.strip() for _g in game_codes.split(',')]
        if any(map(lambda g: get_game_type_from_info(g) in ['slot', ], query_games)):
            return Response(f'Given games({game_codes}) is not ready in GetUserSummaryByGame!',
                            status.HTTP_403_FORBIDDEN)

        try:
            on_page = int(_on_page)
            page_size = int(_page_size)
            redis = get_redis_connection()
            _key_prefix = f'risk:user:{date.replace("-", "")}:summary:{":".join(query_games)}:p' + '{on_page}'
            _key = _key_prefix.format(on_page=on_page)
            _mx_p_key = f'risk:user:{date.replace("-", "")}:summary:{":".join(query_games)}:maxp'
            logger.info(f'Get request: {self.request} with key: {_key}')
            _mx_page = redis.get(_mx_p_key)
            _res = redis.get(_key)
            if _res is None:
                logger.debug(f'Generate for {_key}')
                user_info = statistic_user_.get_user_summary_by_game(date, query_games)
                _mx_p = 0
                for _p in range(0, len(user_info), page_size):
                    _page_user_info = user_info[_p:(_p+page_size)]
                    _p_key = _key_prefix.format(on_page=_p // page_size)
                    redis.setex(_p_key, 30, json.dumps(_page_user_info, cls=SupplyJsonEncoder))
                    _mx_p += 1

                redis.setex(_mx_p_key, 30, _mx_p)
                _res = redis.get(_key)
                _mx_page = redis.get(_mx_p_key)

            logger.debug('--- user_info by game and page ---')
            logger.debug(_res)
            logger.debug('--- user_info by game and page ---')
            _resp_data = {'summary': [], 'max_page': 0}
            if _res is None:
                return Response(_resp_data)
            else:
                _resp_data['summary'] = json.loads(_res.decode())
                _resp_data['max_page'] = json.loads(_mx_page.decode())
                return Response(_resp_data)

        except Exception:
            logger.exception(f'GetUserSummaryByGame API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get user summary by game error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetNewsWinStatic(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        date: YYYY-MM-DD
        game_codes: '51' or '51,52'(example)
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = self.request.query_params
        date: [str, None] = query_dict.get('date')
        game_codes: [str, None] = query_dict.get('game_codes')
        if any(map(lambda i: i in ['', None], [game_codes, date, ])):
            return Response('Request parameters not sufficient for GetNewsWinStatic!', status.HTTP_400_BAD_REQUEST)
        elif any(map(lambda g: get_game_type_from_info(g) in ['slot', ], game_codes.split(','))):
            return Response(f'Given games({game_codes}) is not ready in GetNewsWinStatic!', status.HTTP_403_FORBIDDEN)

        try:
            news_win_static = statistic_user_.get_news_win_static(
                date, game_codes.split(','))
            logger.debug('--- news_win_static ---')
            logger.debug(news_win_static)
            logger.debug('--- news_win_static ---')
            return Response(news_win_static)

        except Exception:
            logger.exception(f'GetHourSummary API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get hour summary error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetHourSummary(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        date: YYYY-MM-DD
        game_codes: '51' or '51,52'(example)
        game_type: str('table')(example)
        userid: Optional[str'']
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = self.request.query_params
        date: [str, None] = query_dict.get('date')
        game_codes: [str, None] = query_dict.get('game_codes')
        game_type: [str, None] = query_dict.get('game_type')
        uid: [str, None] = query_dict.get('uid')
        if any(map(lambda i: i in ['', None], [game_codes, date, game_type])):
            return Response('Request parameters not sufficient for GetHourSummary!', status.HTTP_400_BAD_REQUEST)
        elif game_type in ['slot', ]:
            return Response(f'Given games({game_codes}) is not ready in GetHourSummary!', status.HTTP_403_FORBIDDEN)

        try:
            query_start_date = date + ' 00:00:00'
            query_end_date = date + ' 23:00:00'
            _hour_info = statistic_user_.get_hour_game_info(
                query_start_date, query_end_date, game_codes.split(','), game_type, uid)
            hour_info = []
            query_dt = datetime.strptime(date, '%Y-%m-%d')
            for _k, _v in _hour_info.items():
                _game_name = _v['game']
                for i in range(24):
                    _dt_k = (query_dt + timedelta(hours=i)).strftime('%Y-%m-%d %H:00:00')
                    _info = _v.get(_dt_k, {'bets': 0, 'net_win': 0, 'rounds': 0, 'players': 0})
                    _info.update({'datetime': _dt_k, 'game': _game_name})
                    hour_info.append(_info)

            logger.debug('--- hour_info ---')
            logger.debug(hour_info)
            logger.debug('--- hour_info ---')
            return Response(hour_info)

        except Exception:
            logger.exception(f'GetHourSummary API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get hour summary error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserSummaryByRule(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):
        """
        date: YYYY-MM-DD
        game_codes: '51' or '51,52'(example)
        rule: choice['HNW', 'HCNW', 'NWDC', 'ABR']
        """

        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = self.request.query_params
        date: [str, None] = query_dict.get('date')
        game_codes: [str, None] = query_dict.get('game_codes')
        rule: [str, None] = query_dict.get('rule')
        if any(map(lambda i: i in ['', None], [game_codes, date, rule])):
            return Response('Request parameters not sufficient for GetUserSummaryByRule!', status.HTTP_400_BAD_REQUEST)
        elif any(map(lambda g: get_game_type_from_info(g) in ['slot', ], game_codes.split(','))):
            return Response(f'Given games({game_codes}) is not ready in GetUserSummaryByRule!', status.HTTP_403_FORBIDDEN)

        try:
            user_info = statistic_user_.get_user_summary_by_game_and_rule(date, game_codes.split(','), rule)
            logger.debug('--- user_info by rule ---')
            logger.debug(user_info)
            logger.debug('--- user_info by rule ---')
            return Response(user_info)

        except Exception:
            logger.exception(f'GetUserSummaryByRule API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get user summary by rule error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPlayerDetail(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
        'POST': ['DA', 'rmsys'],
        'PUT': ['__all__'],
    }

    def post(self, request, format=None):

        req_dict = request.POST
        logger.info('---get player detail params---')
        logger.info(req_dict)
        logger.info(request.data)
        logger.info('---get player detail params---')
        req_data = request.data
        user_ssid = req_data.get('user_ssid')
        query_dates = req_data.get('query_dates')

        if user_ssid is None or query_dates is None:
            return Response('Request data not sufficient!', status.HTTP_400_BAD_REQUEST)

        resp_dict = {}
        try:
            for str_dt in query_dates:
                dt = datetime.strptime(str_dt, '%Y-%m-%d')
                dt = dt.replace(tzinfo=pytz.UTC)
                resp_dict.setdefault(
                    str_dt, cache.get_or_set(
                        'GPD_' + dt.strftime('%Y%m%d_') + user_ssid,
                        get_player_detail_top_day_info(dt, dt + timedelta(days=1), user_ssid),
                        12 * 60 * 60
                    )
                )
            return Response(resp_dict)

        except Exception:
            issue = 'GetPlayerDetail API error => \n'
            logger.exception(issue)
            return Response('Get player detail error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetGameStatus(APIView):
    permission_classes = [IsAuthenticated, HasAnyGroupPermission]
    required_groups = {
        'GET': ['DA', 'rmsys'],
        'POST': ['DA', 'rmsys'],
    }

    def get(self, request, format=None):

        # for get POST data
        # request.data
        # for get GET query
        # request.query_params
        # return as django.http.QueryDict

        today = datetime.utcnow()
        logger.info(f'Get request: {self.request}! (param: {self.request.query_params}; '
                    f'data: {self.request.data})')

        query_dict = request.query_params
        game_type: [str, None] = query_dict.get('game_type')
        interval: [str, None] = query_dict.get('interval')
        if any(map(lambda i: i in ['', None], [game_type, interval])):
            return Response('Request parameters not sufficient for GetGameStatus!', status.HTTP_400_BAD_REQUEST)

        try:
            if interval.upper() == 'DAY':
                resp_dict = cache.get_or_set(
                    'GGS_' + today.strftime('%Y%m%d_') + game_type,
                    get_day_game_status(today, game_type),
                    12 * 60 * 60
                )
                return Response(resp_dict)
            elif interval.upper() == 'MIN':
                resp_dict = cache.get_or_set(
                    'GGS_' + today.strftime('%Y%m%dT%H:%M_') + game_type,
                    get_interval_game_status(today, game_type),
                    15 * 60
                )
                return Response(resp_dict)
            else:
                return Response(f'GetGameStatus do not process for interval: {interval.upper()}!',
                                status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception(f'GetGameStatus API (param: {self.request.query_params}; data: {self.request.data}) FAILED!')
            return Response('Get game status error!', status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupplyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # decimal to float
            return round(float(obj), 2)
        elif isinstance(obj, set):
            # only set of strings can be joined
            return ','.join(obj)
        elif isinstance(obj, bytes):
            return obj.decode()
        return super(SupplyJsonEncoder, self).default(obj)

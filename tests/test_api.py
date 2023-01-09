from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase, APITransactionTestCase
from unittest.mock import Mock

import json
import logging
from datetime import datetime, timedelta
from operator import itemgetter

from rmsys import util
from dao.mongo import gamedetail
from api.alteration import update_by_betNwin_info, get_win_multiplier_level

logger = logging.getLogger(__name__)


class NoDBAndAuthAPITest(APITestCase):
    """
    run in terminal:
        python manage.py test tests.test_api.NoDBAndAuthAPITest --testrunner=tests.test_dao.NoDbTestRunner
    """
    databases = {'default_read', 'maria_read', 'mareport_read', }

    def setUp(self) -> None:
        """
        REMEMBER to set permission_classes = [HasAnyGroupPermission] !!!
        """
        from api.permission import HasAnyGroupPermission
        HasAnyGroupPermission.has_permission = Mock(return_value=True)
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_order_alert(self):
        param = {
            'on_page': 4,
            'page_size': 10
        }
        resp = self.client.get('/api/order/alert', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_user_live_hedge_info(self):
        param = {
            'userid': '619c62e9ee3dd0000112d485'
        }
        resp = self.client.get('/api/getuserlivehedgeinfo', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_recent_live_hedge_info(self):
        param = {}
        resp = self.client.get('/api/getrecentlivehedgeinfo', content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_user_summary_by_game(self):
        param = {
            'date': '2021-12-10',
            'game_codes': '196,GO169',
            'on_page': 0,
            'page_size': 2
        }
        resp = self.client.get('/api/getusersummarybygame', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_news_win_static(self):
        param = {
            'date': '2021-11-15',
            'game_codes': '217,GO01',
        }
        resp = self.client.get('/api/getnewswinstatic', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_hour_summary(self):
        param = {
            'date': '2021-11-14',
            'game_codes': '217,GO01',
            'game_type': 'arcade',
            'uid': ''
        }
        resp = self.client.get('/api/gethoursummary', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_game_daily_info(self):
        param = {
            'game_type': 'table',
            'interval': 'day',
        }
        resp = self.client.get('/api/getgamestatus', data=param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)
        logger.info(type(resp.data))

    def test_get_user_summary_by_rule(self):
        param = {
            'date': '2021-11-14',
            'game_codes': '217,GO01',
            'rule': 'ABR',
        }
        resp = self.client.get('/api/getusersummarybyrule', param, content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)


class APITest(APITransactionTestCase):
    """
    run in terminal:
        python manage.py test tests.test_api.APITest
    """

    def setUp(self) -> None:

        # create user
        group = Group(name='DA')
        group.save()
        self.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        self.test_user1.save()
        self.test_user1.groups.add(group)
        self.test_user1.save()
        group = Group(name='rmsys')
        group.save()
        self.test_user2 = User.objects.create_user(username='testuser2', password='12345')
        self.test_user2.save()
        self.test_user2.groups.add(group)
        self.test_user2.save()
        self.test_user3 = User.objects.create_user(username='testuser3', password='12345')
        self.test_user3.save()
        # self.client = APIClient()

    def tearDown(self) -> None:
        # self.client.logout()
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_game_daily_info(self):
        # self.client.force_authenticate(user=self.test_user1)
        param = {
            'game_type': 'table',
            'interval': 'day',
        }
        resp = self.client.get('/api/getgamestatus', param)
        logger.info(resp)
        logger.info(resp.data)

    def test_failed_group_get_game_daily_info(self):
        self.client.force_authenticate(user=self.test_user3)
        data = {
            'game_type': 'table',
        }
        resp = self.client.get('/api/getgamestatus', data)
        logger.info(resp)
        logger.info(resp.data)

    def test_post_game_daily_info(self):
        self.client.force_authenticate(user=self.test_user1)
        data = {
            'game_type': 'slot',
        }
        resp = self.client.post(
            '/api/getgamedailyinfo', data=json.dumps(data),
            content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_player_detail(self):
        self.client.force_authenticate(user=self.test_user1)
        data = {
            'user_ssid': 'test',
            'query_dates': ['2021-07-28']
        }
        resp = self.client.post(
            '/api/getplayerdetail', data=json.dumps(data),
            content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_player_detail_without_group(self):
        self.client.force_authenticate(user=self.test_user3)
        data = {
            'user_ssid': 'test',
            'query_dates': ['2021-07-28']
        }
        resp = self.client.post(
            '/api/getplayerdetail', data=json.dumps(data),
            content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)

    def test_get_player_detail_error(self):
        self.client.force_authenticate(user=self.test_user2)
        data = {
            'user_ssid': 'test',
        }
        resp = self.client.post(
            '/api/getplayerdetail', data=json.dumps(data),
            content_type='application/json;charset=utf-8')
        logger.info(resp)
        logger.info(resp.data)


class AlterationTest(APITestCase):
    """
    run in terminal:
        python manage.py test tests.test_api.AlterationTest
    """

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_get_player_detail_top_day_info(self):
        # 610aa3883834690001826014, 60eef530160017000104679e, 60e9af39160017000103e74f, 60eef530160017000104679e
        user_ssid = '60e9af39160017000103e74f'
        check_dt = util.get_datawarehouse_latest_date()
        infos = gamedetail.get_player_game_detail(check_dt - timedelta(days=2), check_dt - timedelta(days=1), user_ssid)

        logger.debug('--- origin data ---')
        logger.debug(infos)
        logger.debug('---------')

        chart_infos = list()
        rec_info = {
            'net_win': 0,
            'main_bet': 0,
            'RTP': 96,
            'games': 0,
            'rounds': 0,
            'max_win': 0,
            'max_win_bet': 0,
            'max_win_game': '51',
            'max_win_type': 'base',
            'max_win_multiplier': 0,
        }
        bar_info = {
            'multiple': {},
            'bet': {},
            'time': {},
        }

        _game_counts = set([])
        _total_bet = 0
        _total_win = 0
        _total_round = 0
        _multiple_stat = {}
        _bet_stat = {}
        _fg_info = {}

        for i in range(len(infos)):
            _game_code = infos[i].get('gameCode', '0')
            _game_counts.add(_game_code)
            _start_time = infos[i].get('startTime').strftime('%Y-%m-%d %H:00:00')
            _gt = 'gt' + str(i + 1)
            _fg_info_by_game = _fg_info.setdefault(_game_code, {'rounds': 0, 'free_game_times': 0})
            _bet_infos = sorted(infos[i].get('betInfos'), key=itemgetter('roundth'))
            _win_infos = sorted(infos[i].get('multipleWinInfos'), key=itemgetter('roundth'))

            _total_bet, _total_win, _total_round = update_by_betNwin_info(
                rec_info, chart_infos,
                _win_infos, _bet_infos,
                _gt, _game_code, _start_time, _total_bet, _total_win, _total_round,
                _fg_info_by_game, _bet_stat
            )

            for _mul_stat in infos[i].get('multipleWinStats'):
                _mul_range = _mul_stat.get('mulRange', 0)
                _mul_level = get_win_multiplier_level(_mul_range)
                if _mul_level not in _multiple_stat.keys():
                    _multiple_stat[_mul_level] = _mul_stat.get('rounds', 0)
                else:
                    _multiple_stat[_mul_level] += _mul_stat.get('rounds', 0)

            for _feature_info in infos[i].get('featureInfos'):
                if _feature_info.get('featureType') == 'freespin':
                    _fg_info_by_game['free_game_times'] += 1

        sorted_bets = sorted(_bet_stat.items(), key=lambda item: item[1], reverse=True)
        rec_info['net_win'] = round(_total_win - _total_bet, 2)
        if sorted_bets:
            rec_info['main_bet'] = sorted_bets[0][0]
        rec_info['RTP'] = round(_total_win*100 / _total_bet, 2)
        rec_info['games'] = len(_game_counts)
        rec_info['rounds'] = _total_round

        bar_info['multiple'] = _multiple_stat.copy()
        bar_info['bet'] = _bet_stat.copy()
        bar_info['time'] = _fg_info.copy()

        logger.debug('--- user bet detail ---')
        logger.debug('--- chart info ---')
        logger.debug(chart_infos.copy())
        logger.debug('--- record info ---')
        logger.debug(rec_info.copy())
        logger.debug('--- bar info ---')
        logger.debug(bar_info.copy())
        logger.debug('------')

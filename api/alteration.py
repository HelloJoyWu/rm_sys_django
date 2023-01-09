import logging
import pytz
from datetime import datetime, timedelta
from typing import List, Union
from operator import itemgetter
from collections import OrderedDict

from django.core.cache import cache

from dao.mongo import gamedetail
from api.models import GameInfo, DayGameStatus, IntervalGameStatus
from dao.maria import statistic_user_

logger = logging.getLogger(__name__)


def get_game_type_from_info(game_code: str) -> str:
    try:
        return GameInfo.objects.get(game_code=game_code).game_type
    except Exception:
        logger.exception(f'Not find game type for game code = \'{game_code}\'!')
        return ''


def get_interval_game_status(utc_today: datetime, game_type: str):

    interval = 15  # minutes
    _to_time = datetime(
        utc_today.year, utc_today.month, utc_today.day, utc_today.hour,
        int(utc_today.minute // interval) * interval, tzinfo=pytz.UTC)
    _from_time = _to_time - timedelta(hours=24)
    default_len = int(24 * 60 / interval)
    all_status = {}
    label_dates = [_from_time + timedelta(minutes=interval * i) for i in range(default_len)]

    query_sets = IntervalGameStatus.objects.filter(
        date__gte=_from_time, date__lt=_to_time, game_type=game_type
    ).order_by('date')

    attrs = ['bets', 'incomes', 'rounds', 'players']
    game_set = set()
    for status in query_sets:
        _game_code = status.game_code
        game_set.add(_game_code)
        the_game_status = all_status.setdefault(_game_code, {})

        for _attr in attrs:
            attr_results = the_game_status.setdefault(_attr, [0] * default_len)
            try:
                attr_results[label_dates.index(status.date)] = getattr(status, _attr)
            except ValueError:
                logger.exception(f'On [{_to_time}, {game_type}], setup interval game({_game_code}) status FAILED!')
                continue

    all_status['info'] = {_gc: __get_game_name(_gc) for _gc in game_set}
    all_status['dates'] = label_dates

    return all_status


def get_day_game_status(utc_today: datetime, game_type: str) -> dict:

    interval = 7  # days
    _to_time = datetime(utc_today.year, utc_today.month, utc_today.day, tzinfo=pytz.UTC).date()
    _from_time = _to_time - timedelta(days=interval)
    label_dates = [_from_time + timedelta(days=i) for i in range(interval)]

    query_sets = DayGameStatus.objects.filter(
        date__gte=_from_time, date__lt=_to_time, game_type=game_type
        ).order_by('date')

    attrs = ['bets', 'incomes', 'rounds', 'players']
    all_status = {}
    game_set = set()
    for status in query_sets:
        _game_code = status.game_code
        game_set.add(_game_code)
        the_game_status = all_status.setdefault(_game_code, {})

        for _attr in attrs:
            attr_results = the_game_status.setdefault(_attr, [0] * interval)
            try:
                attr_results[label_dates.index(status.date)] = getattr(status, _attr)
            except ValueError:
                logger.exception(f'On [{_to_time}, {game_type}], setup day game({_game_code}) status FAILED!')
                continue

    all_status['info'] = {_gc: __get_game_name(_gc) for _gc in game_set}
    all_status['dates'] = label_dates

    return all_status


def get_player_detail_top_day_info(start_dt: datetime, end_dt: datetime, user_ssid: str):
    # remember to return by .copy()

    infos = gamedetail.get_player_game_detail(start_dt, end_dt, user_ssid)

    logger.debug('--- origin data ---')
    logger.debug(infos)
    logger.debug('---------')

    chart_infos = list()
    win_info = list()
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
        _start_time = infos[i].get('startTime').strftime('%Y-%m-%d %H:%M:%S')
        _gt = 'Gt' + str(i + 1)
        _fg_info_by_game = _fg_info.setdefault(_game_code, {'rounds': 0, 'free_game_times': 0})
        _bet_infos = sorted(infos[i].get('betInfos', []), key=itemgetter('roundth'))
        _win_infos = sorted(infos[i].get('multipleWinInfos', []), key=itemgetter('roundth'))

        _the_bet_time = infos[i].get('startTime').strftime('%Y-%m-%d %H:%M:%S')
        _the_game_name = __get_game_name(_game_code)
        win_info += [{
            'bet_time': _the_bet_time,
            'roundid': _win.get('roundID'),
            'game': _the_game_name,
            'win': _win.get('win'),
            'bet': _win.get('bet'),
            'win_mutiplier': round(_division_no_zero(_win.get('win'), _win.get('bet')), 2),
            'win_type': __trans_win_type(_win.get('winType'))
        } for _win in _win_infos]

        _total_bet, _total_win, _total_round = update_by_betNwin_info(
            rec_info, chart_infos,
            _win_infos, _bet_infos,
            _gt, _game_code, _start_time, _total_bet, _total_win, _total_round,
            _fg_info_by_game, _bet_stat, _the_game_name
        )

        for _mul_stat in infos[i].get('multipleWinStats', []):
            _mul_range = _mul_stat.get('mulRange', 0)
            _mul_level = get_win_multiplier_level(_mul_range)
            if _mul_level not in _multiple_stat.keys():
                _multiple_stat[_mul_level] = _mul_stat.get('rounds', 0)
            else:
                _multiple_stat[_mul_level] += _mul_stat.get('rounds', 0)

        for _feature_info in infos[i].get('featureInfos', []):
            if _feature_info.get('featureType') == 'freespin':
                _fg_info_by_game['free_game_times'] += 1

    rec_info['net_win'] = round(_total_win - _total_bet, 2)
    try:
        rec_info['main_bet'] = max(_bet_stat, key=_bet_stat.get)
    except ValueError:
        pass
    rec_info['RTP'] = round(_division_no_zero(_total_win, _total_bet)*100, 2)
    rec_info['games'] = len(_game_counts)
    rec_info['rounds'] = _total_round
    rec_info['max_win_game'] = __get_game_name(rec_info['max_win_game'])

    _multiple_stat['total'] = sum(_multiple_stat.values())
    bar_info['multiple'] = _multiple_stat.copy()
    bar_info['bet'] = OrderedDict(sorted(_bet_stat.items(), key=lambda item: item[0]))
    bar_info['time'] = _fg_info.copy()

    win_info = sorted(win_info, key=lambda _info: _info.get('win_mutiplier'), reverse=True)[:3]

    logger.info(f'Set player({user_ssid}) info on {start_dt} success!')
    logger.debug('--- user bet detail ---')
    logger.debug('--- chart info ---')
    logger.debug(chart_infos)
    logger.debug('--- record info ---')
    logger.debug(rec_info)
    logger.debug('--- bar info ---')
    logger.debug(bar_info)
    logger.debug('------')
    logger.debug('--- win info ---')
    logger.debug(win_info)
    logger.debug('------')

    return {
        'chart_info': chart_infos.copy(),
        'record_info': rec_info.copy(),
        'bar_info': bar_info.copy(),
        'win_info': win_info.copy()
    }


def update_by_betNwin_info(
        rec_info: dict, chart_infos: List[dict],
        _win_infos: List[dict], _bet_infos: List[dict],
        _gt: str, _game_code: str, _start_time: str,
        _total_bet: Union[int, float], _total_win: Union[int, float], _total_round: int,
        _fg_info_by_game: dict, _bet_stat: dict, _the_game_name: str
):

    _check_win = 0
    _last_win = len(_win_infos) - 1
    _last_bet = len(_bet_infos) - 1
    for _check_bet in range(len(_bet_infos)):
        _check_bet_info = _bet_infos[_check_bet]
        _total_bet += _check_bet_info.get('bets', 0)
        _total_win += _check_bet_info.get('wins', 0)
        _total_round += _check_bet_info.get('rounds', 0)
        _fg_info_by_game['rounds'] += _check_bet_info.get('rounds', 0)

        if _check_bet_info.get('bet') not in _bet_stat.keys():
            _bet_stat[_check_bet_info.get('bet')] = _check_bet_info.get('rounds')
        else:
            _bet_stat[_check_bet_info.get('bet')] += _check_bet_info.get('rounds')

        _chart_info = {
            'game': _the_game_name,
            'roundth': str(_check_bet_info.get('roundth')) + 'th',
            'start_time': _start_time,
            'bet': _check_bet_info.get('bet'),
            'total_bet': _check_bet_info.get('bets'),
            'total_round': _check_bet_info.get('rounds'),
            'max_win_multiple': 0,
            'max_win_multiple_win': 0,
        }

        while True:
            if _check_win > _last_win or _last_win == -1:
                break

            if _check_bet + 1 <= _last_bet:
                _this_roundth = _check_bet_info.get('roundth')
                _next_roundth = _bet_infos[_check_bet + 1].get('roundth')

                if _this_roundth <= _win_infos[_check_win].get('roundth') < _next_roundth:
                    update_by_max_win_info(rec_info, _chart_info, _win_infos[_check_win], _game_code)
                else:
                    break

            else:
                update_by_max_win_info(rec_info, _chart_info, _win_infos[_check_win], _game_code)

            _check_win += 1

        chart_infos.append(_chart_info)

    return _total_bet, _total_win, _total_round


def update_by_max_win_info(rec_info: dict, chart_info: dict, win_info: dict, this_game_code: str):
    """
    Update max_win_multiple and max_win_multiple_win if this time's 'win multiplier' is bigger.
    """
    _this_win = win_info.get('win')
    _this_bet = win_info.get('bet')
    _this_win_multiple = round(_this_win / _this_bet, 2)
    if _this_win_multiple > chart_info['max_win_multiple']:
        chart_info['max_win_multiple'] = _this_win_multiple
        chart_info['max_win_multiple_win'] = _this_win

    if _this_win > rec_info['max_win']:
        rec_info['max_win'] = _this_win
        rec_info['max_win_bet'] = _this_bet
        rec_info['max_win_game'] = this_game_code
        rec_info['max_win_type'] = __trans_win_type(win_info.get('winType'))
        rec_info['max_win_multiplier'] = _this_win_multiple


def get_win_multiplier_level(win_mutiplier: Union[int, float]):

    if win_mutiplier <= 20:
        return '20'
    elif 20 < win_mutiplier <= 50:
        return '50'
    elif 50 < win_mutiplier <= 100:
        return '100'
    elif 100 < win_mutiplier < 1000:
        return str(((win_mutiplier // 100) + 1) * 100)
    else:
        return '1000+'


def _division_no_zero(numerator: Union[int, float], denominator: Union[int, float]):

    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def __trans_win_type(win_type: Union[None, str]) -> str:

    if win_type == 'freespin':
        return '免費遊戲'
    elif win_type == 'bonus':
        return '特色遊戲'
    elif win_type == 'jackpots':
        return '累積遊戲'
    else:
        return '主遊戲'


def __get_game_name(game_code: str) -> str:
    try:
        return GameInfo.objects.get(game_code=game_code).game_name_tw
    except Exception:
        logger.exception(f'Not find game name tw for game code = \'{game_code}\'!')
        return game_code


def __nested_dict_cumulative_update(origin_dict: dict, updated_dict: dict):

    for _k, _dict_v in updated_dict.items():
        if _k not in origin_dict.keys():
            origin_dict[_k] = _dict_v
        else:
            if 'bets' in _dict_v.keys():
                for __k, __v in _dict_v.items():
                    if __k in ('bets', 'net_win', 'rounds', 'play_hours'):
                        origin_dict[_k][__k] += __v
            else:
                __nested_dict_cumulative_update(origin_dict[_k], updated_dict[_k])

    return origin_dict

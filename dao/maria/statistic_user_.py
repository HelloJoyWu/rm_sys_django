import logging
from typing import Callable, Union, Optional
from decimal import Decimal

from django.db import connections

logger = logging.getLogger(__name__)


def get_user_summary_by_game(
        check_date: str, game_codes: list
) -> list:
    """
    Note: net-win is based on player!
    """

    stmt = 'SELECT CAST(plo.account AS CHAR), CAST(plp.account AS CHAR), CAST(ul.account AS CHAR), su.uid, DATE_FORMAT(ul.update_time, \'%Y-%m-%d\'), gi.game_name_tw, '
    stmt += '  ROUND(su.total_bet/su.rate), ROUND((su.total_win - su.total_bet - su.total_rake - su.room_fee)/su.rate), '
    stmt += '  su.total_round, su.play_hour '
    stmt += 'FROM daSystem.summarized_user su '
    stmt += 'JOIN cypress.parent_list plo ON su.oid = plo.id '
    stmt += 'JOIN cypress.parent_list plp ON su.pid = plp.id '
    stmt += f'JOIN MaReport.game_info gi ON su.gid = gi.gid AND gi.game_code IN ({str(game_codes)[1:-1]}) '
    stmt += 'JOIN cypress.user_list ul ON su.uid = ul.id '
    stmt += f'WHERE su.date = \'{check_date}\' '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)
        logger.info(f'Get game({str(game_codes)[1:-1]}) user summary on {check_date} SUCCESS!')

        _res = list(cursor)
        if _res:
            summary = [{
                'owner': info[0], 'parent': info[1], 'user': info[2], 'uid': info[3], 'registered_date': info[4],
                'game_name': info[5], 'bets': info[6], 'net_wins': info[7], 'rounds': info[8], 'play_hour': info[9],
            } for info in _res]
        else:
            summary = []

        return summary


def get_news_win_static(
        check_date: str, game_codes: list
) -> list:
    """
    Note: net-win is based on player!
    """

    stmt = 'SELECT plo.account, gi.game_name_tw, COUNT(DISTINCT su.uid), '
    stmt += 'SUM(CASE WHEN (su.total_win - su.total_bet - su.total_rake - su.room_fee) > 0 THEN 1 ELSE 0 END), '
    stmt += 'SUM((su.total_win - su.total_bet - su.total_rake - su.room_fee)/su.rate), '
    stmt += 'su.total_round, su.play_hour '
    stmt += 'FROM daSystem.summarized_user su '
    stmt += 'JOIN cypress.parent_list plo ON su.oid = plo.id '
    stmt += f'JOIN MaReport.game_info gi ON su.gid = gi.gid AND gi.game_code IN ({str(game_codes)[1:-1]}) '
    stmt += f'JOIN cypress.user_list ul ON su.uid = ul.id AND ul.update_time >= \'{check_date}\' '
    stmt += f'WHERE su.date = \'{check_date}\' '
    stmt += 'GROUP BY su.oid, su.gid '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)
        logger.info(f'Get game({str(game_codes)[1:-1]}) news win static on {check_date} SUCCESS!')

        _res = list(cursor)
        if _res:
            summary = [{
                'owner': info[0], 'game': info[1], 'players': info[2], 'win_players': info[3], 'net_win': info[4],
            } for info in _res]
        else:
            summary = []

        return summary


def get_hour_game_info(
        start_time: str, end_time: str, game_codes: list, game_type: str, uid: Optional[int] = None
) -> dict:
    """
    Note: net-win is based on player!
    """
    stmt = 'SELECT gi.game_code, DATE_FORMAT(ug.date, \'%Y-%m-%d %H:00:00\'), gi.game_name_tw, SUM(ug.total_bet/rpl.rate) bets, '
    if game_type in ('slot', 'fish', 'arcade'):
        stmt += '  SUM((ug.total_win - ug.total_bet)/rpl.rate), SUM(ug.total_round), COUNT(DISTINCT ug.uid) '
        stmt += 'FROM cypress.statistic_user_by_game ug '
    elif game_type in ('table', 'live'):
        stmt += '  SUM((ug.total_rake - ug.total_win + ug.room_fee)/rpl.rate), SUM(ug.total_round), COUNT(DISTINCT ug.uid) '
        stmt += 'FROM cypress.statistic_user_by_tablegame ug '
    else:
        stmt += '  SUM((ug.total_win - ug.total_bet)/rpl.rate), SUM(ug.total_bet_count), COUNT(DISTINCT ug.uid) '
        stmt += 'FROM cypress.statistic_user_by_lottogame ug '

    stmt += 'JOIN cypress.user_list ul ON ug.uid = ul.id '
    if uid not in (None, ''):
        stmt += f'AND ul.id = {uid} '
    stmt += 'JOIN MaReport.report_parent_list rpl ON ul.parentid = rpl.pid '
    stmt += f'JOIN MaReport.game_info gi ON ug.gid = gi.gid AND gi.game_code IN ({str(game_codes)[1:-1]}) '
    stmt += f'WHERE ug.date BETWEEN \'{start_time}\' AND  \'{end_time}\' '
    stmt += 'GROUP BY ug.date, ug.gid '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)
        logger.info(f'Get game({str(game_codes)[1:-1]}) hour summary between {start_time}~{end_time} SUCCESS!')

        _res = list(cursor)
        summary = {}
        if _res:
            for info in _res:
                _info = summary.setdefault(info[0], {})
                if 'game' not in _info.keys():
                    _info.update({'game': info[2]})
                _info.update({info[1]: {
                    'bets': info[3], 'net_win': info[4],
                    'rounds': info[5], 'players': info[6],
                }})

        return summary


def get_user_summary_by_game_and_rule(
        check_date: str, game_codes: list, rule: str
) -> list:
    """
    Note: net-win is based on player!
    """

    stmt = 'SELECT plo.account, plp.account, ul.account, su.uid, ul.update_time, gi.game_name_tw, '
    stmt += 'ROUND(su.total_bet/su.rate), ROUND((su.total_win - su.total_bet - su.total_rake - su.room_fee)/su.rate), '
    stmt += 'su.total_round, su.play_hour, rr.HCNW, rr.HCNW_on_hour '
    stmt += 'FROM daSystem.summarized_user su '
    stmt += 'JOIN daSystem.risk_record rr ON su.uid = rr.uid AND su.gid = rr.gid '
    stmt += f' AND su.date = rr.date AND rr.date = \'{check_date}\' '

    if rule == 'HNW':
        stmt += 'AND rr.is_HNW = 1 '
    elif rule == 'HCNW':
        stmt += 'AND rr.HCNW >= 6 '
    elif rule == 'NWDC':
        stmt += 'AND rr.NWDC >= 3 '
    elif rule == 'ABR':
        stmt += 'AND rr.ABR >= 100 '

    stmt += 'JOIN cypress.parent_list plo ON su.oid = plo.id '
    stmt += 'JOIN cypress.parent_list plp ON su.pid = plp.id '
    stmt += f'JOIN MaReport.game_info gi ON rr.gid = gi.gid AND gi.game_code IN ({str(game_codes)[1:-1]}) '
    stmt += 'JOIN cypress.user_list ul ON su.uid = ul.id '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)
        logger.info(f'Get game({str(game_codes)[1:-1]}) user summary on {check_date} by rule-{rule} SUCCESS!')

        _res = list(cursor)
        if _res:
            summary = [{
                'owner': info[0], 'parent': info[1], 'user': info[2], 'uid': info[3], 'registered_date': info[4],
                'game_name': info[5], 'bets': info[6], 'net_wins': info[7], 'rounds': info[8], 'play_hour': info[9],
                'HCNW': info[10], 'HCNW_on_hour': info[11],
            } for info in _res]
        else:
            summary = []

        return summary


def trans_num_type_prevent_none(tr_type: Callable, num: Decimal) -> Union[int, float]:
    if num is None:
        return 0
    else:
        return tr_type(num)

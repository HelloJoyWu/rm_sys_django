import logging
from collections import OrderedDict
from datetime import datetime
import json

from django.db import connections

from risk.models import PlayerBasicInfo

logger = logging.getLogger(__name__)


def get_risk_players(check_dt: str, check_interval: int) -> str:

    stmt = 'SELECT DATE_FORMAT(checkDate, \'%Y-%m-%d\'), playerID, account, owner, alertLevel '
    stmt += 'FROM alert.RiskPlayerAlert '
    stmt += f'WHERE checkDate >= DATE_SUB(\'{check_dt}\', INTERVAL {check_interval} DAY) AND checkDate < \'{check_dt}\' '
    stmt += '  AND alertLevel IN (\'A\', \'B\') '
    stmt += 'ORDER BY alertLevel '

    results = dict()
    try:
        with connections['maria_read'].cursor() as cursor:
            cursor.execute(stmt)
            for (dt, usr_ssid, usr_acc, o_acc, lvl) in list(cursor):
                results.setdefault(dt, {}).setdefault(lvl, []).append(
                    {'name': usr_acc,
                     'owner': o_acc,
                     'ssid': usr_ssid})
        return json.dumps(
            OrderedDict(sorted(results.items(), key=lambda d: datetime.strptime(d[0], '%Y-%m-%d'), reverse=True))
        )
    except:
        issue = 'Get risk player error =>\n'
        logger.exception(issue)
        return json.dumps(results)


def get_basic_info_by_ssid(user_ssid: str) -> PlayerBasicInfo:
    """
    return: PlayerBasicInfo
    """

    stmt = 'SELECT ul.account, ul.id, ul.userid, plp.account, plo.account, DATE_FORMAT(ul.update_time, \'%Y-%m-%d\') '
    stmt += 'FROM cypress.user_list ul '
    stmt += 'JOIN cypress.parent_list plp ON ul.parentid = plp.id '
    stmt += 'JOIN cypress.parent_list plo ON ul.ownerid = plo.id '
    stmt += f'WHERE ul.userid = \'{user_ssid}\' '

    try:
        with connections['maria_read'].cursor() as cursor:
            cursor.execute(stmt)
            (usr_acc, uid, ussid, p_acc, o_acc, reg_dt) = cursor.fetchone()

            return PlayerBasicInfo(
                usr_acc.decode('utf-8'), uid, ussid, p_acc.decode('utf-8'), o_acc.decode('utf-8'), reg_dt)
    except:
        issue = 'Get basic info by ssid error =>\n'
        logger.exception(issue)
        return PlayerBasicInfo()


def get_daily_info(check_dt: str, check_interval: int, uid: int) -> dict:

    stmt = 'SELECT DATE_FORMAT(date, \'%Y-%m-%d\'), SUM(bets), SUM(rounds), SUM(wins) '
    stmt += 'FROM dataWarehouse.player_game_by_day '
    stmt += f'WHERE uid = {uid} AND date >= DATE_SUB(\'{check_dt}\', INTERVAL {check_interval} DAY) AND date < \'{check_dt}\' '
    stmt += 'GROUP BY DATE_FORMAT(date, \'%Y-%m-%d\') '

    result = dict()
    try:
        with connections['maria_read'].cursor() as cursor:
            cursor.execute(stmt)
            for (dt, bets, rounds, wins) in list(cursor):
                dt_info = result.setdefault(dt, {})
                dt_info['bets'] = float(bets)
                dt_info['rounds'] = float(rounds)
                dt_info['wins'] = float(wins)
        return result
    except:
        issue = 'Get daily info error =>\n'
        logger.exception(issue)
        return result

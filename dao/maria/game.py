import logging
from collections import OrderedDict
from datetime import datetime
import json

from django.db import connections

logger = logging.getLogger(__name__)


def get_basic_info_by_type(check_dt: str, check_interval: int, game_type: str) -> str:

    stmt = 'SELECT DATE_FORMAT(ug.date, \'%Y-%m-%d\'), ul.userid, ul.account, plo.account, '
    stmt += '(CASE WHEN SUM(ug.total_bet) >= 100000 THEN \'A\' ELSE \'B\' END) lvl '
    stmt += 'FROM cypress.statistic_user_by_game ug '
    stmt += 'JOIN cypress.user_list ul ON ug.uid = ul.id '
    stmt += 'JOIN cypress.parent_list plo ON ul.ownerid=plo.id '
    stmt += f'WHERE ug.date >= DATE_SUB(\'{check_dt}\', INTERVAL {check_interval} DAY) AND ug.date < \'{check_dt}\' '
    stmt += 'GROUP BY DATE_FORMAT(ug.date, \'%Y-%m-%d\'), ug.uid '
    stmt += 'HAVING SUM(ug.total_bet) >= 10000 '
    stmt += 'ORDER BY lvl '

    results = dict()
    try:
        with connections['maria_read'].cursor() as cursor:
            cursor.execute(stmt)
            for (dt, usr_ssid, usr_acc, o_acc, lvl) in list(cursor):
                results.setdefault(dt, {}).setdefault(lvl, []).append(
                    {'name': usr_acc.decode('utf-8'),
                     'owner': o_acc.decode('utf-8'),
                     'ssid': usr_ssid})
        return json.dumps(
            OrderedDict(sorted(results.items(), key=lambda d: datetime.strptime(d[0], '%Y-%m-%d'), reverse=True))
        )
    except:
        issue = 'Get risk player error =>\n'
        logger.exception(issue)
        return json.dumps(results)

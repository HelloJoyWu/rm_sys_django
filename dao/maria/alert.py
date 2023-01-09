import logging
from typing import Callable, Union, Optional
from decimal import Decimal

from django.db import connections

logger = logging.getLogger(__name__)


def get_recent_order_alert(
        recent_range: int = 24 * 7
) -> list:
    """
    Get recent 7 days order alert.
    """

    stmt = 'SELECT DATE_FORMAT(hwoa.alertTime, \'%Y-%m-%d %H:%i:00\'), hwoa.alertLevel, '
    stmt += 'hwoa.owner, hwoa.parent, hwoa.account, gi.game_name_tw, hwoa.gameCode, gi.game_type, '
    stmt += 'hwoa.roundID, hwoa.bet, hwoa.win, hwoa.multipleWin '
    stmt += 'FROM alert.HighWinOrderAlert hwoa '
    stmt += 'JOIN MaReport.game_info gi ON hwoa.gameCode = gi.game_code '
    # stmt += f'WHERE hwoa.alertTime BETWEEN \'2020-09-10\' AND \'2020-09-17\' '
    stmt += f'WHERE hwoa.alertTime BETWEEN DATE_FORMAT(DATE_SUB(NOW(), INTERVAL {recent_range} HOUR), \'%Y-%m-%d %H:%i:00\') AND NOW() '
    stmt += 'ORDER BY hwoa.alertTime DESC '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)

        _res = list(cursor)
        if _res:
            alerts = [{
                'alert_time': info[0], 'alert_level': info[1], 'owner': info[2], 'parent': info[3], 'account': info[4],
                'game_name': info[5], 'game_code': info[6], 'game_type': info[7], 'round_id': info[8],
                'bet': info[9], 'win': info[10], 'win_multiplier': info[11],
            } for info in _res]
        else:
            alerts = []

        return alerts

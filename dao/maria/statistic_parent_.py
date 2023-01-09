import logging
from typing import Callable, Union, Optional
from decimal import Decimal

from django.db import connections

logger = logging.getLogger(__name__)


def get_playing_parents_by_game(
        game_code: str, game_type: str, recent_range: int = 24
) -> list:
    """
    Get playing parents!
    """

    stmt = 'SELECT DISTINCT pg.pid '
    if game_type in ('slot', 'fish', 'arcade'):
        stmt += 'FROM cypress.statistic_parent_by_game pg '
    elif game_type in ('table', 'live'):
        stmt += 'FROM cypress.statistic_parent_by_tablegame pg '
    else:
        stmt += 'FROM cypress.statistic_parent_by_lottogame pg '

    stmt += 'JOIN MaReport.report_parent_list rpl ON pg.pid = rpl.pid '
    stmt += f'JOIN MaReport.game_info gi ON pg.gid = gi.gid AND gi.game_code = \'{game_code}\' '
    stmt += f'WHERE pg.date BETWEEN DATE_FORMAT(DATE_SUB(NOW(), INTERVAL {recent_range} HOUR), \'%Y-%m-%d %H:00:00\') '
    stmt += f'   AND NOW() '

    with connections['maria_read'].cursor() as cursor:
        cursor.execute(stmt)
        logger.info(f'Get playing game({game_code}) parents in recent {recent_range} hour SUCCESS!')

        _res = [i[0] for i in cursor.fetchall() if i]

        return _res

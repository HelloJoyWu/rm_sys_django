import logging
from datetime import datetime
from collections import Counter

from dao.trigger import mongo_read_trigger

logger = logging.getLogger(__name__)


@mongo_read_trigger
def get_user_daily_free_spin_count(
        start_date: datetime, end_date: datetime, user_ssid: str, **kwargs
) -> dict:

    finds = {
        'startTime': {'$gte': start_date,
                      '$lt': end_date},
        'playerID': user_ssid
        }
    projections = {
        '_id': 0,
        'startTime': 1,
        'fTimes': 1
    }

    daily_counter = Counter()
    try:
        mongo_cnx = kwargs['mongo_cnx']
        result = list(mongo_cnx.analysis.gameDetail.find(finds, projections))
        if result is not list():
            for info in result:
                daily_counter[info['startTime'].strftime('%Y-%m-%d')] += int(info['fTimes'])
    except Exception:
        logger.exception('Get user daily free spin count FAILED!')

    return dict(daily_counter)


@mongo_read_trigger
def get_player_game_detail(
        start_date: datetime, end_date: datetime, user_ssid: str, **kwargs
) -> list:
    """
    Get player arcade and slot games' detail
    """

    finds = {
        'startTime': {'$gte': start_date,
                      '$lt': end_date},
        'playerID': user_ssid
    }
    projections = {
        '_id': 0,
        'startTime': 1,
        'gameCode': 1,
        'featureInfos': 1,
        'betInfos': 1,
        'multipleWinInfos': 1,
        'multipleWinStats': 1,
    }

    mongo_cnx = kwargs['mongo_cnx']
    result = list(mongo_cnx.analysis.gameDetail.find(finds, projections))

    return result

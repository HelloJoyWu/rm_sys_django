from django.test import TestCase, SimpleTestCase
from django.test.runner import DiscoverRunner
import logging
from datetime import datetime, timedelta
import pytz

from rmsys import util

from dao.maria import user
from dao.mongo import gamedetail

logger = logging.getLogger(__name__)


class UserTest(SimpleTestCase):
    """
    run in terminal:
        python manage.py test tests.test_dao.UserTest --testrunner=tests.test_dao.NoDbTestRunner
    """
    databases = {'maria_read', }

    def setUp(self) -> None:
        self.to_dt = datetime.utcnow()
        self.from_dt = self.to_dt - timedelta(days=1)
        pass

    def tearDown(self) -> None:
        pass

    def test_connections(self):
        from django.db import connections
        with connections['maria_read'].cursor() as cursor:
            cursor.execute('SELECT * FROM cypress.game_list;')
            result = list(cursor)
            logger.info(result[:10])
            cursor.execute('SELECT @@session.time_zone;')
            logger.info(cursor.fetchall())

    def test_get_daily_info(self):
        user_ssid = '60f805153834690001785aab'
        user_basic_info = user.get_basic_info_by_ssid(user_ssid)
        check_dt = util.get_datawarehouse_latest_date()
        check_interval = 7
        user_daily = user.get_daily_info(check_dt.strftime('%Y-%m-%d'), check_interval, user_basic_info.user_id)
        logger.debug('--- user daily info ---')
        logger.debug(user_daily)
        logger.debug('------')

    def test_get_basic_info_by_ssid(self):

        user_ssid = '60eef70e16001700010467e4'
        user_basic_info = user.get_basic_info_by_ssid(user_ssid)
        logger.debug('--- user basic info ---')
        logger.debug(user_basic_info)
        logger.debug('------')
        self.assertEqual(user_basic_info.user_ssid, user_ssid)

    def test_get_risks(self):

        check_dt = util.get_datawarehouse_latest_date()
        check_interval = 7
        query_result = user.get_risk_players(check_dt.strftime('%Y-%m-%d'), check_interval)

        logger.debug(query_result.keys())
        logger.debug(query_result)
        # a = json.dumps(
        #     OrderedDict(
        #         sorted(query_result.items(), key=lambda d: datetime.strptime(d[0], '%Y-%m-%d'), reverse=True)
        #     ))
        # b = ','.join([json.dumps(dict([d])) for d in sorted(query_result.items(), key=lambda d: datetime.strptime(d[0], '%Y-%m-%d'), reverse=True)])

        self.assertIsNotNone(query_result)
        # self.assertEqual(a, b)


class GamedetailTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_dao.GamedetailTest --testrunner=tests.test_dao.NoDbTestRunner
    """

    def setUp(self) -> None:
        self.to_dt = (datetime.utcnow()).replace(tzinfo=pytz.UTC)
        self.from_dt = self.to_dt - timedelta(days=1)
        pass

    def tearDown(self) -> None:
        pass

    def test_get_user_daily_free_spin_count(self):
        user_ssid = '60f805153834690001785aab'
        check_dt = util.get_datawarehouse_latest_date()
        check_interval = 7
        ft_dict = gamedetail.get_user_daily_free_spin_count(
            check_dt - timedelta(days=check_interval), check_dt, user_ssid)
        logger.debug('--- user free-spin count ---')
        logger.debug(ft_dict)
        logger.debug('------')


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion """

    def setup_databases(self, **kwargs):
        # from django.conf import settings
        # connections = {'default': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME': settings.BASE_DIR / 'test_db.sqlite3',
        # }}
        # super().setup_databases(aliases=connections)
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass

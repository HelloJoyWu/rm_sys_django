from django.test import TestCase, RequestFactory

from risk.models import PowerBIReport, PowerBIRSL
from django.urls import reverse
from django.contrib.auth.models import User, Group  # Required to assign User as a borrower

from risk.views import SlotAlert

import logging

logger = logging.getLogger(__name__)


class RiskAlertTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_views.RiskAlertTest
    """

    def setUp(self) -> None:

        # create user
        group = Group(name='DA')
        group.save()
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user1.groups.add(group)
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('slot_alert'))
        logger.info(resp)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/accounts/login?next=/risk/slot_alert')
        # self.assertRedirects(resp, '/accounts/login?next=/risk/risk_alert')

    def test_forbidden_if_logged_in_with_wrong_group(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('risk_alert'))
        logger.info(resp)
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('risk_alert'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'slot_alert.html')

    def test_get_queryset(self):
        request = RequestFactory().get('/risk_alert')
        view = SlotAlert()
        view.request = request
        qs = view.get_queryset()
        logger.info(qs)


class GetEmbedInfoTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_views.GetEmbedInfoTest
    """

    def setUp(self) -> None:

        # create user
        group = Group(name='DA')
        group.save()
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user1.groups.add(group)
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # create report
        PowerBIReport.objects.create(
            report_id='6265c101-ffaf-44b1-87ad-913cefde3081',
            group_id='f4f018e7-a20f-401f-a9c5-2a90f328d2e5',
            report_name='players_30day_info',
            api_client_id='7e80ddc8-7454-417a-9cd4-8df029654d4d',
            api_secrete='2i6A~76LLG.9V-bc6XOk-4n2V-n-b6b.cJ')

        # create identities
        PowerBIRSL.objects.create(
            role_name='bbin',
            user_name='bbin@mtopv1.onmicrosoft.com',
            dataset_id='ee58832f-33cd-4150-850b-4488fbf05830')

    def test_get_embed_pbi_report_info_for_certain_owner(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(
            '/risk/getembedinfo',
            {
                'owner': 'bbin',
                'report_name': 'players_30day_info'
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        )

        logger.info('---response---')
        logger.info(resp)
        logger.info('------')

        # self.assertEqual(str(resp.context['user']), 'testuser1')
        self.assertEqual(resp.status_code, 200)

    def test_get_embed_pbi_report_info_for_all(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(
            '/risk/getembedinfo',
            {
                'owner': 'asiaweinet',
                'report_name': 'players_30day_info'
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        )

        logger.info('---response---')
        logger.info(resp)
        logger.info('------')

        # self.assertEqual(str(resp.context['user']), 'testuser1')
        self.assertEqual(resp.status_code, 200)

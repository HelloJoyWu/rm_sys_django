from django.test import TestCase
from risk.models import PowerBIReport

import logging

logger = logging.getLogger(__name__)


class PowerBIReportTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_models.PowerBIReportTest
    """

    def setUp(self) -> None:
        PowerBIReport.objects.create(
            report_id='6265c101-ffaf-44b1-87ad-913cefde3081',
            group_id='f4f018e7-a20f-401f-a9c5-2a90f328d2e5',
            report_name='players_30day_info',
            api_client_id='7e80ddc8-7454-417a-9cd4-8df029654d4d',
            api_secrete='2i6A~76LLG.9V-bc6XOk-4n2V-n-b6b.cJ')

    def tearDown(self) -> None:
        pass

    def test_object_name(self):
        pbi_report = PowerBIReport.objects.get(id=1)
        expected_object_name = '%s' % (pbi_report.report_name, )
        logger.info(PowerBIReport.objects.all())
        self.assertEquals(expected_object_name, str(pbi_report))

    def test_report_name_label(self):
        pbi_report = PowerBIReport.objects.get(id=1)
        field_label = pbi_report._meta.get_field('report_name').verbose_name
        self.assertEquals(field_label, 'report name')

    def test_not_get_object(self):
        from django.shortcuts import get_object_or_404
        # The following will raise an Http404 error
        no_pbi_report = get_object_or_404(PowerBIReport, id=10)

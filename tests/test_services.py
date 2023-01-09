from django.test import TestCase
from risk.models import PBIEmbedTokenRequestBody
from risk.services import AadService, PbiEmbedService

import requests
import logging
import json

logger = logging.getLogger(__name__)


class AadServiceTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_services.AadServiceTest
    """

    def setUp(self) -> None:
        self.client_id = '7e80ddc8-7454-417a-9cd4-8df029654d4d'
        self.client_secrete = '2i6A~76LLG.9V-bc6XOk-4n2V-n-b6b.cJ'

    def tearDown(self) -> None:
        pass

    def test_get_account(self):
        response = AadService.get_access_token(self.client_id, self.client_secrete)
        print('---response---')
        print(response)
        self.assertIsNotNone(response)

    def test_cache(self):
        pass


class PbiEmbedServiceTest(TestCase):
    """
    run in terminal:
        python manage.py test tests.test_services.PbiEmbedServiceTest
    """

    def setUp(self) -> None:
        client_id = '7e80ddc8-7454-417a-9cd4-8df029654d4d'
        client_secrete = '2i6A~76LLG.9V-bc6XOk-4n2V-n-b6b.cJ'
        self.access_token = AadService.get_access_token(client_id, client_secrete)
        self.pbi_embed_service = PbiEmbedService(self.access_token)
        # 玩家30天概況-RSL
        self.report_id = '6265c101-ffaf-44b1-87ad-913cefde3081'
        self.group_id = 'f4f018e7-a20f-401f-a9c5-2a90f328d2e5'

    def tearDown(self) -> None:
        self.pbi_embed_service = None

    def test_get_non_rsl_report_embed_token(self):
        embed_info, status = self.pbi_embed_service.get_embed_params_for_single_report(self.group_id, self.report_id)
        self.assertIsNotNone(embed_info)
        self.assertEqual(status, 200)

    def test_get_rsl_report_embed_token(self):
        identity = {
            'username': 'risk_sys@mtopv1.onmicrosoft.com',
            'roles': ['ALL'],
            'datasets': ['ee58832f-33cd-4150-850b-4488fbf05830']
        }
        embed_info, status = self.pbi_embed_service.get_embed_params_for_single_report_with_identity(
            self.group_id, self.report_id, identity=identity)
        self.assertIsNotNone(embed_info)
        self.assertEqual(status, 200)

    def test_get_report_embed_url_from_rsl_test_report(self):
        # static RSL_test
        # group_id = 'af5fe79a-e719-40e9-804f-7d08a4bfb3e7'  # workspace_id
        # report_id = '996681e0-c9fc-4207-b0bd-fbb7008f7938'
        group_id = self.group_id
        report_id = self.report_id

        report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}'
        api_response = requests.get(report_url, headers=self.pbi_embed_service.get_request_header())

        status_code = api_response.status_code
        if api_response.status_code != 200:
            logger.error('Failed while getting embedUrl')
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
        else:
            api_response = json.loads(api_response.text)
            logger.debug('---report embed url---')
            logger.debug(api_response)
            logger.debug('---report embed url---')

        self.assertEqual(status_code, 200)

    def test_get_rsl_embed_token_from_rsl_test_report(self):
        """
        python manage.py test
            risk.tests.test_services.PbiEmbedServiceTest.test_get_rsl_embed_token_from_rsl_test_report
        """

        group_id = 'af5fe79a-e719-40e9-804f-7d08a4bfb3e7'  # workspace_id
        report_id = '996681e0-c9fc-4207-b0bd-fbb7008f7938'
        dataset_id = 'e2042edc-8de2-42ab-a756-f8610833638a'

        request_body = PBIEmbedTokenRequestBody()

        request_body.datasets.append({'id': dataset_id})

        request_body.reports.append({'id': report_id})

        request_body.targetWorkspaces.append({'id': group_id})

        request_body.identities.append(
            {
                'username': 'bbin@mtopv1.onmicrosoft.com',
                'roles': ['bbin'],
                'datasets': [dataset_id]
            })

        # Generate Embed token for multiple workspaces, datasets, and reports.
        # Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.pbi_embed_service.get_request_header())

        status_code = api_response.status_code
        if api_response.status_code != 200:
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
        else:
            api_response = json.loads(api_response.text)
            logger.debug('---report embed_token---')
            logger.debug(api_response)
            logger.debug('---report embed_token---')

        self.assertEqual(status_code, 200)

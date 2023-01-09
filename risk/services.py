from .models import \
    PBIReportConfig, PBIEmbedToken, PBIEmbedConfig, PBIEmbedTokenRequestBody

import requests
import json
import msal
import logging
from typing import Optional, Tuple, Dict, Union

logger = logging.getLogger(__name__)


class AadService:

    # TODO: saving clientapp cache with the suggestion on the following website
    # https://stackoverflow.com/questions/60008677/how-should-i-be-implementing-user-sso-with-aad-in-a-django-application-using-th

    @staticmethod
    def get_access_token(client_id, client_secrete) -> str:
        """
        Generates and returns Access token. Only one scope(or permission) can be accessed at a time.
        Remember to grant permission by admin with AAD.
        1. PublicClientApplication: Get token by username and password. The type of permission for API
        should be "delegate".
        2. ConfidentialClientApplication: Get token with client secret.
        Both are just different way to get token. They all get powerBI report as an API.
        :return: Access token
        """
        # from django.conf import settings
        # aad_cfg = settings.AAD_SET

        # response = None
        # if aad_cfg['AUTHENTICATION_MODE'].lower() == 'masteruser':
        #
        #     # Create a public client to authorize the app with the AAD app
        #     clientapp = msal.PublicClientApplication(
        #         client_id=aad_cfg['CLIENT_ID'],
        #         authority=aad_cfg['AUTHORITY'])
        #
        #     accounts = clientapp.get_accounts(username=aad_cfg['POWER_BI_USER'])
        #
        #     if accounts:
        #         # Retrieve Access token from user cache if available
        #         response = clientapp.acquire_token_silent(aad_cfg['SCOPE'], account=accounts[0])
        #
        #     if not response:
        #         # Make a client call if Access token is not available in cache
        #         response = clientapp.acquire_token_by_username_password(
        #             username=aad_cfg['POWER_BI_USER'],
        #             password=aad_cfg['POWER_BI_PASS'],
        #             scopes=aad_cfg['SCOPE'])

        # Service Principal auth is the recommended by Microsoft to achieve App Owns Data Power BI embedding
        # elif aad_cfg['AUTHENTICATION_MODE'].lower() == 'serviceprincipal':
        # authority = aad_cfg['AUTHORITY'].replace('organizations', aad_cfg['TENANT_ID'])
        authority = 'https://login.windows.net/mtopv1.onmicrosoft.com'
        clientapp = msal.ConfidentialClientApplication(
            client_id, client_credential=client_secrete, authority=authority)

        # Make a client call if Access token is not available in cache
        response = clientapp.acquire_token_for_client(scopes=['https://analysis.windows.net/powerbi/api/.default'])

        try:
            return response['access_token']
        except KeyError:
            raise Exception('Failed get access token: ' + response['error_description'])


class PbiEmbedService:

    ACCESS_TOKEN: str

    def __init__(self, access_token):
        self.ACCESS_TOKEN = access_token

    def get_embed_params_for_single_report(
            self, workspace_id: str, report_id: str, additional_dataset_id: [str, Optional] = None
    ) -> Tuple[Dict, int]:
        """
        Get embed params for a report and a workspace
        :param workspace_id: Workspace Id
        :param report_id: Report Id
        :param additional_dataset_id: (str, optional) Dataset Id different than the one bound to the report.
            Defaults to None.
        :return: (EmbedConfig: Embed token and Embed URL, status code)
        """

        report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'
        api_response = requests.get(report_url, headers=self.get_request_header())

        if api_response.status_code != 200:
            logger.error('Failed get_embed_params_for_single_report while getting embedUrl')
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
            return err_dict, api_response.status_code

        api_response = json.loads(api_response.text)
        report = PBIReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
        dataset_ids = [api_response['datasetId']]

        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_id is not None:
            dataset_ids.append(additional_dataset_id)

        embed_token, status_code = self.get_embed_token_for_single_report_single_workspace(
            report_id, dataset_ids, workspace_id)

        if status_code != 200:
            logger.error('Failed get_embed_token_for_single_report_single_workspace')
            return embed_token, status_code
        else:
            embed_config = PBIEmbedConfig(
                embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])
            return embed_config.__dict__, 200

    def get_embed_params_for_single_report_with_identity(
            self, workspace_id: str, report_id: str, additional_dataset_id: [str, Optional] = None,
            identity: Dict = None
    ) -> Tuple[Dict, int]:
        """
        Get embed params for a report and a workspace
        :param workspace_id: Workspace Id
        :param report_id: Report Id
        :param additional_dataset_id: (str, optional) Dataset Id different than the one bound to the report.
            Defaults to None.
        :param identity: RSL report identity
        :return: (EmbedConfig: Embed token and Embed URL, status code)
        """

        report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'
        api_response = requests.get(report_url, headers=self.get_request_header())

        if api_response.status_code != 200:
            logger.error('Failed get_embed_params_for_single_report while getting embedUrl')
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
            return err_dict, api_response.status_code

        api_response = json.loads(api_response.text)
        report = PBIReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
        dataset_ids = [api_response['datasetId']]

        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_id is not None:
            dataset_ids.append(additional_dataset_id)

        embed_token, status_code = self.get_embed_token_for_single_report_single_workspace(
            report_id, dataset_ids, workspace_id, identity)

        if status_code != 200:
            logger.error('Failed get_embed_token_for_single_report_single_workspace')
            return embed_token, status_code
        else:
            embed_config = PBIEmbedConfig(
                embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])
            return embed_config.__dict__, 200

    def get_embed_token_for_single_report_single_workspace(
            self, report_id: str, dataset_ids: list, target_workspace_id: [str, Optional] = None, identity: Dict = None
    ) -> Tuple[Union[Dict, PBIEmbedToken], int]:
        """
        Get Embed token for single report, multiple datasets, and an optional target workspace
        :param report_id: Report Id
        :param dataset_ids:
        :param target_workspace_id:
        :param identity: RSL report identity
        :return: (EmbedToken: Embed token, status code)
        """

        request_body = PBIEmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        request_body.reports.append({'id': report_id})

        if target_workspace_id is not None:
            request_body.targetWorkspaces.append({'id': target_workspace_id})

        if identity is not None:
            request_body.identities.append(identity)

        # Generate Embed token for multiple workspaces, datasets, and reports.
        # Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header())

        if api_response.status_code != 200:
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
            return err_dict, api_response.status_code

        api_response = json.loads(api_response.text)
        embed_token = PBIEmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token, 200

    def get_embed_params_for_multiple_reports(
            self, workspace_id: str, report_ids: list, additional_dataset_ids: [list, Optional] = None
    ) -> Tuple[Dict, int]:
        """
        Get embed params for a report and a workspace
        :param workspace_id: Workspace Id
        :param report_ids: Report Ids
        :param additional_dataset_ids: Dataset Ids which are different than the ones bound to the reports.
            Defaults to None.
        :return: (EmbedConfig: Embed token and Embed URLs, status code)
        """

        # Note: This method is an example and is not consumed in this sample app

        dataset_ids = []

        # To store multiple report info
        reports = []

        for report_id in report_ids:
            report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'
            api_response = requests.get(report_url, headers=self.get_request_header())

            if api_response.status_code != 200:
                err_dict = {
                    'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                                f'{api_response.reason}:\t{api_response.text}\n' +
                                f'RequestId:\t{api_response.headers.get("RequestId")}'}
                logger.error(err_dict.get('errorMsg'))
                return err_dict, api_response.status_code

            api_response = json.loads(api_response.text)
            report_config = PBIReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
            reports.append(report_config.__dict__)
            dataset_ids.append(api_response['datasetId'])

        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_ids is not None:
            dataset_ids.extend(additional_dataset_ids)

        embed_token, status_code = self.get_embed_token_for_multiple_reports_single_workspace(
            report_ids, dataset_ids, workspace_id)

        if status_code != 200:
            logger.error('Failed get_embed_token_for_multiple_reports_single_workspace')
            return embed_token, status_code
        else:
            embed_config = PBIEmbedConfig(
                embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, reports)
            return embed_config.__dict__, 200

    def get_embed_token_for_multiple_reports_single_workspace(
            self, report_ids: list, dataset_ids: list, target_workspace_id: [str, Optional] = None
    ) -> Tuple[Union[Dict, PBIEmbedToken], int]:
        """
        Get Embed token for multiple reports, multiple dataset, and an optional target workspace.
        :param report_ids: Report Ids
        :param dataset_ids: Report Ids
        :param target_workspace_id: Workspace Id. Defaults to None.
        :return: (EmbedToken: Embed token, status code)
        """

        # Note: This method is an example and is not consumed in this sample app

        request_body = PBIEmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        for report_id in report_ids:
            request_body.reports.append({'id': report_id})

        if target_workspace_id is not None:
            request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Generate Embed token for multiple workspaces, datasets, and reports.
        # Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header())

        if api_response.status_code != 200:
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
            return err_dict, api_response.status_code

        api_response = json.loads(api_response.text)
        embed_token = PBIEmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token, 200

    def get_embed_token_for_multiple_reports_multiple_workspaces(
            self, report_ids: list, dataset_ids: list, target_workspace_ids: [list, Optional] = None
    ) -> Tuple[Union[Dict, PBIEmbedToken], int]:
        """
        Get Embed token for multiple reports, multiple datasets, and optional target workspaces
        :param report_ids: Report Ids
        :param dataset_ids: Dataset Ids
        :param target_workspace_ids: Workspace Ids. Defaults to None.
        :return: (Embed token, status code)
        """

        # Note: This method is an example and is not consumed in this sample app

        request_body = PBIEmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        for report_id in report_ids:
            request_body.reports.append({'id': report_id})

        if target_workspace_ids is not None:
            for target_workspace_id in target_workspace_ids:
                request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Generate Embed token for multiple workspaces, datasets, and reports.
        # Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header())

        if api_response.status_code != 200:
            err_dict = {
                'errorMsg': f'Error {api_response.status_code} while retrieving Embed URL\n' +
                            f'{api_response.reason}:\t{api_response.text}\n' +
                            f'RequestId:\t{api_response.headers.get("RequestId")}'}
            logger.error(err_dict.get('errorMsg'))
            return err_dict, api_response.status_code

        api_response = json.loads(api_response.text)
        embed_token = PBIEmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token, 200

    def get_request_header(self):
        """
        Get Power BI API request header
        :return: Request header
        """

        return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.ACCESS_TOKEN}

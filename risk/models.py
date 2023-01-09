from django.db import models
from django.contrib.auth.models import User

from typing import Optional, Tuple, Dict, Union, List
# Create your models here.


class Model(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class PowerBIReport(Model):
    report_id = models.CharField(help_text='Power BI report\'s id', max_length=50)
    group_id = models.CharField(help_text='Power BI report\'s group id(or workspace id)', max_length=50)
    report_name = models.CharField(help_text='report name which is received from embed request', max_length=30)
    api_client_id = models.CharField(help_text='Azure API client id', max_length=50)
    api_secrete = models.CharField(help_text='Azure API client secrete', max_length=50)

    def __str__(self):
        """
        String for representing the MyModelName object (in Admin site etc.).
        """
        return self.report_name


class PowerBIRSL(Model):
    role_name = models.CharField(help_text='RSL role name', max_length=30)
    user_name = models.EmailField(help_text='RSL user name(Azure email account)')
    dataset_id = models.CharField(help_text='Azure user\'s dataset id', max_length=50)

    def __str__(self):
        return self.role_name


class RiskAlertInfo:
    date: str
    sums: int
    players: list

    def __init__(self, date: str, sums: int, players):
        self.date = date
        self.sums = sums
        self.players = players


class PlayerBasicInfo:
    user_name: str
    user_id: int
    user_ssid: str
    parent_name: str
    owner_name: str
    reg_date: str

    def __init__(
            self, user_name: str = '', user_id: int = 0, user_ssid: str = '',
            parent_name: str = '', owner_name: str = '', reg_date: str = '1970-01-01'):
        self.user_name = user_name
        self.user_id = user_id
        self.user_ssid = user_ssid
        self.parent_name = parent_name
        self.owner_name = owner_name
        self.reg_date = reg_date


class PBIEmbedToken:
    # Camel casing is used for the member variables as they are going to be serialized
    # and camel case is standard for JSON keys

    tokenId = None
    token = None
    tokenExpiry = None

    def __init__(self, token_id, token, token_expiry):
        self.tokenId = token_id
        self.token = token
        self.tokenExpiry = token_expiry


class PBIReportConfig:
    # Camel casing is used for the member variables as they are going to be serialized
    # and camel case is standard for JSON keys

    reportId = None
    reportName = None
    embedUrl = None
    datasetId = None

    def __init__(self, report_id, report_name, embed_url, dataset_id = None):
        self.reportId = report_id
        self.reportName = report_name
        self.embedUrl = embed_url
        self.datasetId = dataset_id


class PBIEmbedConfig:
    # Camel casing is used for the member variables as they are going to be serialized
    # and camel case is standard for JSON keys

    tokenId = None
    accessToken = None
    tokenExpiry = None
    reportConfig = None

    def __init__(self, token_id, access_token, token_expiry, report_config):
        self.tokenId = token_id
        self.accessToken = access_token
        self.tokenExpiry = token_expiry
        self.reportConfig = report_config


class PBIEmbedTokenRequestBody:
    # Camel casing is used for the member variables as they are going to be serialized
    # and camel case is standard for JSON keys

    datasets: Union[List[Dict], None] = None
    reports: Union[List[Dict], None] = None
    targetWorkspaces: Union[List[Dict], None] = None
    identities: Union[List[Dict], None] = None

    def __init__(self):
        self.datasets = []
        self.reports = []
        self.targetWorkspaces = []
        self.identities = []

from risk.services import PbiEmbedService, AadService
from risk.models import PowerBIReport, PowerBIRSL
from dao.maria import user
from dao.mongo import gamedetail
from rmsys import util

from datetime import datetime, timedelta
import logging
import json
from collections import OrderedDict

from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Create your views here.


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/login'


class AgentAlert(LoginRequiredMixin, TemplateView):
    template_name = 'agent_alert.html'
    login_url = '/login'


class ThirtyDayInfo(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = '30d_risks_info.html'
    login_url = '/login'
    # 30d_risks_info/{{ user.groups.first }} for default?

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class TableAlert(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'table_alert.html'
    login_url = '/login'

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class FishAlert(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'fish_alert.html'
    login_url = '/login'

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class ArcadeAlert(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'arcade_alert.html'
    login_url = '/login'

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class SportAlert(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'sport_alert.html'
    login_url = '/login'

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class LiveAlert(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'live_alert.html'
    login_url = '/login'

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class SlotRiskPlayer(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'slot_risk_player.html'
    login_url = '/login'
    date_limit = 7

    def get_context_data(self, **kwargs):
        """
        Inherit from View. Add the html context manually like add dict in context.
        :return:
        """
        context = super().get_context_data(**kwargs)
        user_ssid = context['userssid']
        check_dt = util.get_datawarehouse_latest_date()
        context['user_info'] = cache.get_or_set(
            'SRP_' + user_ssid,
            user.get_basic_info_by_ssid(user_ssid),
            24 * 60 * 60
        )
        context['user_daily'] = cache.get_or_set(
            'SRP_' + check_dt.strftime('%Y%m%d_') + user_ssid,
            self.get_user_daily_info(check_dt, context['user_info']),
            60 * 60
        )

        return context

    def get_user_daily_info(self, check_dt, user_info) -> str:

        user_daily = OrderedDict()
        for i in range(self.date_limit):
            user_daily[(check_dt - timedelta(days=i+1)).strftime('%Y-%m-%d')] = {
                'bets': 0,
                'rounds': 0,
                'wins': 0,
                'frees': 0
            }
        user_daily_info = user.get_daily_info(check_dt.strftime('%Y-%m-%d'), self.date_limit, user_info.user_id)
        user_daily_ft = gamedetail.get_user_daily_free_spin_count(
            check_dt - timedelta(days=self.date_limit), check_dt, user_info.user_ssid)

        for dt in user_daily.keys():
            user_daily[dt]['bets'] += user_daily_info.get(dt, {}).get('bets', 0)
            user_daily[dt]['rounds'] += user_daily_info.get(dt, {}).get('rounds', 0)
            user_daily[dt]['wins'] += user_daily_info.get(dt, {}).get('wins', 0)
            user_daily[dt]['frees'] += user_daily_ft.get(dt, 0)

        return json.dumps(user_daily)

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()


class SlotAlert(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'slot_alert.html'
    login_url = '/login'
    # ListView would pass queryset to context; use context_object_name in html to show context
    context_object_name = 'risk_dates'
    # queryset = test_query_set()
    date_limit = 7
    check_dt: datetime

    def test_func(self):
        return self.request.user.groups.filter(name='DA').exists()

    def get_queryset(self):
        """
        Using the to dynamically return query result by the kwargs in url
        Ref: https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-display/
        :return:
        """
        self.check_dt = util.get_datawarehouse_latest_date()

        return list(
            map(lambda i, j: (self.check_dt - (i+1)*j).strftime('%Y-%m-%d'),
                range(self.date_limit), (timedelta(days=1),) * self.date_limit)
        )

    def get_context_data(self, **kwargs):
        """
        Inherit from View. Add the html context manually like add dict in context.
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['risk_info'] = cache.get_or_set(
            'SA_' + self.check_dt.strftime('%Y-%m-%d'),
            user.get_risk_players(self.check_dt.strftime('%Y-%m-%d'), self.date_limit),
            12 * 60 * 60
        )
        context['check_risks_dt'] = (self.check_dt - timedelta(days=1)).strftime('%Y-%m-%d')
        return context


class GetEmbedInfo(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):

        owner_name = self.request.GET.get('owner')
        report_name = self.request.GET.get('report_name')
        logger.info('---getembedinfo request data---')
        logger.info(owner_name)
        logger.info(report_name)
        logger.info('------')

        if request.is_ajax and request.method == 'GET':
            logger.debug(request.session)

            try:
                pbi_report = PowerBIReport.objects.get(report_name=report_name)

                access_token = cache.get_or_set(
                    'GEI_' + pbi_report.api_client_id + '_' + pbi_report.api_secrete,
                    AadService.get_access_token(pbi_report.api_client_id, pbi_report.api_secrete),
                    30 * 60
                )
                pbi_embed_service = PbiEmbedService(access_token)

                try:
                    id_info = PowerBIRSL.objects.get(role_name=owner_name)
                    identity = {
                        'username': id_info.user_name,
                        'roles': [id_info.role_name],
                        'datasets': [id_info.dataset_id]
                    }
                except Exception as e:
                    logger.warning(f'The owner {owner_name} is not in PowerBIRSL retrun all.')
                    identity = {
                        'username': 'risk_sys@mtopv1.onmicrosoft.com',
                        'roles': ['ALL'],
                        'datasets': ['ee58832f-33cd-4150-850b-4488fbf05830']
                    }

                embed_info, status = pbi_embed_service.get_embed_params_for_single_report_with_identity(
                    pbi_report.group_id, pbi_report.report_id, identity=identity)

                return JsonResponse(embed_info, status=status)

            except Exception as e:
                return JsonResponse({'errorMsg': str(e)}, status=500)

        return JsonResponse({"errorMsg": "Unknown Error"}, status=400)

    def test_func(self):
        # TODO: set this for powerBI read-permission
        return self.request.user.groups.filter(name='DA').exists()

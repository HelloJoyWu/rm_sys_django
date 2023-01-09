from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('getembedinfo', views.GetEmbedInfo.as_view(), name='getembedinfo'),
    path('30d_info/<str:owner>', views.ThirtyDayInfo.as_view(), name='30d_info'),
    path('slot/player/<str:userssid>', views.SlotRiskPlayer.as_view()),
    path('agent', views.AgentAlert.as_view(), name='risk_agent'),
    path('slot', views.SlotAlert.as_view(), name='risk_slot'),
    path('table', views.TableAlert.as_view(), name='risk_table'),
    path('fish', views.FishAlert.as_view(), name='risk_fish'),
    path('arcade', views.ArcadeAlert.as_view(), name='risk_arcade'),
    path('live', views.LiveAlert.as_view(), name='risk_live'),
    path('sport', views.SportAlert.as_view(), name='risk_sport'),
]

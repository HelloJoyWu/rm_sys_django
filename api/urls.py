# Adding django rest framework
from rest_framework import routers, permissions, renderers
from django.urls import path, include

from api import views


class StaffBrowsableAPIMixin(object):
    def get_renderers(self):
        """
        add BrowsableAPIRenderer if user is staff (regular users see JSONRenderer response)
        """
        # explicitly set renderer to JSONRenderer (the default for non staff users)
        rends = [renderers.JSONRenderer]
        if self.request.user.is_staff:
            # staff users see browsable API
            rends.append(renderers.BrowsableAPIRenderer)
        return [renderer() for renderer in rends]


class CustomAPIRootView(StaffBrowsableAPIMixin, routers.APIRootView):
    permission_classes = (permissions.IsAdminUser,)


class CustomDefaultRouter(routers.DefaultRouter):
    APIRootView = CustomAPIRootView


router = CustomDefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('order/alert', views.GetOrderAlert.as_view()),
    path('key/generate', views.GenerateAPIKey.as_view()),
    path('broadcast/risk/online', views.GetBroadcastMessage.as_view()),
    path('getuserlivehedgeinfo', views.GetUserLiveHedgeInfo.as_view()),
    path('getrecentlivehedgeinfo', views.GetRecentLiveHedgeInfo.as_view()),
    path('getusersummarybygame', views.GetUserSummaryByGame.as_view()),
    path('getplayerdetail', views.GetPlayerDetail.as_view()),
    path('getgamestatus', views.GetGameStatus.as_view()),
    path('getusersummarybyrule', views.GetUserSummaryByRule.as_view()),
    path('gethoursummary', views.GetHourSummary.as_view()),
    path('getnewswinstatic', views.GetNewsWinStatic.as_view()),
]
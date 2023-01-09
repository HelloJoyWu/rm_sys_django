from django.urls import re_path

from ws import consumers

websocket_urlpatterns = [
    re_path(r'ws/risk_online/', consumers.RiskOnlineConsumer.as_asgi()),
]
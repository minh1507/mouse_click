"""WebSocket routing configuration for the tracking app."""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tracking/$', consumers.TrackingConsumer.as_asgi()),
] 
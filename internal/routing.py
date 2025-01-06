from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/customer/location/(?P<user_id>\d+)/$', consumers.CustomerLocationConsumer.as_asgi()),
]
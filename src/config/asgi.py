"""
Файл содержит конфигурацию для ASGI-приложения Django.

Он устанавливает переменную окружения DJANGO_SETTINGS_MODULE на 'src.config.patterns.development',
что указывает Django, какие настройки использовать для этого окружения. Затем создает ASGI-приложение
с помощью функции get_asgi_application из django.core.asgi.
"""

import os
from django.core.asgi import get_asgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "src.config.settings"

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from src.modules.crm.realtime.consumers import TaskCommentsConsumer, NotificationsConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # ws://<host>/api/crm/ws/tasks/<task_id>/comments/
            re_path(r"^api/crm/ws/tasks/(?P<task_id>\d+)/comments/$", TaskCommentsConsumer.as_asgi()),
            re_path(r"^api/crm/ws/notifications/(?P<user_id>\d+)$", NotificationsConsumer.as_asgi()),
        ])
    ),
})

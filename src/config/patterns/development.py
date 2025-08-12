"""
Файл содержащий настройки для разработки (development) Django-приложения.

Он импортирует базовые настройки из модуля `local` и добавляет специфические настройки для разработки,
такие как секретный ключ, режим отладки и разрешенные хосты.
"""

from celery.schedules import crontab

from src.config.patterns.local import *
from src.config.env import env

SECRET_KEY = env.str('API_SECRET_KEY')

DEBUG = True

CELERY_BEAT_SCHEDULE = {
    'sync-every-5-minutes': {
        'task': 'src.modules.bi_analysis.tasks.sync_data_from_sources',
        'schedule': crontab(minute='*/5'),
    },
}

ALLOWED_HOSTS = env.list('API_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# --- WebSockets / Django Channels (dev) ---
# аккуратно дополняем INSTALLED_APPS, не перезаписывая
try:
    _apps = list(INSTALLED_APPS)
except NameError:
    _apps = []
if "channels" not in _apps:
    _apps.append("channels")
INSTALLED_APPS = _apps

# путь до ASGI-приложения
ASGI_APPLICATION = "src.config.asgi.application"

# in-memory слой для локалки (на проде лучше Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

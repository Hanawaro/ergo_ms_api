INSTALLED_APPS = [
    'channels',
]

ASGI_APPLICATION = 'src.config.asgi.application'

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
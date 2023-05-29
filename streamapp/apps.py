from django.apps import AppConfig


class StreamappConfig(AppConfig):
    name = 'streamapp'

    def ready(self):
        from streamapp import signals
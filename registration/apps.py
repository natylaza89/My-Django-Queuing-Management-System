from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'registration'

    def ready(self):
        import registration.signals

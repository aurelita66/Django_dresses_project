from django.apps import AppConfig


class DresscodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dresscode'

    def ready(self):
        from .signals import create_profile

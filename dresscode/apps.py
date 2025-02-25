from django.apps import AppConfig


class DresscodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dresscode'

    def ready(self):
        """ Vykdomas programėlės paleidimo metu.
            Importuoja signalus, kad jie būtų prijungti ir veiktų.
            Šiuo atveju importuojamas 'create_profile' signalas.
        """
        from .signals import create_profile

from django.apps import AppConfig


class SbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SB'

    def ready(self) -> None:
        import SB.signals
        return super().ready()

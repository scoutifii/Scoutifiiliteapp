from django.apps import AppConfig


class ScoutifiiappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scoutifiiapp'
    
    def ready(self):
        import scoutifiiapp.signals

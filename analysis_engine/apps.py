from django.apps import AppConfig


class AnalysisEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analysis_engine'
    verbose_name = 'Business Analysis Engine'
    
    def ready(self):
        # Import signal handlers
        try:
            import analysis_engine.signals  # noqa
        except ImportError:
            pass

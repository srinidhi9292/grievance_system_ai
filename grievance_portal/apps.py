from django.apps import AppConfig


class GrievancePortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'grievance_portal'
    verbose_name = 'Grievance Portal'

    def ready(self):
        # Pre-initialize AI engine when Django starts
        try:
            from ai_engine import ai_engine
        except Exception as e:
            print(f"Warning: AI Engine initialization error: {e}")

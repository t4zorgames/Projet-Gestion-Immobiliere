from django.apps import AppConfig


class ImmobilierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'immobilier'

    def ready(self):
        # Import signal handlers to ensure they're registered
        try:
            import immobilier.signals  # noqa: F401
        except Exception:
            pass

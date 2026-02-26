"""
Django AppConfig for patients app.
"""
from django.apps import AppConfig


class PatientsConfig(AppConfig):
    """Configuration for the patients application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.patients'
    verbose_name = 'Patient Management'

    def ready(self):
        """Import signals when app is ready."""
        import apps.patients.signals  # noqa

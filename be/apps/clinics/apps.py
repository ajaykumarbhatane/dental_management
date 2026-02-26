"""
Django AppConfig for clinics app.
"""
from django.apps import AppConfig


class ClinicsConfig(AppConfig):
    """Configuration for the clinics application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.clinics'
    verbose_name = 'Clinic Management'

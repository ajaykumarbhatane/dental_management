"""
Django AppConfig for users app.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'

    def ready(self):
        """Import signals when app is ready."""
        import apps.users.signals  # noqa

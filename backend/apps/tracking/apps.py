from django.apps import AppConfig
from .utils.mongo_client import ensure_collections

class TrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tracking'

    def ready(self):
        """Ensure MongoDB collections exist when app starts."""
        ensure_collections() 
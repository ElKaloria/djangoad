from core.config import (
    get_django_settings, 
    get_postgres_settings,
    get_celery_settings
)

from .celery import app as celery_app


__all__ = ("celery_app",)
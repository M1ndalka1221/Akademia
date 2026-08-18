"""Basic initialization tests for Akademia Django app."""

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_django_settings_loaded() -> None:
    """Verify that Django settings are loaded properly."""
    assert settings.SECRET_KEY is not None
    assert isinstance(settings.DEBUG, bool)


def test_database_engine_is_postgresql() -> None:
    """Verify configured DB engine is PostgreSQL or SQLite."""
    engine: str = settings.DATABASES['default']['ENGINE']
    assert 'postgresql' in engine or 'sqlite3' in engine

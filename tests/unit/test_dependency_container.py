"""Unit tests for the dependency container."""

from fapi_tmpl.config import AppSettings
from fapi_tmpl.container import DependencyContainer


def test_dependency_container_exposes_settings_defaults() -> None:
    """Container should expose default application settings."""
    container = DependencyContainer()

    assert container.settings.app_name == "fapi-tmpl"
    assert container.settings.debug is False


def test_dependency_container_accepts_custom_settings() -> None:
    """Container should accept injected settings instances."""
    custom_settings = AppSettings(app_name="custom-app", debug=True)

    container = DependencyContainer(app_settings=custom_settings)

    assert container.settings.app_name == "custom-app"
    assert container.settings.debug is True

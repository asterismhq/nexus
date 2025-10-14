"""Dependency container for the FastAPI template."""

from dataclasses import dataclass
from typing import Optional

from .config import AppSettings, settings


@dataclass(slots=True)
class DependencyContainer:
    """Basic dependency container exposing application settings."""

    app_settings: AppSettings

    def __init__(self, app_settings: Optional[AppSettings] = None) -> None:
        self.app_settings = app_settings or AppSettings()

    @property
    def settings(self) -> AppSettings:
        """Return configured application settings."""
        return self.app_settings


container = DependencyContainer(settings)

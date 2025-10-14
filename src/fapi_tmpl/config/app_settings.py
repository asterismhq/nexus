"""Application-level settings for the FastAPI template."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Minimal settings exposed to the dependency container."""

    app_name: str = "fapi-tmpl"
    debug: bool = False


settings = AppSettings()

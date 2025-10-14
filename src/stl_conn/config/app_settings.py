"""Application-level settings for the FastAPI template."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Minimal settings exposed to the dependency container."""

    model_config = {"env_prefix": "STL_CONN_"}

    app_name: str = "stl-conn"
    debug: bool = False
    llm_backend: str = "ollama"
    use_mock_ollama: bool = False
    use_mock_mlx: bool = False


settings = AppSettings()

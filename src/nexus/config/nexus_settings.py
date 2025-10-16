"""Application-level settings for the FastAPI template."""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusSettings(BaseSettings):
    """Minimal settings exposed to the dependency container."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(
        default="nexus",
        title="Application Name",
        description="The name of the application.",
        alias="NEXUS_APP_NAME",
    )
    bind_ip: str = Field(
        default="127.0.0.1",
        title="Bind IP",
        description="IP address to bind the server to.",
        alias="NEXUS_BIND_IP",
    )
    bind_port: int = Field(
        default=8000,
        title="Bind Port",
        description="Port to bind the server to.",
        alias="NEXUS_BIND_PORT",
    )
    dev_port: int = Field(
        default=8000,
        title="Dev Port",
        description="Port used by just dev.",
        alias="NEXUS_DEV_PORT",
    )
    debug: bool = Field(
        default=False,
        title="Debug Mode",
        description="Enable debug mode.",
        alias="NEXUS_DEBUG",
    )
    llm_backend: str = Field(
        default="ollama",
        title="LLM Backend",
        description="The active LLM backend (ollama or mlx).",
        alias="NEXUS_LLM_BACKEND",
    )
    use_mock_ollama: bool = Field(
        default=False,
        title="Use Mock Ollama",
        description="Toggle mock Ollama client for tests.",
        alias="NEXUS_USE_MOCK_OLLAMA",
    )
    use_mock_mlx: bool = Field(
        default=False,
        title="Use Mock MLX",
        description="Toggle mock MLX client for tests.",
        alias="NEXUS_USE_MOCK_MLX",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> bool:
        """Ensure debug is parsed as a boolean from string."""
        if isinstance(value, str):
            return value.lower() in {"true", "1", "yes", "on"}
        return bool(value)


settings = NexusSettings()

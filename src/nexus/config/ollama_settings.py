"""Settings for configuring the Ollama client."""

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Configuration for interacting with an Ollama deployment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    host: AnyHttpUrl = Field(
        default="http://localhost:11434",
        title="Ollama Host",
        description="The base URL for the Ollama service.",
        alias="NEXUS_OLLAMA_HOST",
    )
    model: str = Field(
        default="tinyllama:1.1b",
        title="Ollama Model",
        description="The model to use for Ollama.",
        alias="NEXUS_OLLAMA_MODEL",
    )

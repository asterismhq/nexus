"""Settings for configuring MLX connectivity."""

from __future__ import annotations

from typing import Any

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLXSettings(BaseSettings):
    """Configuration values for MLX execution and routing."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    host: AnyHttpUrl = Field(
        ...,
        alias="NEXUS_MLX_HOST",
        description="Remote MLX server base URL.",
    )
    model: str = Field(
        default="mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit",
        alias="NEXUS_MLX_MODEL",
        description="Model identifier forwarded to MLX backends.",
    )
    temperature: float = Field(
        default=0.7,
        alias="NEXUS_MLX_TEMPERATURE",
        description="Sampling temperature for generation.",
    )
    max_tokens: int | None = Field(
        default=None,
        alias="NEXUS_MLX_MAX_TOKENS",
        description="Maximum number of tokens to generate.",
    )
    top_p: float | None = Field(
        default=None,
        alias="NEXUS_MLX_TOP_P",
        description="Top-p nucleus sampling parameter.",
    )
    timeout: int = Field(
        default=60,
        alias="NEXUS_MLX_TIMEOUT",
        description="Timeout applied to HTTP requests (seconds).",
    )

    def require_host(self) -> str:
        """Return the configured host."""

        return str(self.host).rstrip("/")

    def to_model_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments common to MLX generation calls."""

        kwargs: dict[str, Any] = {"temperature": self.temperature}
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs

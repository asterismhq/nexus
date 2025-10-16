"""Settings for configuring the MLX language model client."""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLXSettings(BaseSettings):
    """Configuration values for the MLX backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    model: str = Field(
        default="mlx-community/Phi-3-mini-4k-instruct-8bit",
        title="MLX Model",
        description="Identifier for the MLX model to load.",
        alias="NEXUS_MLX_MODEL",
    )
    temperature: float = Field(
        default=0.7,
        title="Temperature",
        description="Sampling temperature for generation.",
        alias="NEXUS_MLX_TEMPERATURE",
    )
    max_tokens: int | None = Field(
        default=None,
        title="Max Tokens",
        description="Maximum number of tokens to generate.",
        alias="NEXUS_MLX_MAX_TOKENS",
    )
    top_p: float | None = Field(
        default=None,
        title="Top P",
        description="Top-p sampling parameter.",
        alias="NEXUS_MLX_TOP_P",
    )

    def to_model_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments for MLX generation calls."""

        kwargs: dict[str, Any] = {"temperature": self.temperature}
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs

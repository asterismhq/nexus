"""Settings for configuring connectivity to a vLLM server."""

from __future__ import annotations

from typing import Any

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class VLLMSettings(BaseSettings):
    """Configuration container for vLLM backends."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    host: AnyHttpUrl = Field(
        default="http://localhost:8001",
        alias="NEXUS_VLLM_HOST",
        description="Base URL for the vLLM server.",
    )
    model: str = Field(
        default="facebook/opt-125m",
        alias="NEXUS_VLLM_MODEL",
        description="Model identifier forwarded to the vLLM backend.",
    )
    temperature: float = Field(
        default=0.7,
        alias="NEXUS_VLLM_TEMPERATURE",
        description="Sampling temperature for vLLM generations.",
    )
    max_tokens: int | None = Field(
        default=None,
        alias="NEXUS_VLLM_MAX_TOKENS",
        description="Optional cap on generated tokens.",
    )
    top_p: float | None = Field(
        default=None,
        alias="NEXUS_VLLM_TOP_P",
        description="Top-p nucleus sampling parameter.",
    )
    timeout: int = Field(
        default=60,
        alias="NEXUS_VLLM_TIMEOUT",
        description="Timeout applied to HTTP requests (seconds).",
    )
    api_key: SecretStr | None = Field(
        default=None,
        alias="NEXUS_VLLM_API_KEY",
        description="Optional bearer token for authenticated vLLM deployments.",
    )

    def require_host(self) -> str:
        """Return the configured host sans trailing slash."""

        return str(self.host).rstrip("/")

    def to_model_kwargs(self) -> dict[str, Any]:
        """Produce keyword arguments common to vLLM generation calls."""

        kwargs: dict[str, Any] = {"temperature": self.temperature}
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs

    def build_headers(self) -> dict[str, str]:
        """Return HTTP headers, injecting Authorization when available."""

        headers = {"Content-Type": "application/json"}
        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key.get_secret_value()}"
        return headers

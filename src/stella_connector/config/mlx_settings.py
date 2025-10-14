"""Settings for configuring the MLX language model client."""

from typing import Any

from pydantic_settings import BaseSettings


class MLXSettings(BaseSettings):
    """Configuration values for the MLX backend."""

    model_config = {"env_prefix": "STELLA_CONN_MLX_"}

    model: str = "mlx-community/Phi-3-mini-4k-instruct-8bit"
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None

    def to_model_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments for MLX generation calls."""

        kwargs: dict[str, Any] = {"temperature": self.temperature}
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs

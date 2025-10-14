"""MLX implementation of the :class:`LLMClientProtocol`."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from ..config.mlx_settings import MLXSettings
from ..protocols.llm_client_protocol import LLMClientProtocol


class MLXClient(LLMClientProtocol):
    """Thin wrapper around `mlx-lm` helpers."""

    def __init__(self, settings: MLXSettings) -> None:
        self._settings = settings
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._tools: list[Any] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        prompt = self._format_messages(messages)
        generation_kwargs = {**self._settings.to_model_kwargs(), **kwargs}
        model, tokenizer = self._ensure_model_loaded()
        return await asyncio.to_thread(
            self._generate, model, tokenizer, prompt, generation_kwargs
        )

    def bind_tools(self, tools: list[Any]) -> "MLXClient":
        self._tools = tools
        return self

    def _ensure_model_loaded(self) -> tuple[Any, Any]:
        if self._model is None or self._tokenizer is None:
            try:
                from mlx_lm import load
            except ImportError as exc:  # pragma: no cover - runtime dependency
                raise RuntimeError("mlx-lm must be installed to use MLXClient") from exc

            self._model, self._tokenizer = load(self._settings.model)
        return self._model, self._tokenizer

    def _generate(
        self, model: Any, tokenizer: Any, prompt: str, kwargs: dict[str, Any]
    ) -> Any:
        from mlx_lm import generate

        return generate(model, tokenizer, prompt, **kwargs)

    def _format_messages(self, messages: Any) -> str:
        if isinstance(messages, str):
            return messages
        if isinstance(messages, Iterable):
            parts: list[str] = []
            for message in messages:
                if isinstance(message, dict):
                    role = message.get("role")
                    content = message.get("content")
                    if role and content:
                        parts.append(f"{role}: {content}")
                        continue
                parts.append(str(message))
            return "\n".join(parts)
        return str(messages)

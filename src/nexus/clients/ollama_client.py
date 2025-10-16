"""Concrete implementation of the :class:`LLMClientProtocol` for Ollama."""

from __future__ import annotations

from typing import Any

from ..config.ollama_settings import OllamaSettings
from ..protocols.llm_client_protocol import LLMClientProtocol


class OllamaClient(LLMClientProtocol):
    """Client that communicates with an Ollama runtime."""

    def __init__(self, settings: OllamaSettings) -> None:
        try:
            from ollama import AsyncClient
        except (
            ImportError
        ) as exc:  # pragma: no cover - exercised in runtime environments
            raise RuntimeError(
                "ollama-python must be installed to use OllamaClient"
            ) from exc

        self._settings = settings
        self._client = AsyncClient(host=settings.host)
        self._tools: list[Any] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "model": self._settings.model,
            "messages": messages,
        }
        if self._tools:
            payload["tools"] = self._tools
        payload.update(kwargs)
        return await self._client.chat(**payload)

    def bind_tools(self, tools: list[Any]) -> "OllamaClient":
        self._tools = tools
        return self

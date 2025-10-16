"""Concrete implementation of the :class:`LLMClientProtocol` for Ollama."""

from __future__ import annotations

from typing import Any, AsyncIterator

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
        model_name = kwargs.pop("model", self._settings.model)
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
        }
        if self._tools:
            payload["tools"] = self._tools
        payload.update(kwargs)
        return await self._client.chat(**payload)

    async def stream(
        self, messages: Any, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:
        model_name = kwargs.pop("model", self._settings.model)
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }
        if self._tools:
            payload["tools"] = self._tools
        payload.update(kwargs)
        stream = await self._client.chat(**payload)

        async def _generator() -> AsyncIterator[dict[str, Any]]:
            async for chunk in stream:
                yield chunk

        return _generator()

    def bind_tools(self, tools: list[Any]) -> "OllamaClient":
        self._tools = tools
        return self

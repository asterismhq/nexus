"""HTTP client for remote MLX servers."""

from __future__ import annotations

from typing import Any, Iterable

import httpx

from ..config.mlx_settings import MLXSettings
from ..protocols.llm_client_protocol import LLMClientProtocol


class MLXClient(LLMClientProtocol):
    """HTTP client for remote MLX servers supporting OpenAI or JSON formats."""

    def __init__(self, settings: MLXSettings | None = None) -> None:
        self._settings = settings or MLXSettings()
        self._tools: list[Any] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        generation_kwargs = {**self._settings.to_model_kwargs(), **kwargs}
        if self._tools:
            generation_kwargs["tools"] = self._tools

        return await self._call_openai(messages, generation_kwargs)

    def bind_tools(self, tools: list[Any]) -> "MLXClient":
        self._tools = tools
        return self

    async def _call_openai(self, messages: Any, kwargs: dict[str, Any]) -> str:
        base_url = self._settings.require_host()

        payload: dict[str, Any] = {
            "model": self._settings.model,
            "messages": messages,
            "stream": False,
        }
        payload.update(kwargs)

        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        try:
            choice = data["choices"][0]
            return str(choice["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Malformed response from OpenAI-compatible MLX backend"
            ) from exc

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

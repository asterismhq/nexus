"""Async HTTP client for OpenAI-compatible vLLM deployments."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from ..config.vllm_settings import VLLMSettings
from ..protocols.llm_client_protocol import LLMClientProtocol


class VLLMClient(LLMClientProtocol):
    """HTTP client that targets a vLLM server exposing the OpenAI API."""

    def __init__(self, settings: VLLMSettings | None = None) -> None:
        self._settings = settings or VLLMSettings()
        self._tools: list[Any] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        model_name = kwargs.pop("model", self._settings.model)
        generation_kwargs = {**self._settings.to_model_kwargs(), **kwargs}
        if self._tools:
            generation_kwargs["tools"] = self._tools

        base_url = self._settings.require_host()
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }
        payload.update(generation_kwargs)

        headers = self._settings.build_headers()

        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def stream(
        self, messages: Any, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:
        model_name = kwargs.pop("model", self._settings.model)
        generation_kwargs = {**self._settings.to_model_kwargs(), **kwargs}
        if self._tools:
            generation_kwargs["tools"] = self._tools

        base_url = self._settings.require_host()
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }
        payload.update(generation_kwargs)

        headers = self._settings.build_headers()

        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            async with client.stream(
                "POST",
                f"{base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()

                async def _generator() -> AsyncIterator[dict[str, Any]]:
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            data_text = line[len("data:") :].strip()
                            if data_text == "[DONE]":
                                break
                            yield json.loads(data_text)

                return _generator()

    def bind_tools(self, tools: list[Any]) -> "VLLMClient":
        self._tools = tools
        return self

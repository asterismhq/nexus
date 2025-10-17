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

    def _prepare_request(
        self, messages: Any, stream: bool, **kwargs: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        model_name = kwargs.pop("model", self._settings.model)
        generation_kwargs = {**self._settings.to_model_kwargs(), **kwargs}
        if self._tools:
            generation_kwargs["tools"] = self._tools

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": stream,
        }
        payload.update(generation_kwargs)

        headers = self._settings.build_headers()
        return payload, headers

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        payload, headers = self._prepare_request(messages, stream=False, **kwargs)

        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            response = await client.post(
                f"{self._settings.require_host()}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def stream(
        self, messages: Any, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:
        payload, headers = self._prepare_request(messages, stream=True, **kwargs)

        async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
            async with client.stream(
                "POST",
                f"{self._settings.require_host()}/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_text = line[len("data:") :].strip()
                        if data_text == "[DONE]":
                            break
                        yield json.loads(data_text)

    def bind_tools(self, tools: list[Any]) -> "VLLMClient":
        self._tools = tools
        return self

"""Mock implementation of the Ollama client used in tests."""

from __future__ import annotations

from typing import Any, AsyncIterator

from nexus.config.ollama_settings import OllamaSettings
from nexus.protocols.llm_client_protocol import LLMClientProtocol


class MockOllamaClient(LLMClientProtocol):
    """A lightweight mock that records invocations for assertions."""

    def __init__(self, settings: OllamaSettings | None = None) -> None:
        self.settings = settings or OllamaSettings()
        self.bound_tools: list[Any] = []
        self.invocations: list[dict[str, Any]] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        model_name = kwargs.pop("model", self.settings.model)
        payload = {
            "model": model_name,
            "messages": messages,
            "tools": list(self.bound_tools),
            "kwargs": kwargs,
            "stream": False,
        }
        self.invocations.append(payload)
        return "Mock Ollama response"

    async def stream(
        self, messages: Any, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:
        model_name = kwargs.pop("model", self.settings.model)
        payload = {
            "model": model_name,
            "messages": messages,
            "tools": list(self.bound_tools),
            "kwargs": kwargs,
            "stream": True,
        }
        self.invocations.append(payload)

        async def _generator() -> AsyncIterator[dict[str, Any]]:
            yield {
                "id": "chatcmpl-mock",
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Mock Ollama response"},
                        "finish_reason": None,
                    }
                ],
            }
            yield {
                "id": "chatcmpl-mock",
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }
                ],
            }

        return _generator()

    def bind_tools(self, tools: list[Any]) -> "MockOllamaClient":
        self.bound_tools = tools
        return self

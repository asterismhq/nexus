"""Mock implementation of the Ollama client used in tests."""

from __future__ import annotations

from typing import Any

from stl_conn.config.ollama_settings import OllamaSettings
from stl_conn.protocols.llm_client_protocol import LLMClientProtocol


class MockOllamaClient(LLMClientProtocol):
    """A lightweight mock that records invocations for assertions."""

    def __init__(self, settings: OllamaSettings | None = None) -> None:
        self.settings = settings or OllamaSettings()
        self.bound_tools: list[Any] = []
        self.invocations: list[dict[str, Any]] = []

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "tools": list(self.bound_tools),
            "kwargs": kwargs,
        }
        self.invocations.append(payload)
        return {
            "model": self.settings.model,
            "message": "Mock Ollama response",
            "input": payload,
        }

    def bind_tools(self, tools: list[Any]) -> "MockOllamaClient":
        self.bound_tools = tools
        return self

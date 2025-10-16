"""Mock implementation of the MLX LLM client."""

from __future__ import annotations

from typing import Any, AsyncIterator

from nexus.config.mlx_settings import MLXSettings
from nexus.protocols.llm_client_protocol import LLMClientProtocol


class MockMLXClient(LLMClientProtocol):
    """Mock MLX client capturing messages without running an actual model."""

    def __init__(self, settings: MLXSettings | None = None) -> None:
        self.settings = settings or MLXSettings()
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
        return "Mock MLX response"

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
                "id": "chatcmpl-mock-mlx",
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Mock MLX response"},
                        "finish_reason": None,
                    }
                ],
            }
            yield {
                "id": "chatcmpl-mock-mlx",
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

    def bind_tools(self, tools: list[Any]) -> "MockMLXClient":
        self.bound_tools = tools
        return self

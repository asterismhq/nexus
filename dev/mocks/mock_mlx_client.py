"""Mock implementation of the MLX LLM client."""

from __future__ import annotations

from typing import Any

from stl_conn.config.mlx_settings import MLXSettings
from stl_conn.protocols.llm_client_protocol import LLMClientProtocol


class MockMLXClient(LLMClientProtocol):
    """Mock MLX client capturing messages without running an actual model."""

    def __init__(self, settings: MLXSettings | None = None) -> None:
        self.settings = settings or MLXSettings()
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
            "message": "Mock MLX response",
            "input": payload,
        }

    def bind_tools(self, tools: list[Any]) -> "MockMLXClient":
        self.bound_tools = tools
        return self

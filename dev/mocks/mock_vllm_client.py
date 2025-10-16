from __future__ import annotations

from typing import Any, AsyncIterator

from nexus.config.vllm_settings import VLLMSettings
from nexus.protocols.llm_client_protocol import LLMClientProtocol


class MockVLLMClient(LLMClientProtocol):
    """Lightweight mock of the vLLM client used in tests."""

    def __init__(self, settings: VLLMSettings | None = None) -> None:
        self.settings = settings or VLLMSettings()
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
        return {"choices": [{"message": {"content": "Mock vLLM response"}}]}

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
                "id": "chatcmpl-mock-vllm",
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Mock vLLM response"},
                        "finish_reason": None,
                    }
                ],
            }
            yield {
                "id": "chatcmpl-mock-vllm",
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

    def bind_tools(self, tools: list[Any]) -> "MockVLLMClient":
        self.bound_tools = tools
        return self

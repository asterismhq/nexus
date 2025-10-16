from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .client import _validate_response_format
from .protocol import NexusClientProtocol
from .response import LangChainResponse
from .strategies import (
    MockResponse,
    MockResponseStrategy,
    SimpleResponseStrategy,
)


class MockNexusClient:
    _MOCK_CONTENT = "This is a mock response from Nexus."

    def __init__(
        self,
        response_format: str = "dict",
        strategy: MockResponseStrategy | None = None,
    ) -> None:
        self.response_format = _validate_response_format(response_format)
        self.invocations: List[Dict[str, Any]] = []
        self._tools: List[Any] | None = None
        self._strategy: MockResponseStrategy = strategy or SimpleResponseStrategy(
            self._MOCK_CONTENT
        )

    def bind_tools(self, tools: Sequence[Any]) -> "MockNexusClient":
        self._tools = list(tools)
        return self

    def set_strategy(self, strategy: MockResponseStrategy) -> "MockNexusClient":
        """Configure the strategy used to build mock responses."""

        self._strategy = strategy
        return self

    @property
    def strategy(self) -> MockResponseStrategy:
        return self._strategy

    async def invoke(self, input_data: Any, **_: Any) -> Any:
        payload = self._prepare_payload(input_data)
        self.invocations.append(payload)
        response = self._resolve_response(payload)
        if self.response_format == "langchain":
            return self._build_langchain_response(response)
        return self._build_dict_response(response)

    def _resolve_response(self, payload: Dict[str, Any]) -> MockResponse:
        strategy = self._strategy
        if not strategy.should_handle(payload):
            raise RuntimeError("Configured mock strategy cannot handle the payload")
        raw_response = strategy.generate(payload)
        return self._ensure_mock_response(raw_response)

    def _ensure_mock_response(self, value: Any) -> MockResponse:
        if isinstance(value, MockResponse):
            return value.copy()
        if isinstance(value, dict) and "content" in value:
            tool_calls = value.get("tool_calls", [])
            if not isinstance(tool_calls, list):
                tool_calls = list(tool_calls)
            return MockResponse(content=value["content"], tool_calls=tool_calls)
        return MockResponse(content=value)

    def _build_langchain_response(self, response: MockResponse) -> LangChainResponse:
        message_payload = {
            "content": response.content,
            "tool_calls": list(response.tool_calls),
        }
        return LangChainResponse(
            content=response.content,
            tool_calls=list(response.tool_calls),
            raw_output={"message": message_payload},
            raw_response={"output": {"message": message_payload}},
        )

    def _build_dict_response(self, response: MockResponse) -> Dict[str, Any]:
        result: Dict[str, Any] = {"output": response.content}
        if response.tool_calls:
            result["tool_calls"] = list(response.tool_calls)
        return result

    def _prepare_payload(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, dict):
            payload = dict(input_data)
            if "input_data" in payload:
                payload = payload["input_data"]
            if self._tools and "tools" not in payload:
                payload["tools"] = self._tools
            return payload

        serialized = self._serialize_messages(input_data)
        payload: Dict[str, Any] = {"input": serialized}
        if self._tools:
            payload["tools"] = self._tools
        return payload

    def _serialize_messages(self, messages: Any) -> Any:
        if not isinstance(messages, list):
            return messages

        serialized: List[Dict[str, Any]] = []
        for msg in messages:
            if hasattr(msg, "type") and hasattr(msg, "content"):
                data: Dict[str, Any] = {
                    "role": getattr(msg, "type"),
                    "content": getattr(msg, "content"),
                }
                additional_kwargs = getattr(msg, "additional_kwargs", None)
                if isinstance(additional_kwargs, dict) and additional_kwargs:
                    data["additional_kwargs"] = additional_kwargs
                serialized.append(data)
            elif isinstance(msg, dict):
                serialized.append(msg)
            else:
                serialized.append({"role": "user", "content": str(msg)})
        return serialized


# For static type checking
_: NexusClientProtocol = MockNexusClient()

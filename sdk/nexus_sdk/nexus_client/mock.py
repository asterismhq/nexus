from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Sequence

from .base_client import _normalize_backend_name, _validate_response_format
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
        *,
        backend: str,
    ) -> None:
        self.response_format = _validate_response_format(response_format)
        self.invocations: List[Dict[str, Any]] = []
        self._tools: List[Any] | None = None
        self._strategy: MockResponseStrategy = strategy or SimpleResponseStrategy(
            self._MOCK_CONTENT
        )
        self._backend = _normalize_backend_name(backend)

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

    async def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        payload = self._prepare_payload(input_data)
        if "backend" in payload and isinstance(payload["backend"], str):
            payload["backend"] = _normalize_backend_name(payload["backend"])

        override_backend = kwargs.pop("backend", None)
        if override_backend:
            payload["backend"] = _normalize_backend_name(str(override_backend))
        else:
            payload.setdefault("backend", self._backend)

        if kwargs:
            filtered_kwargs = {
                key: value
                for key, value in kwargs.items()
                if key not in {"model", "messages", "tools"}
            }
            if filtered_kwargs:
                payload.update(filtered_kwargs)

        self.invocations.append(payload)
        response = self._resolve_response(payload)
        wire_response = self._build_openai_response(payload, response)
        if self.response_format == "langchain":
            return self._build_langchain_response(wire_response)
        return wire_response

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

    def _build_langchain_response(
        self, wire_response: Dict[str, Any]
    ) -> LangChainResponse:
        choices = wire_response.get("choices", [])
        choice = choices[0] if choices else {}
        message = choice.get("message", {}) if isinstance(choice, dict) else {}
        tool_calls = message.get("tool_calls") or []

        return LangChainResponse(
            content=message.get("content"),
            tool_calls=list(tool_calls),
            raw_output=choice,
            raw_response=wire_response,
        )

    def _build_openai_response(
        self, payload: Dict[str, Any], response: MockResponse
    ) -> Dict[str, Any]:
        message_payload = {
            "role": "assistant",
            "content": response.content,
            "tool_calls": list(response.tool_calls),
        }

        choice = {
            "index": 0,
            "message": message_payload,
            "finish_reason": "stop",
        }

        return {
            "id": f"chatcmpl-mock-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": payload.get("model", "mock-model"),
            "choices": [choice],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

    def _prepare_payload(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, dict):
            payload = dict(input_data)
        else:
            payload = {"messages": self._serialize_messages(input_data)}

        if "input_data" in payload:
            nested = payload.pop("input_data")
            if isinstance(nested, dict):
                payload.update(nested)

        if "messages" not in payload and "input" in payload:
            payload["messages"] = payload.pop("input")

        payload.setdefault("model", "mock-model")

        normalized_messages = self._ensure_message_list(payload.get("messages", []))
        payload["messages"] = normalized_messages

        if self._tools and "tools" not in payload:
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

    def _ensure_message_list(self, messages: Any) -> List[Dict[str, Any]]:
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        if not isinstance(messages, list):
            return [{"role": "user", "content": str(messages)}]
        normalized: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, dict):
                normalized.append(msg)
                continue
            if hasattr(msg, "type") and hasattr(msg, "content"):
                normalized.append(
                    {
                        "role": getattr(msg, "type"),
                        "content": getattr(msg, "content"),
                        "additional_kwargs": getattr(msg, "additional_kwargs", None)
                        or None,
                    }
                )
                if normalized[-1]["additional_kwargs"] is None:
                    normalized[-1].pop("additional_kwargs")
                continue
            normalized.append({"role": "user", "content": str(msg)})
        return normalized


# For static type checking
_: NexusClientProtocol = MockNexusClient(backend="ollama")

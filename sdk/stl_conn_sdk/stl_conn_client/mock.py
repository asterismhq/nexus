from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .client import _validate_response_format
from .protocol import StlConnClientProtocol
from .response import LangChainResponse


class MockStlConnClient:
    _MOCK_CONTENT = "This is a mock response from Stl-Conn."

    def __init__(self, response_format: str = "dict"):
        self.response_format = _validate_response_format(response_format)
        self.invocations: List[Dict[str, Any]] = []
        self._tools: List[Any] | None = None

    def bind_tools(self, tools: Sequence[Any]) -> "MockStlConnClient":
        self._tools = list(tools)
        return self

    async def invoke(self, input_data: Any, **_: Any) -> Any:
        payload = self._prepare_payload(input_data)
        self.invocations.append(payload)
        if self.response_format == "langchain":
            mock_json_content = self._build_langchain_content(payload)
            mock_tool_calls = self._build_mock_tool_calls(payload)
            return LangChainResponse(
                content=mock_json_content,
                tool_calls=mock_tool_calls,
                raw_output={
                    "message": {
                        "content": mock_json_content,
                        "tool_calls": mock_tool_calls,
                    }
                },
                raw_response={
                    "output": {
                        "message": {
                            "content": mock_json_content,
                            "tool_calls": mock_tool_calls,
                        }
                    }
                },
            )
        return {"output": self._MOCK_CONTENT}

    def _build_langchain_content(self, payload: Dict[str, Any]) -> str:
        messages = payload.get("input")
        message_str = str(messages).lower()

        if "query" in message_str or "search" in message_str:
            return '{"query": "mock search query for testing", "rationale": "This is a mock query"}'
        if "reflect" in message_str or "evaluation" in message_str:
            return '{"reflection": "This is a mock reflection.", "evaluation": "continue", "rationale": "Mock evaluation for testing"}'
        if "summary" in message_str or "summarize" in message_str:
            return '{"summary": "This is a mock summary of the research. The mock client has generated this response for testing purposes."}'
        return '{"query": "test query", "rationale": "test rationale"}'

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

    def _build_mock_tool_calls(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        tools = payload.get("tools", [])
        if not tools:
            return []
        # Return a mock tool call for the first tool
        first_tool = tools[0]
        if isinstance(first_tool, dict) and "name" in first_tool:
            return [{"name": first_tool["name"], "args": {"mock_arg": "mock_value"}}]
        return [{"name": "mock_tool", "args": {"mock_arg": "mock_value"}}]


# For static type checking
_: StlConnClientProtocol = MockStlConnClient()

from __future__ import annotations

from typing import Any, Dict, Final, List, Sequence

import httpx

from .protocol import NexusClientProtocol
from .response import LangChainResponse

_DEFAULT_RESPONSE_FORMAT: Final[str] = "dict"
_SUPPORTED_RESPONSE_FORMATS: Final[frozenset[str]] = frozenset({"dict", "langchain"})


def _validate_response_format(response_format: str) -> str:
    if response_format not in _SUPPORTED_RESPONSE_FORMATS:
        supported = ", ".join(sorted(_SUPPORTED_RESPONSE_FORMATS))
        raise ValueError(
            f"Unsupported response_format '{response_format}'. Supported formats: {supported}."
        )
    return response_format


class NexusClient:
    def __init__(
        self,
        base_url: str,
        response_format: str = _DEFAULT_RESPONSE_FORMAT,
        timeout: float = 10.0,
    ):
        self.base_url = base_url
        self.response_format = _validate_response_format(response_format)
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._tools: List[Any] | None = None

    def bind_tools(self, tools: Sequence[Any]) -> "NexusClient":
        """Store tool definitions for upcoming invokes (LangChain-style chaining)."""
        self._tools = list(tools)
        return self

    async def invoke(self, input_data: Any, **_: Any) -> Any:
        payload = self._prepare_payload(input_data)
        response = await self._client.post(
            "/api/chat/invoke", json={"input_data": payload}
        )
        response.raise_for_status()
        result = response.json()
        return self._format_response(result)

    def _format_response(self, result: Dict[str, Any]) -> Any:
        if self.response_format == "langchain":
            return self._to_langchain_response(result)
        return result

    def _to_langchain_response(self, result: Dict[str, Any]) -> LangChainResponse:
        output = result.get("output")

        content: Any = ""
        tool_calls: Any = []

        if isinstance(output, dict):
            message = output.get("message")
            if isinstance(message, dict):
                content = message.get("content", "")
                tool_calls = message.get("tool_calls", [])
            elif message is not None:
                content = message
            elif "content" in output:
                content = output.get("content", "")
            else:
                content = output
        elif output is not None:
            content = output

        if isinstance(tool_calls, list):
            normalized_tool_calls = tool_calls
        elif tool_calls:
            normalized_tool_calls = [tool_calls]
        else:
            normalized_tool_calls = []

        return LangChainResponse(
            content=content,
            tool_calls=normalized_tool_calls,
            raw_output=output,
            raw_response=result,
        )

    def _prepare_payload(self, input_data: Any) -> Dict[str, Any]:
        """
        Normalize payload for the /invoke endpoint.

        Accepts:
        - Raw dicts (backwards compatibility)
        - LangChain message objects (list with `.type`/`.content`)
        - Plain lists of dicts/strings
        """
        if isinstance(input_data, dict):
            payload = dict(input_data)
            # Support callers that already wrap data as {"input": ...}
            if "input_data" in payload:
                payload = payload["input_data"]
            if self._tools and "tools" not in payload:
                payload["tools"] = self._tools
            return payload

        serialized_messages = self._serialize_messages(input_data)
        payload: Dict[str, Any] = {"input": serialized_messages}
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

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "NexusClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()


# For static type checking
_: NexusClientProtocol = NexusClient(base_url="")

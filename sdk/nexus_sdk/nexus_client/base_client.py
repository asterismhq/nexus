from __future__ import annotations

from typing import Any, Dict, Final, List, Sequence

import httpx

from .protocol import NexusClientProtocol
from .response import LangChainResponse

_DEFAULT_RESPONSE_FORMAT: Final[str] = "dict"
_SUPPORTED_RESPONSE_FORMATS: Final[frozenset[str]] = frozenset({"dict", "langchain"})


def _normalize_backend_name(value: str) -> str:
    return value.lower().strip()


def _prepare_invoke_payload(
    payload: Dict[str, Any], kwargs: Dict[str, Any], backend: str
) -> None:
    """Prepare payload for invoke by handling backend and kwargs."""
    if "backend" in payload and isinstance(payload["backend"], str):
        payload["backend"] = _normalize_backend_name(payload["backend"])

    override_backend = kwargs.pop("backend", None)
    if override_backend:
        payload["backend"] = _normalize_backend_name(str(override_backend))
    else:
        payload.setdefault("backend", backend)

    if kwargs:
        filtered_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"model", "messages", "tools"}
        }
        if filtered_kwargs:
            payload.update(filtered_kwargs)


def _validate_response_format(response_format: str) -> str:
    if response_format not in _SUPPORTED_RESPONSE_FORMATS:
        supported = ", ".join(sorted(_SUPPORTED_RESPONSE_FORMATS))
        raise ValueError(
            f"Unsupported response_format '{response_format}'. Supported formats: {supported}."
        )
    return response_format


class BaseNexusClient(NexusClientProtocol):
    """Shared HTTP client implementation for the Nexus SDK backends."""

    def __init__(
        self,
        base_url: str,
        response_format: str = _DEFAULT_RESPONSE_FORMAT,
        timeout: float = 10.0,
        *,
        backend: str,
    ) -> None:
        self.base_url = base_url
        self.response_format = _validate_response_format(response_format)
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._backend = _normalize_backend_name(backend)
        self._tools: List[Any] | None = None

    def bind_tools(self, tools: Sequence[Any]) -> "BaseNexusClient":
        """Store tool definitions for upcoming invokes (LangChain-style chaining)."""

        self._tools = list(tools)
        return self

    async def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        payload = self._prepare_payload(input_data)
        _prepare_invoke_payload(payload, kwargs, self._backend)

        response = await self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        result = response.json()
        return self._format_response(result)

    def _format_response(self, result: Dict[str, Any]) -> Any:
        if self.response_format == "langchain":
            return self._to_langchain_response(result)
        return result

    def _to_langchain_response(self, result: Dict[str, Any]) -> LangChainResponse:
        content: Any = ""
        tool_calls: Any = []

        choices = result.get("choices")
        if isinstance(choices, list) and choices:
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                message = first_choice.get("message")
                if isinstance(message, dict):
                    content = message.get("content", "")
                    tool_calls = message.get("tool_calls", [])
                elif message is not None:
                    content = message
                elif "delta" in first_choice:
                    delta = first_choice.get("delta", {})
                    if isinstance(delta, dict):
                        content = delta.get("content", "")
                else:
                    content = first_choice

        if isinstance(tool_calls, list):
            normalized_tool_calls = tool_calls
        elif tool_calls:
            normalized_tool_calls = [tool_calls]
        else:
            normalized_tool_calls = []

        raw_output = choices[0] if isinstance(choices, list) and choices else result

        return LangChainResponse(
            content=content,
            tool_calls=normalized_tool_calls,
            raw_output=raw_output,
            raw_response=result,
        )

    def _prepare_payload(self, input_data: Any) -> Dict[str, Any]:
        """Normalize payload for the /invoke endpoint.
        Accepts:
        - Raw dicts (backwards compatibility)
        - LangChain message objects (list with `.type`/`.content`)
        - Plain lists of dicts/strings
        """

        if isinstance(input_data, dict):
            payload = dict(input_data)
        else:
            payload = {"messages": self._serialize_messages(input_data)}

        if "input_data" in payload:
            nested = payload.pop("input_data")
            if isinstance(nested, dict):
                payload.update(nested)

        if "messages" not in payload:
            if "input" in payload:
                payload["messages"] = self._ensure_message_list(payload.pop("input"))
            else:
                raise ValueError("messages must be provided for chat completions")

        if "model" not in payload:
            raise ValueError("model must be specified for chat completions")

        payload["messages"] = self._ensure_message_list(payload["messages"])

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

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""

        await self._client.aclose()

    async def __aenter__(self) -> "BaseNexusClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: D401
        await self.aclose()

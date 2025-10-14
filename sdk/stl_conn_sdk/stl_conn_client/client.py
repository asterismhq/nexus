from __future__ import annotations

from typing import Any, Dict, Final

import httpx

from .protocol import StlConnClientProtocol
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


class StlConnClient:
    def __init__(
        self,
        base_url: str,
        response_format: str = _DEFAULT_RESPONSE_FORMAT,
        timeout: float = 10.0,
    ):
        self.base_url = base_url
        self.response_format = _validate_response_format(response_format)
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def invoke(self, input_data: Dict[str, Any]) -> Any:
        response = await self._client.post(
            "/api/chat/invoke", json={"input_data": input_data}
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

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "StlConnClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()


# For static type checking
_: StlConnClientProtocol = StlConnClient(base_url="")

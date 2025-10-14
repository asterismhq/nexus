from __future__ import annotations

from typing import Any, Dict, List

from .protocol import StlConnClientProtocol
from .response import LangChainResponse


class MockStlConnClient:
    _SUPPORTED_FORMATS = {"dict", "langchain"}
    _MOCK_CONTENT = "This is a mock response from Stl-Conn."

    def __init__(self, response_format: str = "dict"):
        if response_format not in self._SUPPORTED_FORMATS:
            supported = ", ".join(sorted(self._SUPPORTED_FORMATS))
            raise ValueError(
                f"Unsupported response_format '{response_format}'. Supported formats: {supported}."
            )
        self.response_format = response_format
        self.invocations: List[Dict[str, Any]] = []

    async def invoke(self, input_data: Dict[str, Any]) -> Any:
        self.invocations.append(input_data)
        if self.response_format == "langchain":
            return LangChainResponse(
                content=self._MOCK_CONTENT,
                tool_calls=[],
                raw_output={"message": {"content": self._MOCK_CONTENT}},
                raw_response={"output": {"message": {"content": self._MOCK_CONTENT}}},
            )
        return {"output": self._MOCK_CONTENT}


# For static type checking
_: StlConnClientProtocol = MockStlConnClient()

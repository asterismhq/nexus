from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class MockResponse:
    """Container for responses emitted by mock strategies."""

    content: Any
    tool_calls: List[Any] = field(default_factory=list)

    def copy(self) -> "MockResponse":
        return MockResponse(content=self.content, tool_calls=list(self.tool_calls))


class MockResponseStrategy(ABC):
    """Strategy interface for `MockNexusClient` response generation."""

    def should_handle(self, payload: Dict[str, Any]) -> bool:
        """Return True when the strategy is able to handle the payload."""

        return True

    @abstractmethod
    def generate(self, payload: Dict[str, Any]) -> MockResponse:
        """Generate a mock response for the given payload."""

        raise NotImplementedError


def coerce_to_mock_response(value: Any) -> MockResponse:
    """Coerce a value into a MockResponse, handling various input types."""
    if isinstance(value, MockResponse):
        return value.copy()
    if isinstance(value, dict):
        content = value.get("content")
        if content is None:
            raise ValueError("response dict must include 'content'")
        tool_calls = value.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            tool_calls = list(tool_calls)
        return MockResponse(content=content, tool_calls=tool_calls)
    return MockResponse(content=value)

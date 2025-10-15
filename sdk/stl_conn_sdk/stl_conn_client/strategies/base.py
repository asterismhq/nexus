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
    """Strategy interface for `MockStlConnClient` response generation."""

    def should_handle(self, payload: Dict[str, Any]) -> bool:
        """Return True when the strategy is able to handle the payload."""

        return True

    @abstractmethod
    def generate(self, payload: Dict[str, Any]) -> MockResponse:
        """Generate a mock response for the given payload."""

        raise NotImplementedError

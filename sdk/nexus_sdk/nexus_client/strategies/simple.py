from __future__ import annotations

from typing import Any, Sequence

from .base import MockResponse, MockResponseStrategy


class SimpleResponseStrategy(MockResponseStrategy):
    """Always returns the same response and optional tool calls."""

    def __init__(self, content: Any, tool_calls: Sequence[Any] | None = None):
        self._content = content
        self._tool_calls = list(tool_calls) if tool_calls is not None else []

    def generate(self, payload: dict[str, Any]) -> MockResponse:  # noqa: ARG002
        return MockResponse(content=self._content, tool_calls=list(self._tool_calls))

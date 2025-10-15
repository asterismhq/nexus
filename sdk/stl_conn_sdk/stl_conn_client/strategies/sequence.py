from __future__ import annotations

from typing import Any, Sequence

from .base import MockResponse, MockResponseStrategy


class SequenceResponseStrategy(MockResponseStrategy):
    """Returns predefined responses for successive invocations."""

    def __init__(self, responses: Sequence[Any], repeat_last: bool = False) -> None:
        if not responses:
            raise ValueError("responses must not be empty")
        self._responses = [self._coerce(response) for response in responses]
        self._repeat_last = repeat_last
        self._index = 0

    def generate(self, payload: dict[str, Any]) -> MockResponse:  # noqa: ARG002
        if self._index >= len(self._responses):
            if self._repeat_last:
                return self._responses[-1].copy()
            raise RuntimeError("SequenceResponseStrategy exhausted all responses")
        response = self._responses[self._index].copy()
        self._index += 1
        return response

    def reset(self) -> None:
        """Reset the sequence pointer back to the beginning."""

        self._index = 0

    def _coerce(self, value: Any) -> MockResponse:
        if isinstance(value, MockResponse):
            return value.copy()
        if isinstance(value, dict):
            content = value.get("content")
            if content is None:
                raise ValueError("sequence response dict must include 'content'")
            tool_calls = value.get("tool_calls", [])
            if not isinstance(tool_calls, list):
                tool_calls = list(tool_calls)
            return MockResponse(content=content, tool_calls=tool_calls)
        return MockResponse(content=value)

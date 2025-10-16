from __future__ import annotations

from typing import Any, Sequence

from .base import MockResponse, MockResponseStrategy, coerce_to_mock_response


class SequenceResponseStrategy(MockResponseStrategy):
    """Returns predefined responses for successive invocations."""

    def __init__(self, responses: Sequence[Any], repeat_last: bool = False) -> None:
        if not responses:
            raise ValueError("responses must not be empty")
        self._responses = [coerce_to_mock_response(response) for response in responses]
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

from __future__ import annotations

from typing import Any, Callable, Dict, Sequence

from .base import MockResponse, MockResponseStrategy


class CallbackResponseStrategy(MockResponseStrategy):
    """Delegates response generation to user-provided callables."""

    def __init__(
        self,
        callback: Callable[[Dict[str, Any]], Any],
        tool_callback: Callable[[Dict[str, Any]], Sequence[Any]] | None = None,
        predicate: Callable[[Dict[str, Any]], bool] | None = None,
    ) -> None:
        self._callback = callback
        self._tool_callback = tool_callback
        self._predicate = predicate

    def should_handle(self, payload: Dict[str, Any]) -> bool:
        if self._predicate is None:
            return True
        return bool(self._predicate(payload))

    def generate(self, payload: Dict[str, Any]) -> MockResponse:
        content = self._callback(payload)
        tool_calls: Sequence[Any] = []
        if self._tool_callback is not None:
            tool_calls = self._tool_callback(payload)
        return MockResponse(content=content, tool_calls=list(tool_calls))

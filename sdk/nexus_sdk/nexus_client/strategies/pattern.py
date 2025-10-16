from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Pattern

from .base import MockResponse, MockResponseStrategy, coerce_to_mock_response


class PatternMatchingStrategy(MockResponseStrategy):
    """Matches message text against regex patterns to select responses."""

    def __init__(self, patterns: Mapping[str, Any], default: Any | None = None) -> None:
        if not patterns:
            raise ValueError("patterns must not be empty")
        self._patterns: list[tuple[Pattern[str], Any]] = [
            (re.compile(pattern, flags=re.MULTILINE), response)
            for pattern, response in patterns.items()
        ]
        self._default = default

    def should_handle(self, payload: Dict[str, Any]) -> bool:
        return self._find_match(payload) is not None or self._default is not None

    def generate(self, payload: Dict[str, Any]) -> MockResponse:
        match = self._find_match(payload)
        if match is None:
            if self._default is None:
                raise RuntimeError("no pattern matched the payload")
            return coerce_to_mock_response(self._default)
        _, response = match
        return coerce_to_mock_response(response)

    def _find_match(self, payload: Dict[str, Any]) -> tuple[Pattern[str], Any] | None:
        message_str = self._extract_message_text(payload)
        for pattern, response in self._patterns:
            if pattern.search(message_str):
                return pattern, response
        return None

    def _extract_message_text(self, payload: Dict[str, Any]) -> str:
        raw_input = payload.get("input")
        if isinstance(raw_input, list):
            parts: list[str] = []
            for item in raw_input:
                if isinstance(item, dict):
                    content = item.get("content")
                    if content is not None:
                        parts.append(str(content))
                    else:
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        if raw_input is None:
            return ""
        return str(raw_input)

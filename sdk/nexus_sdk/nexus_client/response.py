from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class LangChainResponse:
    """LangChain-compatible response wrapper for Stella Connector SDK."""

    content: Any
    tool_calls: List[Any] = field(default_factory=list)
    raw_output: Optional[Any] = None
    raw_response: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        # Ensure tool_calls is always a plain list for LangChain compatibility.
        self.tool_calls = list(self.tool_calls)

"""Protocol definition for language model client interface."""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol


class LLMClientProtocol(Protocol):
    """Protocol defining the interface for any LLM client implementation.

    This allows for dependency injection and easier testing.
    """

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        """Generate a response from the LLM."""

    async def stream(self, messages: Any, **kwargs: Any) -> AsyncIterator[Any]:
        """Stream a response from the LLM chunk by chunk."""

    def bind_tools(self, tools: list[Any]) -> "LLMClientProtocol":
        """Bind tools to the LLM client for function calling."""

from typing import Any, Protocol, Sequence


class StlConnClientProtocol(Protocol):
    def bind_tools(self, tools: Sequence[Any]) -> "StlConnClientProtocol": ...

    async def invoke(self, input_data: Any, **kwargs: Any) -> Any: ...

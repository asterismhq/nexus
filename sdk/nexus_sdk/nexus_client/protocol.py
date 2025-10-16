from typing import Any, Protocol, Sequence


class NexusClientProtocol(Protocol):
    def bind_tools(self, tools: Sequence[Any]) -> "NexusClientProtocol": ...

    async def invoke(self, input_data: Any, **kwargs: Any) -> Any: ...

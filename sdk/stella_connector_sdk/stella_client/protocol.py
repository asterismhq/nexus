from typing import Any, Dict, Protocol


class StellaConnectorClientProtocol(Protocol):
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]: ...

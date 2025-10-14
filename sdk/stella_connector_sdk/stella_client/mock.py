from typing import Any, Dict

from .protocol import StellaConnectorClientProtocol


class MockStellaConnectorClient:
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Mock invoke called with: {input_data}")
        return {"output": "This is a mock response from Stella Connector."}


# For static type checking
_: StellaConnectorClientProtocol = MockStellaConnectorClient()

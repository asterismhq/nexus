from typing import Any, Dict, List

from .protocol import StlConnClientProtocol


class MockStlConnClient:
    def __init__(self):
        self.invocations: List[Dict[str, Any]] = []

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.invocations.append(input_data)
        return {"output": "This is a mock response from Stl-Conn."}


# For static type checking
_: StlConnClientProtocol = MockStlConnClient()

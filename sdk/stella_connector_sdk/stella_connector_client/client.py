from typing import Any, Dict

import httpx

from .protocol import StellaConnectorClientProtocol


class StellaConnectorClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/api/v1/chat/invoke"
            response = await client.post(url, json=input_data)
            response.raise_for_status()
            return response.json()


# For static type checking
_: StellaConnectorClientProtocol = StellaConnectorClient(base_url="")

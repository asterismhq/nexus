from unittest.mock import AsyncMock, Mock, patch

import pytest
from stella_connector_sdk.stella_connector_client import StellaConnectorClient


@pytest.mark.asyncio
async def test_stella_client_invoke():
    client = StellaConnectorClient(base_url="http://example.com")
    mock_response = Mock()
    mock_response.json.return_value = {"result": "test"}
    mock_response.raise_for_status.return_value = None
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance
        result = await client.invoke({"input": "test"})
        mock_client_instance.post.assert_called_once_with(
            "http://example.com/api/chat/invoke", json={"input_data": {"input": "test"}}
        )
        assert result == {"result": "test"}

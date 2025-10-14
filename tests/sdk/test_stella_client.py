from unittest.mock import Mock, patch

from stella_connector_sdk.stella_client import StellaConnectorClient


def test_stella_client_invoke():
    client = StellaConnectorClient(base_url="http://example.com")
    mock_response = Mock()
    mock_response.json.return_value = {"result": "test"}
    with patch("httpx.post", return_value=mock_response) as mock_post:
        result = client.invoke({"input": "test"})
        mock_post.assert_called_once_with(
            "http://example.com/api/v1/chat/invoke", json={"input": "test"}
        )
        assert result == {"result": "test"}

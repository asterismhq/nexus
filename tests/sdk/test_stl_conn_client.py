from unittest.mock import AsyncMock, Mock, patch

import pytest
from stl_conn_sdk.stl_conn_client import (
    LangChainResponse,
    MockStlConnClient,
    StlConnClient,
)


@pytest.mark.asyncio
async def test_stl_conn_client_invoke():
    mock_response = Mock()
    mock_response.json.return_value = {"result": "test"}
    mock_response.raise_for_status.return_value = None
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = StlConnClient(base_url="http://example.com")
        result = await client.invoke({"input": "test"})
        mock_client_instance.post.assert_called_once_with(
            "/api/chat/invoke", json={"input_data": {"input": "test"}}
        )
        assert result == {"result": "test"}


@pytest.mark.asyncio
async def test_stl_conn_client_invoke_langchain_response():
    mock_response = Mock()
    mock_response.json.return_value = {
        "output": {
            "message": {
                "content": "Hello from Stella Connector",
                "tool_calls": [{"type": "test"}],
            }
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = StlConnClient(
            base_url="http://example.com", response_format="langchain"
        )

        result = await client.invoke({"input": "test"})

        assert isinstance(result, LangChainResponse)
        assert result.content == "Hello from Stella Connector"
        assert result.tool_calls == [{"type": "test"}]
        assert result.raw_response == mock_response.json.return_value


def test_stl_conn_client_rejects_unknown_response_format():
    with pytest.raises(ValueError):
        StlConnClient(base_url="http://example.com", response_format="unknown")


def test_stl_conn_client_timeout_parameter():
    with patch("httpx.AsyncClient") as mock_client_class:
        StlConnClient(base_url="http://example.com", timeout=30.0)
        mock_client_class.assert_called_once_with(
            base_url="http://example.com", timeout=30.0
        )


@pytest.mark.asyncio
async def test_stl_conn_client_aclose():
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value = mock_client_instance
        client = StlConnClient(base_url="http://example.com")
        await client.aclose()
        mock_client_instance.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_mock_client_langchain_response():
    client = MockStlConnClient(response_format="langchain")
    result = await client.invoke({"input": "test"})

    assert isinstance(result, LangChainResponse)
    assert result.content == "This is a mock response from Stl-Conn."
    assert result.tool_calls == []


def test_mock_client_rejects_unknown_response_format():
    with pytest.raises(ValueError):
        MockStlConnClient(response_format="unknown")

from typing import Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from stl_conn_sdk.stl_conn_client import (
    LangChainResponse,
    MockStlConnClient,
    SimpleResponseStrategy,
    StlConnClient,
)


class _FakeLangChainMessage:
    def __init__(
        self, msg_type: str, content: str, additional_kwargs: Optional[dict] = None
    ):
        self.type = msg_type
        self.content = content
        self.additional_kwargs = additional_kwargs or {}


@pytest.mark.asyncio
async def test_stl_conn_client_invoke_with_dict_payload():
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
async def test_stl_conn_client_serializes_langchain_messages():
    mock_response = Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = StlConnClient(base_url="http://example.com")

        messages = [
            _FakeLangChainMessage("user", "hello"),
            {"role": "assistant", "content": "hi"},
            "fallback",
        ]

        await client.invoke(messages)

        mock_client_instance.post.assert_called_once_with(
            "/api/chat/invoke",
            json={
                "input_data": {
                    "input": [
                        {"role": "user", "content": "hello"},
                        {"role": "assistant", "content": "hi"},
                        {"role": "user", "content": "fallback"},
                    ]
                }
            },
        )


@pytest.mark.asyncio
async def test_stl_conn_client_bind_tools_adds_tools():
    mock_response = Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = StlConnClient(base_url="http://example.com")

        client.bind_tools([{"name": "calculator"}])
        await client.invoke([{"role": "user", "content": "compute"}])

        mock_client_instance.post.assert_called_once_with(
            "/api/chat/invoke",
            json={
                "input_data": {
                    "input": [{"role": "user", "content": "compute"}],
                    "tools": [{"name": "calculator"}],
                }
            },
        )


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

        result = await client.invoke([{"role": "user", "content": "test"}])

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
    result = await client.invoke([{"role": "user", "content": "test"}])

    assert isinstance(result, LangChainResponse)
    assert result.content == "This is a mock response from Stl-Conn."
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_mock_client_records_serialized_invocations_with_tools():
    client = MockStlConnClient()
    client.bind_tools([{"name": "web_search"}])

    await client.invoke([_FakeLangChainMessage("user", "go find", {"foo": "bar"})])

    assert client.invocations[-1] == {
        "input": [
            {"role": "user", "content": "go find", "additional_kwargs": {"foo": "bar"}}
        ],
        "tools": [{"name": "web_search"}],
    }


def test_mock_client_rejects_unknown_response_format():
    with pytest.raises(ValueError):
        MockStlConnClient(response_format="unknown")


@pytest.mark.asyncio
async def test_mock_client_langchain_response_with_tools():
    strategy = SimpleResponseStrategy(
        content={"result": "ok"},
        tool_calls=[{"name": "calculator", "args": {"total": 42}}],
    )
    client = MockStlConnClient(response_format="langchain", strategy=strategy)
    client.bind_tools([{"name": "calculator"}])
    result = await client.invoke([{"role": "user", "content": "test"}])

    assert isinstance(result, LangChainResponse)
    assert result.content == {"result": "ok"}
    assert result.tool_calls == [{"name": "calculator", "args": {"total": 42}}]
    assert client.invocations[-1]["tools"] == [{"name": "calculator"}]

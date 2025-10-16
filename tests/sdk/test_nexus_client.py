from typing import Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nexus_sdk.nexus_client import (
    LangChainResponse,
    MockNexusClient,
    NexusClient,
    SimpleResponseStrategy,
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
        client = NexusClient(base_url="http://example.com")
        result = await client.invoke({"model": "test-model", "messages": "test"})
        mock_client_instance.post.assert_called_once_with(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}],
            },
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
        client = NexusClient(base_url="http://example.com")

        messages = [
            _FakeLangChainMessage("user", "hello"),
            {"role": "assistant", "content": "hi"},
            "fallback",
        ]

        await client.invoke({"model": "test-model", "messages": messages})

        mock_client_instance.post.assert_called_once_with(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "hi"},
                    {"role": "user", "content": "fallback"},
                ],
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
        client = NexusClient(base_url="http://example.com")

        client.bind_tools([{"name": "calculator"}])
        await client.invoke(
            {
                "model": "test-model",
                "messages": [{"role": "user", "content": "compute"}],
            }
        )

        mock_client_instance.post.assert_called_once_with(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "compute"}],
                "tools": [{"name": "calculator"}],
            },
        )


@pytest.mark.asyncio
async def test_stl_conn_client_invoke_langchain_response():
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 123,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello from Stella Connector",
                    "tool_calls": [{"type": "test"}],
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = NexusClient(base_url="http://example.com", response_format="langchain")

        result = await client.invoke(
            {"model": "test-model", "messages": [{"role": "user", "content": "test"}]}
        )

        assert isinstance(result, LangChainResponse)
        assert result.content == "Hello from Stella Connector"
        assert result.tool_calls == [{"type": "test"}]
        assert result.raw_response == mock_response.json.return_value


def test_stl_conn_client_rejects_unknown_response_format():
    with pytest.raises(ValueError):
        NexusClient(base_url="http://example.com", response_format="unknown")


def test_stl_conn_client_timeout_parameter():
    with patch("httpx.AsyncClient") as mock_client_class:
        NexusClient(base_url="http://example.com", timeout=30.0)
        mock_client_class.assert_called_once_with(
            base_url="http://example.com", timeout=30.0
        )


@pytest.mark.asyncio
async def test_stl_conn_client_aclose():
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value = mock_client_instance
        client = NexusClient(base_url="http://example.com")
        await client.aclose()
        mock_client_instance.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_mock_client_langchain_response():
    client = MockNexusClient(response_format="langchain")
    result = await client.invoke(
        {"model": "mock", "messages": [{"role": "user", "content": "test"}]}
    )

    assert isinstance(result, LangChainResponse)
    assert result.content == "This is a mock response from Nexus."
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_mock_client_records_serialized_invocations_with_tools():
    client = MockNexusClient()
    client.bind_tools([{"name": "web_search"}])

    await client.invoke(
        {
            "model": "mock",
            "messages": [_FakeLangChainMessage("user", "go find", {"foo": "bar"})],
        }
    )

    recorded = client.invocations[-1]
    assert recorded["model"] == "mock"
    assert recorded["messages"] == [
        {"role": "user", "content": "go find", "additional_kwargs": {"foo": "bar"}}
    ]
    assert recorded["tools"] == [{"name": "web_search"}]


def test_mock_client_rejects_unknown_response_format():
    with pytest.raises(ValueError):
        MockNexusClient(response_format="unknown")


@pytest.mark.asyncio
async def test_mock_client_langchain_response_with_tools():
    strategy = SimpleResponseStrategy(
        content={"result": "ok"},
        tool_calls=[{"name": "calculator", "args": {"total": 42}}],
    )
    client = MockNexusClient(response_format="langchain", strategy=strategy)
    client.bind_tools([{"name": "calculator"}])
    result = await client.invoke(
        {"model": "mock", "messages": [{"role": "user", "content": "test"}]}
    )

    assert isinstance(result, LangChainResponse)
    assert result.content == {"result": "ok"}
    assert result.tool_calls == [{"name": "calculator", "args": {"total": 42}}]
    assert client.invocations[-1]["tools"] == [{"name": "calculator"}]

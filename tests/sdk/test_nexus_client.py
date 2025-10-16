from typing import Any, Optional, Type
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nexus_sdk.nexus_client import (
    LangChainResponse,
    MockNexusClient,
    NexusMLXClient,
    NexusOllamaClient,
    NexusVLLMClient,
    SimpleResponseStrategy,
)

_BASE_CLIENT_PATH = "nexus_sdk.nexus_client.base_client.httpx.AsyncClient"


class _FakeLangChainMessage:
    def __init__(
        self, msg_type: str, content: str, additional_kwargs: Optional[dict] = None
    ) -> None:
        self.type = msg_type
        self.content = content
        self.additional_kwargs = additional_kwargs or {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("client_cls", "expected_backend"),
    [
        (NexusOllamaClient, "ollama"),
        (NexusMLXClient, "mlx"),
        (NexusVLLMClient, "vllm"),
    ],
)
async def test_backend_clients_invoke_with_dict_payload(
    client_cls: Type[Any], expected_backend: str
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = {"result": "test"}
    mock_response.raise_for_status.return_value = None
    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = client_cls(base_url="http://example.com")
        result = await client.invoke({"model": "test-model", "messages": "test"})
        mock_client_instance.post.assert_called_once_with(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}],
                "backend": expected_backend,
            },
        )
        assert result == {"result": "test"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("client_cls", "expected_backend"),
    [
        (NexusOllamaClient, "ollama"),
        (NexusMLXClient, "mlx"),
        (NexusVLLMClient, "vllm"),
    ],
)
async def test_backend_clients_serialize_langchain_messages(
    client_cls: Type[Any], expected_backend: str
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = client_cls(base_url="http://example.com")

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
                "backend": expected_backend,
            },
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("client_cls", "expected_backend"),
    [
        (NexusOllamaClient, "ollama"),
        (NexusMLXClient, "mlx"),
        (NexusVLLMClient, "vllm"),
    ],
)
async def test_backend_clients_bind_tools_adds_tools(
    client_cls: Type[Any], expected_backend: str
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = client_cls(base_url="http://example.com")

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
                "backend": expected_backend,
            },
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client_cls",
    [NexusOllamaClient, NexusMLXClient, NexusVLLMClient],
)
async def test_backend_clients_langchain_response(
    client_cls: Type[Any],
) -> None:
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

    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        client = client_cls(base_url="http://example.com", response_format="langchain")

        result = await client.invoke(
            {"model": "test-model", "messages": [{"role": "user", "content": "test"}]}
        )

        assert isinstance(result, LangChainResponse)
        assert result.content == "Hello from Stella Connector"
        assert result.tool_calls == [{"type": "test"}]
        assert result.raw_response == mock_response.json.return_value


@pytest.mark.parametrize(
    "client_cls",
    [NexusOllamaClient, NexusMLXClient, NexusVLLMClient],
)
def test_clients_reject_unknown_response_format(client_cls: Type[Any]) -> None:
    with pytest.raises(ValueError):
        client_cls(base_url="http://example.com", response_format="unknown")


@pytest.mark.parametrize(
    "client_cls",
    [NexusOllamaClient, NexusMLXClient, NexusVLLMClient],
)
def test_backend_clients_timeout_parameter(client_cls: Type[Any]) -> None:
    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        client_cls(base_url="http://example.com", timeout=30.0)
        mock_client_class.assert_called_once_with(
            base_url="http://example.com", timeout=30.0
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client_cls",
    [NexusOllamaClient, NexusMLXClient, NexusVLLMClient],
)
async def test_backend_clients_aclose(client_cls: Type[Any]) -> None:
    with patch(_BASE_CLIENT_PATH) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value = mock_client_instance
        client = client_cls(base_url="http://example.com")
        await client.aclose()
        mock_client_instance.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_mock_client_langchain_response() -> None:
    client = MockNexusClient(response_format="langchain", backend="ollama")
    result = await client.invoke(
        {"model": "mock", "messages": [{"role": "user", "content": "test"}]}
    )

    assert isinstance(result, LangChainResponse)
    assert result.content == "This is a mock response from Nexus."
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_mock_client_records_serialized_invocations_with_tools() -> None:
    client = MockNexusClient(backend="ollama")
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
    assert recorded["backend"] == "ollama"


def test_mock_client_rejects_unknown_response_format() -> None:
    with pytest.raises(ValueError):
        MockNexusClient(response_format="unknown", backend="ollama")


@pytest.mark.asyncio
async def test_mock_client_langchain_response_with_tools() -> None:
    strategy = SimpleResponseStrategy(
        content={"result": "ok"},
        tool_calls=[{"name": "calculator", "args": {"total": 42}}],
    )
    client = MockNexusClient(
        response_format="langchain", strategy=strategy, backend="ollama"
    )
    client.bind_tools([{"name": "calculator"}])
    result = await client.invoke(
        {"model": "mock", "messages": [{"role": "user", "content": "test"}]}
    )

    assert isinstance(result, LangChainResponse)
    assert result.content == {"result": "ok"}
    assert result.tool_calls == [{"name": "calculator", "args": {"total": 42}}]
    assert client.invocations[-1]["tools"] == [{"name": "calculator"}]


@pytest.mark.asyncio
async def test_mock_client_records_backend_choice() -> None:
    client = MockNexusClient(backend="mlx")
    await client.invoke({"model": "mock", "messages": "hi"})
    assert client.invocations[-1]["backend"] == "mlx"

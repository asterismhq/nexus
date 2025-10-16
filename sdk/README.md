# Nexus SDK

The Nexus SDK provides a Python client library for interacting with the Nexus API, enabling seamless integration with Large Language Model (LLM) services through a unified interface.

## Overview

Nexus is a FastAPI service that mediates LLM inference across multiple pluggable backends (Ollama, MLX). The SDK ships backend-aware clients—`NexusOllamaClient` and `NexusMLXClient`—so external applications can choose or pin a backend without manually shaping HTTP requests.

### Key Features

- **Unified API**: Single interface for multiple LLM backends.
- **Backend Hints**: Pick a backend once or override per call without changing payload shapes.
- **LangChain Native**: Accepts LangChain message objects and returns `LangChainResponse` when requested.
- **Tool Binding**: `bind_tools()` mirrors LangChain patterns for function calling.
- **Async Support**: Full asyncio compatibility for high-performance applications.
- **Type Safety**: Full type hints and protocol-based design.
- **Mock Client**: Built-in mock client with matching serialization and tool binding.
- **Error Handling**: Comprehensive error handling with detailed responses.
- **Flexible Configuration**: Environment-aware configuration.

## Quick Start

### LangChain Messages (Recommended)

```python
import asyncio
from langchain_core.messages import HumanMessage
from nexus_sdk.nexus_client import NexusOllamaClient


async def main():
    client = NexusOllamaClient(
        base_url="http://localhost:8000",
        response_format="langchain",
    )

    response = await client.invoke(
        {
            "model": "your-model-id",
            "messages": [HumanMessage(content="Hello, world!")],
        }
    )
    print(response.content)


asyncio.run(main())
```

### Tool Binding

```python
import asyncio
from nexus_sdk.nexus_client import NexusMLXClient


async def main():
    client = NexusMLXClient(base_url="https://your-nexus-instance.com")
    client.bind_tools([{"name": "calculator"}])

    response = await client.invoke(
        {
            "model": "your-model-id",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
        }
    )
    print(response)


asyncio.run(main())
```

### Dict Payloads Are Still Supported

```python
response = await client.invoke(
    {
        "model": "your-model-id",
        "messages": "Explain quantum computing",
        "temperature": 0.7,
        "stream": False,
    }
)
```

### Backend Selection

Pick the correct runtime by instantiating the corresponding client class. The backend hint is encoded in the class itself, so there is no separate flag to remember later. Example with the MLX client:

```python
import asyncio
from nexus_sdk.nexus_client import NexusMLXClient


async def main():
    client = NexusMLXClient(base_url="http://localhost:8000")
    result = await client.invoke(
        {
            "model": "mlx-model",
            "messages": "summarise the paper",
        }
    )
    print(result)


asyncio.run(main())
```

### Mock Client for Testing

```python
import asyncio
from nexus_sdk.nexus_client import MockNexusClient

async def main():
    client = MockNexusClient(response_format="langchain", backend="ollama").bind_tools(
        [{"name": "search"}]
    )

    response = await client.invoke(
        {
            "model": "mock-model",
            "messages": [{"role": "user", "content": "search headlines"}],
        }
    )
    print(response.content)
    print(client.invocations[-1])

asyncio.run(main())
```

#### Strategy-Based Responses

The mock client now accepts pluggable strategies so tests can precisely control the simulated output:

```python
from nexus_sdk.nexus_client import (
    MockNexusClient,
    SequenceResponseStrategy,
    SimpleResponseStrategy,
)

# Default behaviour mirrors a simple textual response
mock_client = MockNexusClient(backend="ollama")

# Fixed JSON payload with bespoke tool call metadata
mock_client.set_strategy(
    SimpleResponseStrategy(
        content={"summary": "precomputed"},
        tool_calls=[{"name": "summarizer", "args": {}}],
    )
)

# Multi-turn sequence for more complex workflows
mock_client.bind_tools([{"name": "search"}])
mock_client.set_strategy(
    SequenceResponseStrategy([
        {"content": {"query": "first"}},
        {"content": {"query": "refine"}},
        {"content": {"summary": "done"}},
    ])
)
```

Additional built-ins include `PatternMatchingStrategy` and `CallbackResponseStrategy`.

#### Testing Example

```python
import pytest
from nexus_sdk.nexus_client import MockNexusClient

@pytest.mark.asyncio
async def test_my_function():
    mock_client = MockNexusClient(backend="ollama")

    # Call your function that uses the client
    result = await my_function_that_uses_client(mock_client)

    # Verify invocations
    assert len(mock_client.invocations) == 1
    assert mock_client.invocations[0]["input"] == "expected input"

    # Verify result
    assert "expected output" in result
```

## API Reference

### NexusOllamaClient & NexusMLXClient

```python
NexusOllamaClient(base_url: str, response_format: str = "dict", timeout: float = 10.0)
NexusMLXClient(base_url: str, response_format: str = "dict", timeout: float = 10.0)
```

The SDK exposes two concrete HTTP clients. Choose the class that matches the backend you want to reach:

- `base_url`: Base URL of the Nexus API (e.g., "http://localhost:8000").
- `response_format`: Response format (`"dict"` for raw JSON, `"langchain"` for `LangChainResponse`).
- `timeout`: Request timeout in seconds (default: 10.0).

Both classes share the same API surface:

- `bind_tools(tools: Sequence[Any]) -> Self`: store tool definitions to include in subsequent invocations.
- `invoke(messages: Any, **kwargs: Any) -> Union[Dict[str, Any], LangChainResponse]`: send a chat completion request. `messages` accepts LangChain objects, dicts, or strings. Additional keyword arguments (e.g., `temperature`, `max_tokens`) are forwarded verbatim to Nexus.
- `aclose() -> None`: close the underlying `httpx.AsyncClient`. They support async context management for automatic cleanup.

Both clients automatically attach the appropriate backend hint, so requests are routed correctly without extra parameters.

### MockNexusClient

#### Constructor

```python
MockNexusClient(
    response_format: str = "dict",
    strategy: MockResponseStrategy | None = None,
    backend: str,
)
```

#### Methods

##### `bind_tools(tools: Sequence[Any]) -> MockNexusClient`

Mirrors the real client by storing bound tools and returning `self`.

##### `invoke(messages: Any, **kwargs: Any) -> Union[Dict[str, Any], LangChainResponse]`

Returns a deterministic mock response and records the serialized payload. Mirrors the behaviour of the real clients. Provide the backend you want to simulate via the constructor, or override per call using `invoke(..., backend="...")`. The response is controlled by the configured strategy (defaults to `SimpleResponseStrategy`).

#### Properties

##### `invocations: List[Dict[str, Any]]`

List of serialized payloads passed to `invoke()` calls. Useful for testing. When a backend hint is active, the payload includes a `backend` field.

### LangChainResponse

The SDK exposes a `LangChainResponse` dataclass when `response_format="langchain"` is selected.

```python
LangChainResponse(
    content: Any,
    tool_calls: List[Any] = [],
    raw_output: Optional[Any] = None,
    raw_response: Optional[Dict[str, Any]] = None,
)
```

- `content`: The response content extracted from the API payload.
- `tool_calls`: Optional tool call metadata for LangChain/LangGraph integrations.
- `raw_output`: The `output` portion of the original API response.
- `raw_response`: The full API response body for reference/debugging.

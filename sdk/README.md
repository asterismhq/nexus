# Stella Connector SDK

The Stella Connector SDK provides a Python client library for interacting with the Stella Connector API, enabling seamless integration with Large Language Model (LLM) services through a unified interface.

## Overview

Stella Connector is a FastAPI service that mediates LLM inference across multiple pluggable backends (Ollama, MLX). The SDK allows external applications to easily invoke LLM operations without directly managing HTTP requests or backend-specific configurations.

### Key Features

- **Unified API**: Single interface for multiple LLM backends.
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
from stl_conn_sdk.stl_conn_client import StlConnClient

async def main():
    client = StlConnClient(
        base_url="http://localhost:8000",
        response_format="langchain",
    )

    response = await client.invoke([HumanMessage(content="Hello, world!")])
    print(response.content)

asyncio.run(main())
```

### Tool Binding

```python
import asyncio
from stl_conn_sdk.stl_conn_client import StlConnClient

async def main():
    client = StlConnClient(base_url="https://your-stl-conn-instance.com")
    client.bind_tools([{"name": "calculator"}])

    response = await client.invoke([{"role": "user", "content": "What is 2+2?"}])
    print(response)

asyncio.run(main())
```

### Dict Payloads Are Still Supported

```python
response = await client.invoke({"input": "Explain quantum computing", "temperature": 0.7})
```

### Mock Client for Testing

```python
import asyncio
from stl_conn_sdk.stl_conn_client import MockStlConnClient

async def main():
    client = MockStlConnClient(response_format="langchain").bind_tools(
        [{"name": "search"}]
    )

    response = await client.invoke([{"role": "user", "content": "search headlines"}])
    print(response.content)
    print(client.invocations[-1])

asyncio.run(main())
```

#### Strategy-Based Responses

The mock client now accepts pluggable strategies so tests can precisely control the simulated output:

```python
from stl_conn_sdk.stl_conn_client import (
    MockStlConnClient,
    SequenceResponseStrategy,
    SimpleResponseStrategy,
)

# Default behaviour mirrors a simple textual response
mock_client = MockStlConnClient()

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
from stl_conn_sdk.stl_conn_client import MockStlConnClient

@pytest.mark.asyncio
async def test_my_function():
    mock_client = MockStlConnClient()

    # Call your function that uses the client
    result = await my_function_that_uses_client(mock_client)

    # Verify invocations
    assert len(mock_client.invocations) == 1
    assert mock_client.invocations[0]["input"] == "expected input"

    # Verify result
    assert "expected output" in result
```

## API Reference

### StlConnClient

#### Constructor

```python
StlConnClient(base_url: str, response_format: str = "dict", timeout: float = 10.0)
```

- `base_url`: Base URL of the Stella Connector API (e.g., "http://localhost:8000")
- `response_format`: Response format (`"dict"` for raw JSON, `"langchain"` for `LangChainResponse`)
- `timeout`: Request timeout in seconds (default: 10.0)

#### Methods

##### `bind_tools(tools: Sequence[Any]) -> StlConnClient`

Registers tool definitions for upcoming requests. Returns `self` so calls can be chained.

##### `invoke(messages: Any, **kwargs: Any) -> Union[Dict[str, Any], LangChainResponse]`

Invokes the LLM with LangChain messages or dict payloads and returns the response in the configured format.

**Parameters:**
- `messages`: LangChain message objects, list of role/content dicts, or a pre-built payload dict.
- `**kwargs`: Reserved for future options; ignored for compatibility with LangChain's signature.

**Returns:**
- Raw dictionary response (default).
- `LangChainResponse` object when `response_format="langchain"`.

**Raises:**
- `httpx.TimeoutException`: If request times out.
- `httpx.HTTPStatusError`: For HTTP error responses.

##### `aclose() -> None`

Closes the underlying HTTP client connection pool. Should be called when the client is no longer needed to free up resources.

**Usage with context manager:**

```python
async with StlConnClient(base_url="http://localhost:8000") as client:
    response = await client.invoke({"input": "Hello"})
```

**Manual cleanup:**

```python
client = StlConnClient(base_url="http://localhost:8000")
try:
    response = await client.invoke({"input": "Hello"})
finally:
    await client.aclose()
```

### MockStlConnClient

#### Constructor

```python
MockStlConnClient(
    response_format: str = "dict",
    strategy: MockResponseStrategy | None = None,
)
```

#### Methods

##### `bind_tools(tools: Sequence[Any]) -> MockStlConnClient`

Mirrors the real client by storing bound tools and returning `self`.

##### `invoke(messages: Any, **kwargs: Any) -> Union[Dict[str, Any], LangChainResponse]`

Returns a deterministic mock response and records the serialized payload. Mirrors the `response_format` behavior of `StlConnClient`. The response is controlled by the configured strategy (defaults to `SimpleResponseStrategy`).

#### Properties

##### `invocations: List[Dict[str, Any]]`

List of serialized payloads passed to `invoke()` calls. Useful for testing.

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

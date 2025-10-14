# Stella Connector SDK

The Stella Connector SDK provides a Python client library for interacting with the Stella Connector API, enabling seamless integration with Large Language Model (LLM) services through a unified interface.

## Overview

Stella Connector is a FastAPI service that mediates LLM inference across multiple pluggable backends (Ollama, MLX). The SDK allows external applications to easily invoke LLM operations without directly managing HTTP requests or backend-specific configurations.

### Key Features

- **Unified API**: Single interface for multiple LLM backends
- **Async Support**: Full asyncio compatibility for high-performance applications
- **Type Safety**: Full type hints and protocol-based design
- **Mock Client**: Built-in mock client for testing and development
- **Optional LangChain Wrapper**: Toggle between raw dict responses and LangChain-friendly objects
- **Error Handling**: Comprehensive error handling with detailed responses
- **Flexible Configuration**: Environment-aware configuration

## Quick Start

### Basic Usage

```python
import asyncio
from stl_conn_sdk.stl_conn_client import StlConnClient

async def main():
    # Initialize client with base URL
    client = StlConnClient(base_url="http://localhost:8000")

    # Invoke LLM with input data
    response = await client.invoke(input_data={"input": "Hello, world!"})

    print(response)
    # {"output": "Hello! How can I help you today?"}

asyncio.run(main())
```

### With Custom Configuration

```python
import asyncio
from stl_conn_sdk.stl_conn_client import StlConnClient

async def main():
    client = StlConnClient(
        base_url="https://your-stl-conn-instance.com",
        response_format="langchain",  # Optional LangChain-compatible response wrapper
    )

    response = await client.invoke(input_data={
        "input": "Explain quantum computing in simple terms",
        "temperature": 0.7,
        "max_tokens": 500
    })

    print(response.content)

asyncio.run(main())
```

The SDK respects the following environment variable:

- `STL_CONN_API_BASE_URL`: Default base URL for clients

### Mock Client for Testing

```python
import asyncio
from stl_conn_sdk.stl_conn_client import MockStlConnClient

async def main():
    # Create mock client
    client = MockStlConnClient(response_format="langchain")

    # Invoke returns predefined response
    response = await client.invoke(input_data={"input": "test message"})

    print(response)
    # LangChainResponse(content="This is a mock response from Stella Connector.")

    # Access invocation history for testing
    print(client.invocations)
    # [{"input": "test message"}]

asyncio.run(main())
```

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
StlConnClient(base_url: str, response_format: str = "dict")
```

- `base_url`: Base URL of the Stella Connector API (e.g., "http://localhost:8000")
- `response_format`: Response format (`"dict"` for raw JSON, `"langchain"` for `LangChainResponse`)

#### Methods

##### `invoke(input_data: Dict[str, Any]) -> Union[Dict[str, Any], LangChainResponse]`

Invokes the LLM with the provided input data and returns the response in the configured format.

**Parameters:**
- `input_data`: Dictionary containing input parameters
  - `input`: The text prompt (required)
  - Additional parameters are passed to the LLM backend

**Returns:**
- Raw dictionary response (default)
- `LangChainResponse` object when `response_format="langchain"`

**Raises:**
- `httpx.TimeoutException`: If request times out
- `httpx.HTTPStatusError`: For HTTP error responses
- `ValueError`: For invalid input data

### MockStlConnClient

#### Constructor

```python
MockStlConnClient(response_format: str = "dict")
```

#### Methods

##### `invoke(input_data: Dict[str, Any]) -> Union[Dict[str, Any], LangChainResponse]`

Returns a mock response and records the invocation. Mirrors the `response_format` behavior of `StlConnClient`.

**Parameters:**
- `input_data`: Input data (recorded but not processed)

**Returns:**
- `{"output": "This is a mock response from Stl-Conn."}` (default)
- `LangChainResponse(content="This is a mock response from Stl-Conn.")` when `response_format="langchain"`

#### Properties

##### `invocations: List[Dict[str, Any]]`

List of all input_data passed to `invoke()` calls. Useful for testing.

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

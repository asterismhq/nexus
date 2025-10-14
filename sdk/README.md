# Stella Connector SDK

The Stella Connector SDK provides a Python client library for interacting with the Stella Connector API, enabling seamless integration with Large Language Model (LLM) services through a unified interface.

## Overview

Stella Connector is a FastAPI service that mediates LLM inference across multiple pluggable backends (Ollama, MLX). The SDK allows external applications to easily invoke LLM operations without directly managing HTTP requests or backend-specific configurations.

### Key Features

- **Unified API**: Single interface for multiple LLM backends
- **Async Support**: Full asyncio compatibility for high-performance applications
- **Type Safety**: Full type hints and protocol-based design
- **Mock Client**: Built-in mock client for testing and development
- **Error Handling**: Comprehensive error handling with detailed responses
- **Flexible Configuration**: Environment-aware configuration

## Installation

Install the SDK dependencies:

```bash
uv sync --group sdk
```

## Quick Start

### Basic Usage

```python
import asyncio
from stella_connector_sdk.stella_connector_client import StellaConnectorClient

async def main():
    # Initialize client with base URL
    client = StellaConnectorClient(base_url="http://localhost:8000")

    # Invoke LLM with input data
    response = await client.invoke(input_data={"input": "Hello, world!"})

    print(response)
    # {"output": "Hello! How can I help you today?"}

asyncio.run(main())
```

### With Custom Configuration

```python
import asyncio
from stella_connector_sdk.stella_connector_client import StellaConnectorClient

async def main():
    client = StellaConnectorClient(
        base_url="https://your-stella-connector-instance.com",
        timeout=30.0  # Custom timeout in seconds
    )

    response = await client.invoke(input_data={
        "input": "Explain quantum computing in simple terms",
        "temperature": 0.7,
        "max_tokens": 500
    })

    print(response["output"])

asyncio.run(main())
```

The SDK respects the following environment variables:

- `STELLA_CONN_API_BASE_URL`: Default base URL for clients
- `STELLA_CONN_API_TIMEOUT`: Default timeout for requests

### Mock Client for Testing

```python
import asyncio
from stella_connector_sdk.stella_connector_client import MockStellaConnectorClient

async def main():
    # Create mock client
    client = MockStellaConnectorClient()

    # Invoke returns predefined response
    response = await client.invoke(input_data={"input": "test message"})

    print(response)
    # {"output": "This is a mock response from Stella Connector."}

    # Access invocation history for testing
    print(client.invocations)
    # [{"input": "test message"}]

asyncio.run(main())
```

#### Testing Example

```python
import pytest
from stella_connector_sdk.stella_connector_client import MockStellaConnectorClient

@pytest.mark.asyncio
async def test_my_function():
    mock_client = MockStellaConnectorClient()

    # Call your function that uses the client
    result = await my_function_that_uses_client(mock_client)

    # Verify invocations
    assert len(mock_client.invocations) == 1
    assert mock_client.invocations[0]["input"] == "expected input"

    # Verify result
    assert "expected output" in result
```

## API Reference

### StellaConnectorClient

#### Constructor

```python
StellaConnectorClient(base_url: str, timeout: float = 10.0)
```

- `base_url`: Base URL of the Stella Connector API (e.g., "http://localhost:8000")
- `timeout`: Request timeout in seconds (default: 10.0)

#### Methods

##### `invoke(input_data: Dict[str, Any]) -> Dict[str, Any]`

Invokes the LLM with the provided input data.

**Parameters:**
- `input_data`: Dictionary containing input parameters
  - `input`: The text prompt (required)
  - Additional parameters are passed to the LLM backend

**Returns:**
- Dictionary with `output` key containing the LLM response

**Raises:**
- `httpx.TimeoutException`: If request times out
- `httpx.HTTPStatusError`: For HTTP error responses
- `ValueError`: For invalid input data

### MockStellaConnectorClient

#### Constructor

```python
MockStellaConnectorClient()
```

#### Methods

##### `invoke(input_data: Dict[str, Any]) -> Dict[str, Any]`

Returns a mock response and records the invocation.

**Parameters:**
- `input_data`: Input data (recorded but not processed)

**Returns:**
- `{"output": "This is a mock response from Stella Connector."}`

#### Properties

##### `invocations: List[Dict[str, Any]]`

List of all input_data passed to `invoke()` calls. Useful for testing.

## Development

### Running Tests

```bash
# From repository root
just test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This SDK is part of the stella-connector project. See main repository for license information.
# Stella Connector Agent Notes

## Overview
- Minimal FastAPI template intended as a clean starting point for new services.
- Ships only the essentials: dependency injection shell, health route, and test/CI/Docker wiring.

## Design Philosophy
- Stay database-agnostic; add persistence only when the target project needs it.
- Use FastAPI's native dependency injection via `Depends()` for clean, testable code.
- Keep settings and dependencies explicit via `AppSettings`, `OllamaSettings`, `MLXSettings`, and factory pattern in `dependencies.py`.
- Maintain parity between local, Docker, and CI flows with a single source of truth (`just`, `uv`, `.env`).

## First Steps When Creating a Real API
1. Clone or copy the template and run `just setup` to install dependencies.
2. Configure the desired LLM backend via environment variables or `AppSettings`.
3. Extend `src/stl_conn/api/router.py` with domain routes using `Depends()` for dependency injection.
4. Register new LLM backends in `dependencies.py` by adding entries to `CLIENT_FACTORIES` and `MOCK_FACTORIES`.
5. Update `.env.example` and documentation to reflect new environment variables or external services.

## Key Files
- `src/stl_conn/dependencies.py`: FastAPI dependency providers using `Depends()` and factory pattern for client selection.
- `src/stl_conn/api/router.py`: API routes with dependency injection via `Depends()`.
- `src/stl_conn/api/main.py`: FastAPI app instantiation; attach new routers here.
- `tests/unit/test_dependencies.py`: tests for dependency injection system.
- `tests/intg/test_chat_invoke.py`: integration tests demonstrating `app.dependency_overrides` for mocking.
- `tests/`: unit/intg/e2e layout kept light so additional checks can drop in without restructuring.

## Tooling Snapshot
- `justfile`: run/lint/test/build tasks used locally and in CI.
- `uv.lock` + `pyproject.toml`: reproducible dependency graph; regenerate with `uv pip compile` when deps change.

## Dependency Injection Architecture

This project leverages **FastAPI's native dependency injection** for maximum clarity and testability:

### Benefits Over Manual Container Pattern
- **Declarative**: Dependencies are declared in function signatures using `Depends()`.
- **Testable**: Use `app.dependency_overrides` to swap dependencies during tests without environment variable manipulation.
- **Extensible**: Factory pattern in `dependencies.py` allows easy registration of new LLM backends.

### Adding New LLM Clients
1. Implement your client in `src/stl_conn/clients/`.
2. Add factory functions in `dependencies.py`:
   ```python
   def _create_your_client(settings: AppSettings) -> YourClient:
       return YourClient(YourSettings())

   CLIENT_FACTORIES["your_backend"] = _create_your_client
   MOCK_FACTORIES["your_backend"] = _create_mock_your_client
   ```
3. Routes automatically receive the correct client via `Depends(get_llm_client)`.

### Testing with Dependency Overrides
```python
def test_with_mock(app: FastAPI, async_client):
    def get_mock_client():
        return MockClient()

    app.dependency_overrides[get_llm_client] = get_mock_client
    # Make requests using async_client
    app.dependency_overrides.clear()
```

## LLM Parameter Forwarding

The `/api/chat/invoke` endpoint now forwards every key under `input_data` except `input` directly to the selected backend client.
Avoid filtering or renaming these keys in router logic—leave interpretation to the backend implementation. Tests in
`tests/intg/test_chat_invoke.py` assert this contract, so update them whenever the request schema changes.

## SDK Usage

The SDK (`nexus_sdk`) now ships LangChain-first ergonomics:

- `NexusClient`: HTTP client that accepts raw LangChain message objects or dict payloads and exposes `bind_tools()` for method chaining.
- `MockNexusClient`: Feature-parity mock that records serialized payloads and mirrors `bind_tools()`.
- `NexusClientProtocol`: Protocol for type checking.
- `LangChainResponse`: Structured response wrapper returned when `response_format="langchain"`.
- Strategy helpers (`SimpleResponseStrategy`, `SequenceResponseStrategy`, `PatternMatchingStrategy`, `CallbackResponseStrategy`, `LegacyKeywordStrategy`) let tests configure mock behaviour without editing shared code.

### Quick Examples

```python
import asyncio
from langchain_core.messages import HumanMessage
from nexus_sdk.stl_conn_client import NexusClient

async def main():
    client = NexusClient(
        base_url="http://localhost:8000",
        response_format="langchain",
    )

    # Messages can be LangChain objects; the client serializes them internally.
    result = await client.invoke([HumanMessage(content="Hello there!")])
    print(result.content)

    # Bind LangChain tools without extra wrappers.
    tool_enabled = client.bind_tools([{"name": "calculator"}])
    follow_up = await tool_enabled.invoke([{"role": "user", "content": "add 2 and 2"}])
    print(tool_enabled is client)  # bind_tools returns self

asyncio.run(main())
```

```python
import asyncio
from nexus_sdk.stl_conn_client import MockNexusClient

async def main():
    mock_client = MockNexusClient(response_format="langchain").bind_tools(
        [{"name": "search"}]
    )
    response = await mock_client.invoke([{"role": "user", "content": "search"}])
    print(mock_client.invocations[-1])  # Serialized payload incl. tools
    print(response.content)             # Deterministic mock JSON

asyncio.run(main())
```

Tests under `tests/sdk/` cover serialization, tool binding, and LangChain response normalization—extend these when evolving the request contract.

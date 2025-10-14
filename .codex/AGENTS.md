# stella-connector Agent Notes

## Overview
- Minimal FastAPI template intended as a clean starting point for new services.
- Ships only the essentials: dependency injection shell, health route, and test/CI/Docker wiring.

## Design Philosophy
- Stay database-agnostic; add persistence only when the target project needs it.
- Keep settings and dependencies explicit via `AppSettings`, `OllamaSettings`, `MLXSettings`, and `DependencyContainer`.
- Maintain parity between local, Docker, and CI flows with a single source of truth (`just`, `uv`, `.env`).

## First Steps When Creating a Real API
1. Clone or copy the template and run `just setup` to install dependencies.
2. Configure the desired LLM backend via environment variables or `AppSettings`.
3. Extend `src/stella_connector/api/router.py` with domain routes and register required dependencies in `container.py`.
4. Update `.env.example` and documentation to reflect new environment variables or external services.

## Key Files
- `src/stella_connector/container.py`: central place to wire settings and future services.
- `src/stella_connector/api/main.py`: FastAPI app instantiation; attach new routers here.
- `tests/`: unit/intg/e2e layout kept light so additional checks can drop in without restructuring.

## Tooling Snapshot
- `justfile`: run/lint/test/build tasks used locally and in CI.
- `uv.lock` + `pyproject.toml`: reproducible dependency graph; regenerate with `uv pip compile` when deps change.

## SDK Usage

This repository provides an SDK (`stella_connector_sdk`) for external repositories to interact with the stella-connector API. The SDK includes:

- `StellaClient`: HTTP client for making requests to the API
- `MockStellaClient`: Mock client for testing
- `StellaClientProtocol`: Protocol for type checking

To use the SDK in your project:

1. Install the SDK dependencies: `uv sync --group sdk`
2. Import and use the client:

```python
from stella_connector_sdk.stella_connector_client import StellaConnectorClient

client = StellaConnectorClient(base_url="http://localhost:8000")
response = client.invoke({"input": "Hello"})
```

For testing, use the mock:

```python
from stella_connector_sdk.stella_connector_client import MockStellaConnectorClient

mock_client = MockStellaConnectorClient()
response = mock_client.invoke({"input": "test"})
```

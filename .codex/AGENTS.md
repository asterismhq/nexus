# Nexus Agent Notes

## Overview
- Minimal FastAPI template intended as a clean starting point for new services.
- Ships only the essentials: dependency injection shell, health route, and test/CI/Docker wiring.

## Design Philosophy
- Stay database-agnostic; add persistence only when the target project needs it.
- Use FastAPI's native dependency injection via `Depends()` for clean, testable code.
- Keep settings and dependencies explicit via `NexusSettings`, `OllamaSettings`, `MLXSettings`, and factory pattern in `dependencies.py`.
- Maintain parity between local, Docker, and CI flows with a single source of truth (`just`, `uv`, `.env`).

## First Steps When Creating a Real API
1. Clone or copy the template and run `just setup` to install dependencies.
2. Configure the desired LLM backend via environment variables or `NexusSettings`.
3. Extend `src/nexus/api/router.py` with domain routes using `Depends()` for dependency injection.
4. Register new LLM backends in `dependencies.py` by adding entries to `CLIENT_FACTORIES` and `MOCK_FACTORIES`.
5. Update `.env.example` and documentation to reflect new environment variables or external services.

## Key Files
- `src/nexus/dependencies.py`: FastAPI dependency providers using `Depends()` and factory pattern for client selection.
- `src/nexus/api/router.py`: API routes with dependency injection via `Depends()`.
- `src/nexus/api/main.py`: FastAPI app instantiation; attach new routers here.
- `tests/unit/test_dependencies.py`: tests for dependency injection system.
- `tests/intg/test_chat_completions.py`: integration tests demonstrating `app.dependency_overrides` for mocking.
- `tests/`: unit/intg/e2e layout kept light so additional checks can drop in without restructuring.
- `sdk/nexus_sdk/nexus_client/`: SDK clients; `ollama_client.py`/`mlx_client.py` provide backend-specific facades used by the Python SDK.

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
1. Implement your client in `src/nexus/clients/`.
2. Add factory functions in `dependencies.py`:
   ```python
   def _create_your_client(settings: NexusSettings) -> YourClient:
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

The `/v1/chat/completions` endpoint forwards all top-level parameters other than `model` and `messages` directly to the
selected backend client. Streaming responses follow the OpenAI Chat Completions SSE contract, and non-streaming responses
emit the OpenAI-compatible `chat.completion` schema. Tests in `tests/intg/test_chat_completions.py` assert this contract, so
update them whenever the request schema changes.

## SDK Backend Selection

The Python SDK now exposes backend-aware entry points:

- `NexusOllamaClient` / `NexusMLXClient` live in `sdk/nexus_sdk/nexus_client/ollama_client.py` and `mlx_client.py` respectively and pin the backend hint automatically.
- `MockNexusClient` requires an explicit `backend` value (e.g., `"ollama"`, `"mlx"`) so tests mirror real routing and still supports per-call overrides.

# Nexus API

`Nexus` is a configurable FastAPI service that mediates LLM inference across pluggable backends. It provides a clean scaffold with dependency injection, environment-aware configuration, dockerisation, and a lightweight test suite so you can start new services quickly without dragging in domain-specific code.

## 🧱 Project Structure

```
├── src/
│   └── nexus/
│       ├── api/
│       │   ├── main.py          # FastAPI app factory and router registration
│       │   └── router.py        # API routes with dependency injection
│       ├── clients/             # Concrete LLM client implementations
│       ├── config/              # Pydantic settings modules
│       ├── dependencies.py      # FastAPI dependency providers (DI)
│       └── protocols/           # Shared interface definitions
├── tests/
│   ├── unit/
│   │   └── test_dependencies.py
│   ├── intg/
│   │   ├── test_api.py
│   │   └── test_chat_completions.py
│   └── e2e/
│       └── api/
│           └── test_health.py
├── justfile
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── entrypoint.sh
```

## 🔧 Configuration

Environment variables are loaded from `.env` (managed by `just setup`):

  * `NEXUS_APP_NAME` – application display name (default `nexus`).
  * `NEXUS_BIND_IP` / `NEXUS_BIND_PORT` – bind address when running under Docker (defaults `0.0.0.0:8000`).
  * `NEXUS_DEV_PORT` – port used by `just dev` (default `8000`).
  * `NEXUS_LLM_BACKEND` – active LLM backend (`ollama` or `mlx`).
  * `NEXUS_USE_MOCK_OLLAMA` / `NEXUS_USE_MOCK_MLX` – toggle mock clients for tests.
  * `NEXUS_OLLAMA_HOST`, `NEXUS_OLLAMA_MODEL` – Ollama connection details.
  * `NEXUS_MLX_HOST` – remote MLX server base URL (required for MLX backend).
  * `NEXUS_MLX_TIMEOUT` – timeout applied to remote MLX HTTP calls (seconds).
  * `NEXUS_MLX_MODEL` – identifier for the MLX model to load.

### Remote MLX Servers

  * Run an MLX-serving process (FastAPI wrapper, OpenAI-compatible bridge, etc.) on your host machine.
  * Configure Nexus with `NEXUS_LLM_BACKEND=mlx`, `NEXUS_MLX_HOST` to the server base URL (must support OpenAI-compatible `/v1/chat/completions` endpoint).
  * When running Nexus inside Docker on macOS, reach the host MLX server via `http://host.docker.internal:<port>`.
  * Verify connectivity with `curl "$NEXUS_MLX_HOST/v1/chat/completions" -H "Content-Type: application/json" -d '{"model":"your-model","messages":[{"role":"user","content":"Hello"}]}'`.

## 🔌 API Endpoints

The service provides the following endpoints:

### Interactive API Documentation

Visit `http://127.0.0.1:8000/docs` to access the automatically generated interactive API documentation powered by FastAPI and OpenAPI. This provides a user-friendly interface to explore and test the API endpoints, including detailed request/response schemas.

### Health Check

```http
GET /health -> {"status": "ok"}
```

### Chat Completions

```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "your-model-id",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms"}
  ],
  "temperature": 0.5,
  "max_tokens": 1024,
  "stream": false
}
```

Top-level parameters other than `model` and `messages` are forwarded verbatim to the active LLM backend, so you can tune
backend-specific options (e.g., `temperature`, `max_tokens`, `top_p`) without altering the API surface. Setting `stream: true`
switches the response to Server-Sent Events (SSE) that follow the OpenAI Chat Completions streaming format. Non-streaming
responses adopt the OpenAI-compatible schema (`chat.completion` object with `choices` and `usage`).

## 🏗️ Dependency Injection

This project uses **FastAPI's native dependency injection system** with the `Depends` mechanism:

  * **`src/nexus/dependencies.py`**: Centralized dependency providers using `Depends()`
  * **Factory Pattern**: Extensible client registration via `CLIENT_FACTORIES` and `MOCK_FACTORIES`
  * **Easy Testing**: Use `app.dependency_overrides` to inject mocks during testing

### Adding a New LLM Backend

1.  Create your client in `src/nexus/clients/`
2.  Register it in `dependencies.py`:
    ```python
    CLIENT_FACTORIES["your_backend"] = lambda settings: YourClient(...)
    MOCK_FACTORIES["your_backend"] = lambda settings: MockYourClient(...)
    ```
3.  Routes automatically use the new backend via dependency injection

Use this as a foundation for adding your own routes, dependencies, and persistence layers.

## SDK

This repository includes a Python SDK for interacting with the Nexus API. The SDK acts as a drop-in LangChain client, allowing you to pass LangChain message objects directly to the backend-specific clients (`NexusOllamaClient` / `NexusMLXClient`) and use `bind_tools()` to chain tool definitions in the LangChain style. Instantiate the class that matches your target backend and call `invoke()` to execute requests. Responses can be returned as `LangChainResponse` objects.

The `MockNexusClient` supports pluggable response strategies for testing, including:

  * **`SimpleResponseStrategy`**: For fixed responses.
  * **`SequenceResponseStrategy`**: For multi-turn workflows.
  * **`PatternMatchingStrategy`**: For regex-triggered responses.
  * **`CallbackResponseStrategy`**: For imperative control over mock content.

See [`sdk/README.md`](sdk/README.md) for detailed documentation, installation instructions, and usage examples.
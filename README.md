# Nexus API

`Nexus` is a configurable FastAPI service that mediates LLM inference across pluggable backends. It provides a clean scaffold with dependency injection, environment-aware configuration, dockerisation, and a lightweight test suite so you can start new services quickly without dragging in domain-specific code.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- (Optional) Docker and Docker Compose

### Local Setup

```shell
just setup
```

This installs dependencies with `uv` and creates a local `.env` file if one does not exist.

### Run the Application

```shell
just dev
```

The service will be available at `http://127.0.0.1:8000/health`.

### Run Tests and Linters

```shell
just test     # pytest test suite
just lint     # black --check and ruff
just format   # auto-format with black and ruff --fix
```

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
│   │   └── test_chat_invoke.py
│   └── e2e/
│       └── api/
│           └── test_health.py
├── justfile
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── entrypoint.sh
```

## 🐳 Docker Usage

Build and run the containerised service:

```shell
just build
docker compose up -d
```

The container listens on port `8000` and exposes `/health` for readiness checks.

## 🔧 Configuration

Environment variables are loaded from `.env` (managed by `just setup`):

- `NEXUS_APP_NAME` – application display name (default `nexus`).
- `NEXUS_BIND_IP` / `NEXUS_BIND_PORT` – bind address when running under Docker (defaults `0.0.0.0:8000`).
- `NEXUS_DEV_PORT` – port used by `just dev` (default `8000`).
- `NEXUS_LLM_BACKEND` – active LLM backend (`ollama` or `mlx`).
- `NEXUS_USE_MOCK_OLLAMA` / `NEXUS_USE_MOCK_MLX` – toggle mock clients for tests.
- `NEXUS_OLLAMA_HOST`, `NEXUS_OLLAMA_PORT`, `NEXUS_OLLAMA_MODEL` – Ollama connection details.
- `NEXUS_MLX_MODEL` – identifier for the MLX model to load.

## 🔌 API Endpoints

The service provides the following endpoints:

### Health Check
```http
GET /health -> {"status": "ok"}
```

### Chat Invocation
```http
POST /api/chat/invoke
Content-Type: application/json

{
  "input_data": {
    "input": "Explain quantum computing in simple terms",
    "temperature": 0.5,
    "max_tokens": 1024,
    "stream": false
  }
}
```

All keys nested under `input_data` other than `input` are transparently forwarded to the active LLM backend. This allows you to
leverage backend-specific options (e.g., `temperature`, `max_tokens`, `top_p`) without changing the API surface. Any new
parameters introduced by future backends are automatically passed through.

## 🏗️ Dependency Injection

This project uses **FastAPI's native dependency injection system** with the `Depends` mechanism:

- **`src/nexus/dependencies.py`**: Centralized dependency providers using `Depends()`
- **Factory Pattern**: Extensible client registration via `CLIENT_FACTORIES` and `MOCK_FACTORIES`
- **Easy Testing**: Use `app.dependency_overrides` to inject mocks during testing

### Adding a New LLM Backend

1. Create your client in `src/nexus/clients/`
2. Register it in `dependencies.py`:
   ```python
   CLIENT_FACTORIES["your_backend"] = lambda settings: YourClient(...)
   MOCK_FACTORIES["your_backend"] = lambda settings: MockYourClient(...)
   ```
3. Routes automatically use the new backend via dependency injection

Use this as a foundation for adding your own routes, dependencies, and persistence layers.

## SDK

This repository includes a Python SDK for interacting with the Nexus API. See [`sdk/README.md`](sdk/README.md) for detailed documentation, installation instructions, and usage examples.

### LangChain Support (v1.2.0)

The SDK now acts as a drop-in LangChain client:

- Pass LangChain message objects directly to `NexusClient.invoke()`—the SDK serializes them for you.
- Use `bind_tools()` on real or mock clients to chain tool definitions in the LangChain style.
- Responses created with `response_format="langchain"` continue to return `LangChainResponse` objects.

Applications that previously required bespoke adapters (e.g., `olm-d-rch`) can now rely on the SDK alone.

### Mock Client Strategies (v1.3.0)

`MockNexusClient` now supports pluggable response strategies so tests can declare exactly how the mock behaves without editing shared infrastructure. Built-in options include:

- `SimpleResponseStrategy` for fixed responses (optionally with predefined tool calls).
- `SequenceResponseStrategy` for multi-turn workflows.
- `PatternMatchingStrategy` for regex-triggered responses with optional fallbacks.
- `CallbackResponseStrategy` when you need imperative control over mock content.

Strategies can be provided when constructing the mock or swapped later via `set_strategy()` / `use_legacy_keyword_strategy()`. See `sdk/README.md` for usage examples.

# stella-connector-api

`stella-connector` is a configurable FastAPI service that mediates LLM inference across pluggable backends. It provides a clean scaffold with dependency injection, environment-aware configuration, dockerisation, and a lightweight test suite so you can start new services quickly without dragging in domain-specific code.

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
│   └── stella_connector/
│       ├── api/
│       │   ├── main.py          # FastAPI app factory and router registration
│       │   └── router.py        # Health check endpoint
│       ├── clients/             # Concrete LLM client implementations
│       ├── config/              # Pydantic settings modules
│       ├── container.py         # Dependency injection container
│       └── protocols/           # Shared interface definitions
├── tests/
│   ├── unit/
│   │   └── test_dependency_container.py
│   ├── intg/
│   │   └── test_health.py
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

- `STELLA_CONN_APP_NAME` – application display name (default `stella-connector`).
- `STELLA_CONN_BIND_IP` / `STELLA_CONN_BIND_PORT` – bind address when running under Docker (defaults `0.0.0.0:8000`).
- `STELLA_CONN_DEV_PORT` – port used by `just dev` (default `8000`).
- `STELLA_CONN_LLM_BACKEND` – active LLM backend (`ollama` or `mlx`).
- `STELLA_CONN_USE_MOCK_OLLAMA` / `STELLA_CONN_USE_MOCK_MLX` – toggle mock clients for tests.
- `STELLA_CONN_OLLAMA_HOST`, `STELLA_CONN_OLLAMA_PORT`, `STELLA_CONN_OLLAMA_MODEL` – Ollama connection details.
- `STELLA_CONN_MLX_MODEL` – identifier for the MLX model to load.

## ✅ Health Check

The template ships with a single health endpoint:

```http
GET /health -> {"status": "ok"}
```

Use this as a foundation for adding your own routes, dependencies, and persistence layers.

## SDK

This repository includes a Python SDK for interacting with the Stella Connector API. See [`sdk/README.md`](sdk/README.md) for detailed documentation, installation instructions, and usage examples.

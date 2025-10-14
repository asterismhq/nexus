# fapi-tmpl

`fapi-tmpl` is a minimal, database-independent FastAPI project template. It provides a clean scaffold with dependency injection, environment-aware configuration, dockerisation, and a lightweight test suite so you can start new services quickly without dragging in domain-specific code.

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
│   └── fapi_tmpl/
│       ├── api/
│       │   ├── main.py      # FastAPI app factory and router registration
│       │   └── router.py    # Health check endpoint
│       ├── config/
│       │   ├── __init__.py
│       │   └── app_settings.py  # Pydantic settings
│       └── container.py    # Minimal dependency container
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

- `FAPI_TMPL_APP_NAME` – application display name (default `fapi-tmpl`).
- `FAPI_TMPL_BIND_IP` / `FAPI_TMPL_BIND_PORT` – bind address when running under Docker (defaults `0.0.0.0:8000`).
- `FAPI_TMPL_DEV_PORT` – port used by `just dev` (default `8000`).

## ✅ Health Check

The template ships with a single health endpoint:

```http
GET /health -> {"status": "ok"}
```

Use this as a foundation for adding your own routes, dependencies, and persistence layers.

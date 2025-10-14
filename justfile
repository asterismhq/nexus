# ==============================================================================
# justfile for fapi-tmpl automation
# ==============================================================================

set dotenv-load

APP_NAME := env("FAPI_TMPL_APP_NAME", "fapi-tmpl")
HOST_IP := env("FAPI_TMPL_BIND_IP", "127.0.0.1")
DEV_PORT := env("FAPI_TMPL_DEV_PORT", "8000")

# default target
default: help

# Show available recipes
help:
    @echo "Usage: just [recipe]"
    @echo "Available recipes:"
    @just --list | tail -n +2 | awk '{printf "  \033[36m%-20s\033[0m %s\n", $1, substr($0, index($0, $2))}'

# ==============================================================================
# Environment Setup
# ==============================================================================

# Initialize project: install dependencies and create the .env file
setup:
    @echo "Installing python dependencies with uv..."
    @uv sync
    @echo "Creating environment file..."
    @if [ ! -f .env ] && [ -f .env.example ]; then \
        echo "Creating .env from .env.example..."; \
        cp .env.example .env; \
        echo "✅ Environment file created (.env)"; \
    else \
        echo ".env already exists. Skipping creation."; \
    fi

# ==============================================================================
# Development Environment Commands
# ==============================================================================

# Run local development server
dev:
    @echo "Starting local development server..."
    @uv run uvicorn fapi_tmpl.api.main:app --reload --host {{HOST_IP}} --port {{DEV_PORT}}

# Start production-like environment with Docker Compose
up:
    @docker compose up -d

# Stop Docker Compose environment
down:
    @docker compose down --remove-orphans

# Build Docker image
build:
    @docker build --target production --tag {{APP_NAME}}:latest .

# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Format code using Black and fix Ruff findings
format:
    @uv run black .
    @uv run ruff check . --fix

# Perform static code analysis
lint:
    @uv run black --check .
    @uv run ruff check .

# ==============================================================================
# TESTING
# ==============================================================================

# Run all tests
test: unit-test intg-test build-test e2e-test 
    @echo "✅ All tests passed!"

# Run unit tests locally (no external dependencies)
unit-test:
    @echo "🚀 Running unit tests (local)..."
    @uv run pytest tests/unit

# Run integration tests (requires Ollama)
intg-test:
    @echo "🚀 Running integration tests (requires Ollama)..."
    @uv run pytest tests/intg

# Run e2e tests (requires Ollama)
e2e-test:
    @echo "🚀 Running e2e tests (requires Ollama)..."
    @uv run pytest tests/e2e

# Build Docker image for testing without leaving artifacts
build-test:
    @echo "Building Docker image for testing (clean build)..."
    @TEMP_IMAGE_TAG=$(date +%s)-build-test; \
    docker build --target production --tag temp-build-test:$TEMP_IMAGE_TAG . && \
    echo "Build successful. Cleaning up temporary image..." && \
    docker rmi temp-build-test:$TEMP_IMAGE_TAG || true

# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and virtual environment
tidy:
    @echo "🧹 Tidying up project artifacts..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv .pytest_cache .ruff_cache
    @echo "✅ Cleanup completed"

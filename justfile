# ==============================================================================
# justfile for stella-connector automation
# ==============================================================================

set dotenv-load

APP_NAME := env("STELLA_CONN_APP_NAME", "stella-connector")
HOST_IP := env("STELLA_CONN_BIND_IP", "127.0.0.1")
DEV_PORT := env("STELLA_CONN_DEV_PORT", "8000")

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
    @uv run uvicorn stella_connector.api.main:app --reload --host {{HOST_IP}} --port {{DEV_PORT}}

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
test: 
    @just local-test
    @just docker-test
    @echo "✅ All tests passed!"

local-test: 
    @just unit-test
    @just intg-test
    @just sdk-test
    @echo "✅ All local tests passed!"

# Run unit tests
unit-test:
    @echo "🚀 Running unit tests..."
    @uv run pytest tests/unit

# Run SDK tests
sdk-test:
    @echo "🚀 Running SDK tests..."
    @uv run pytest tests/sdk

# Run integration tests
intg-test:
    @echo "🚀 Running integration tests..."
    @uv run pytest tests/intg

docker-test:
    @just build-test
    @just e2e-test
    @echo "✅ All Docker tests passed!"

# Build Docker image for testing without leaving artifacts
build-test:
    @echo "Building Docker image for testing..."
    @TEMP_IMAGE_TAG=$(date +%s)-build-test; \
    docker build --target production --tag temp-build-test:$TEMP_IMAGE_TAG . && \
    echo "Build successful. Cleaning up temporary image..." && \
    docker rmi temp-build-test:$TEMP_IMAGE_TAG || true

# Run e2e tests
e2e-test:
    @echo "🚀 Running e2e tests..."
    @uv run pytest tests/e2e

# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and virtual environment
clean:
    @echo "🧹 Tidying up project artifacts..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv .pytest_cache .ruff_cache
    @echo "✅ Cleanup completed"

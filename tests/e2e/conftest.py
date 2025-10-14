"""E2E fixtures that exercise the app inside Docker Compose."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest

PROJECT_NAME = os.getenv("STL_CONN_E2E_PROJECT", "stl-conn-e2e")
COMPOSE_FILE = os.getenv("STL_CONN_E2E_COMPOSE_FILE", "docker-compose.yml")
HOST_IP = os.getenv("STL_CONN_E2E_HOST", "127.0.0.1")
HOST_PORT = os.getenv("STL_CONN_E2E_PORT", "8100")


def _wait_for_health(url: str, timeout_seconds: int = 60) -> bool:
    """Poll the health endpoint until it responds with 2xx or timeout expires."""

    deadline = time.time() + timeout_seconds
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            response = httpx.get(url, timeout=5.0)
        except httpx.RequestError:
            response = None
        if response and 200 <= response.status_code < 300:
            return True
        time.sleep(2)
    return False


@pytest.fixture(scope="session", autouse=True)
def e2e_environment() -> Generator[None, None, None]:
    """Start the FastAPI app via Docker Compose for end-to-end tests."""

    compose_env = os.environ.copy()
    compose_env["STL_CONN_BIND_IP"] = HOST_IP
    compose_env["STL_CONN_BIND_PORT"] = HOST_PORT

    up_command = [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
        "-f",
        COMPOSE_FILE,
        "up",
        "-d",
        "--build",
    ]
    down_command = [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
        "-f",
        COMPOSE_FILE,
        "down",
        "-v",
    ]

    try:
        result = subprocess.run(
            up_command, check=False, capture_output=True, text=True, env=compose_env
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Failed to start docker compose services for E2E tests."
                f"\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        health_url = f"http://{compose_env['STL_CONN_BIND_IP']}:{compose_env['STL_CONN_BIND_PORT']}/health"
        if not _wait_for_health(health_url):
            logs_command = [
                "docker",
                "compose",
                "--project-name",
                PROJECT_NAME,
                "-f",
                COMPOSE_FILE,
                "logs",
            ]
            logs = subprocess.run(
                logs_command, capture_output=True, text=True, env=compose_env
            )
            raise RuntimeError(
                "Application failed health check after starting docker compose."
                f"\nHealth URL: {health_url}"
                f"\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                f"\nLOGS:\n{logs.stdout}\n{logs.stderr}"
            )
        yield
    finally:
        subprocess.run(down_command, capture_output=True, text=True, env=compose_env)


@pytest.fixture(scope="session")
def api_config() -> dict[str, str]:
    """Return connection information for the running container."""

    return {
        "base_url": f"http://{HOST_IP}:{HOST_PORT}",
        "health_url": f"http://{HOST_IP}:{HOST_PORT}/health",
    }


@pytest.fixture()
async def async_client(
    api_config: dict[str, str],
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client bound to the containerised FastAPI application."""

    async with httpx.AsyncClient(
        base_url=api_config["base_url"], timeout=30.0
    ) as client:
        yield client

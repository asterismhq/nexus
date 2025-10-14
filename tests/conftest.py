"""Shared pytest fixtures for the stella-connector project."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from stella_connector.api.main import app as fastapi_app


@pytest.fixture()
def app() -> FastAPI:
    """Return the FastAPI application under test."""
    return fastapi_app


@pytest.fixture()
async def async_client(app: FastAPI) -> AsyncClient:
    """Provide an async HTTP client for exercising the API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

"""Integration tests for the FastAPI application."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok(async_client):
    response = await async_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

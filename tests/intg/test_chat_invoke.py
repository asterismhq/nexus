"""Integration tests for the chat invoke endpoint."""

import pytest
from fastapi import FastAPI

from dev.mocks.mock_ollama_client import MockOllamaClient
from stella_connector.dependencies import get_llm_client


@pytest.mark.asyncio
async def test_invoke_chat_with_mock_client(app: FastAPI, async_client):
    """Test /api/chat/invoke endpoint with dependency override."""

    def get_mock_llm_client():
        return MockOllamaClient()

    # Override the dependency with a mock
    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        response = await async_client.post(
            "/api/chat/invoke",
            json={"input_data": {"input": "Hello, world!"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "output" in data
        # Mock returns a dict with model, message, and input
        assert isinstance(data["output"], (str, dict))
    finally:
        # Clean up the override
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invoke_chat_handles_dict_messages(app: FastAPI, async_client):
    """Test that invoke_chat correctly handles dict-formatted messages."""

    def get_mock_llm_client():
        return MockOllamaClient()

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        response = await async_client.post(
            "/api/chat/invoke",
            json={"input_data": {"input": "Test message"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "output" in data
    finally:
        app.dependency_overrides.clear()

"""Integration tests for the chat invoke endpoint."""

import pytest
from fastapi import FastAPI

from dev.mocks.mock_ollama_client import MockOllamaClient
from nexus.dependencies import get_llm_client


@pytest.mark.asyncio
async def test_invoke_chat_with_mock_client(app: FastAPI, async_client):
    """Test /api/chat/invoke endpoint with dependency override."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client():
        return mock_client

    # Override the dependency with a mock
    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        input_message = "Hello, world!"
        response = await async_client.post(
            "/api/chat/invoke",
            json={"input_data": {"input": input_message}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "output" in data
        # Mock returns a dict with model, message, and input
        assert isinstance(data["output"], (str, dict))

        # Assert that the mock client was called with the correct message
        assert len(mock_client.invocations) == 1
        received_messages = mock_client.invocations[0]["messages"]
        assert received_messages == [{"role": "user", "content": input_message}]
    finally:
        # Clean up the override
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invoke_chat_handles_dict_messages(app: FastAPI, async_client):
    """Test that invoke_chat correctly handles dict-formatted messages."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client():
        return mock_client

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        input_message = "Test message"
        response = await async_client.post(
            "/api/chat/invoke",
            json={"input_data": {"input": input_message}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "output" in data

        # Assert that the mock client was called with the correct message
        assert len(mock_client.invocations) == 1
        received_messages = mock_client.invocations[0]["messages"]
        assert received_messages == [{"role": "user", "content": input_message}]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_invoke_chat_forwards_extra_options(app: FastAPI, async_client):
    """Ensure backend-specific options are forwarded untouched."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client():
        return mock_client

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        payload = {
            "input_data": {
                "input": "Hello, settings!",
                "temperature": 0.3,
                "max_tokens": 256,
                "stream": False,
            }
        }

        response = await async_client.post("/api/chat/invoke", json=payload)

        assert response.status_code == 200
        assert len(mock_client.invocations) == 1
        invocation = mock_client.invocations[0]
        assert invocation["kwargs"] == {
            "temperature": 0.3,
            "max_tokens": 256,
            "stream": False,
        }
    finally:
        app.dependency_overrides.clear()

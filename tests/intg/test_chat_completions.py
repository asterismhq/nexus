"""Integration tests for the OpenAI-compatible chat completions endpoint."""

import json

import pytest
from fastapi import FastAPI

from dev.mocks.mock_ollama_client import MockOllamaClient
from nexus.dependencies import get_llm_client


@pytest.mark.asyncio
async def test_create_chat_completion_returns_openai_schema(app: FastAPI, async_client):
    """The /v1/chat/completions endpoint returns an OpenAI-compatible payload."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client() -> MockOllamaClient:
        return mock_client

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        payload = {
            "model": "mock-model",
            "messages": [{"role": "user", "content": "Hello, world!"}],
            "temperature": 0.2,
            "max_tokens": 32,
        }

        response = await async_client.post("/v1/chat/completions", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "chat.completion"
        assert data["model"] == "mock-model"
        assert isinstance(data["id"], str) and data["id"].startswith("chatcmpl-")
        assert isinstance(data["created"], int)
        assert len(data["choices"]) == 1
        choice = data["choices"][0]
        assert choice["finish_reason"] == "stop"
        assert choice["message"]["role"] == "assistant"
        assert "Mock Ollama response" in choice["message"]["content"]
        usage = data["usage"]
        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0

        assert len(mock_client.invocations) == 1
        invocation = mock_client.invocations[0]
        assert invocation["model"] == "mock-model"
        assert invocation["messages"] == payload["messages"]
        assert invocation["kwargs"]["temperature"] == 0.2
        assert invocation["kwargs"]["max_tokens"] == 32
        assert invocation["kwargs"]["top_p"] == 1.0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_chat_completion_streaming_sends_sse(app: FastAPI, async_client):
    """Streaming responses are emitted as SSE data chunks."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client() -> MockOllamaClient:
        return mock_client

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        payload = {
            "model": "mock-model",
            "messages": "Stream this",
            "stream": True,
        }

        async with async_client.stream(
            "POST", "/v1/chat/completions", json=payload
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            chunks = []
            async for line in response.aiter_lines():
                if not line:
                    continue
                assert line.startswith("data:")
                chunks.append(line)

        # The final chunk should be the [DONE] sentinel
        assert chunks[-1] == "data: [DONE]"

        data_chunks = [
            json.loads(chunk.split("data:", 1)[1].strip()) for chunk in chunks[:-1]
        ]
        assert any(
            "Mock Ollama response" in entry["choices"][0]["delta"].get("content", "")
            for entry in data_chunks
        )

        assert len(mock_client.invocations) == 1
        invocation = mock_client.invocations[0]
        assert invocation["stream"] is True
        assert invocation["model"] == "mock-model"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_chat_completion_forwards_backend_options(
    app: FastAPI, async_client
):
    """Backend options other than messages/model are forwarded verbatim."""

    mock_client = MockOllamaClient()

    def get_mock_llm_client() -> MockOllamaClient:
        return mock_client

    app.dependency_overrides[get_llm_client] = get_mock_llm_client

    try:
        payload = {
            "model": "mock-model",
            "messages": [{"role": "user", "content": "Check options"}],
            "temperature": 0.3,
            "max_tokens": 256,
            "top_p": 0.9,
        }

        response = await async_client.post("/v1/chat/completions", json=payload)
        assert response.status_code == 200

        assert len(mock_client.invocations) == 1
        invocation = mock_client.invocations[0]
        assert invocation["kwargs"] == {
            "temperature": 0.3,
            "max_tokens": 256,
            "top_p": 0.9,
        }
    finally:
        app.dependency_overrides.clear()

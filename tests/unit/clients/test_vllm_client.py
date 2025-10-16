"""Unit tests for the vLLM client implementation."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import httpx
import pytest
import respx

from nexus.clients.vllm_client import VLLMClient
from nexus.config.vllm_settings import VLLMSettings


@pytest.mark.asyncio
async def test_vllm_client_invoke_posts_payload_and_returns_json() -> None:
    """invoke should POST to the vLLM server and return JSON content."""

    settings = VLLMSettings(
        host="http://localhost:9999",
        model="base-model",
        api_key="secret-key",  # type: ignore[arg-type]
        temperature=0.1,
        max_tokens=64,
    )
    client = VLLMClient(settings)
    messages = [{"role": "user", "content": "Hi"}]
    response_payload = {"choices": [{"message": {"content": "Hello"}}]}

    with respx.mock(assert_all_called=True) as router:
        route = router.post("http://localhost:9999/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=response_payload)
        )

        result = await client.invoke(
            messages,
            model="override-model",
            top_p=0.9,
        )

    assert result == response_payload

    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer secret-key"
    body = json.loads(request.content)
    assert body["model"] == "override-model"
    assert body["messages"] == messages
    assert body["temperature"] == 0.1
    assert body["max_tokens"] == 64
    assert body["top_p"] == 0.9
    assert body["stream"] is False


@pytest.mark.asyncio
async def test_vllm_client_stream_yields_parsed_chunks(monkeypatch) -> None:
    """stream should yield decoded SSE chunks until the [DONE] sentinel."""

    settings = VLLMSettings(host="http://localhost:9999")
    client = VLLMClient(settings)
    messages = "Stream this"

    chunks = [
        "data: {\"choices\":[{\"delta\":{\"content\":\"hello\"}}]}\n\n",
        "data: {\"choices\":[{\"delta\":{}}]}\n\n",
        "data: [DONE]\n\n",
    ]

    class _MockResponse:
        status_code = 200

        def raise_for_status(self) -> None:  # pragma: no cover - simple
            return None

        async def aiter_lines(self) -> AsyncIterator[str]:
            for entry in chunks:
                yield entry.strip()

    @asynccontextmanager
    async def _mock_stream(*args: Any, **kwargs: Any):  # type: ignore[no-untyped-def]
        yield _MockResponse()

    class _FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[no-untyped-def]
            return None

        async def __aenter__(self) -> "_FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
            return None

        def stream(self, *args: Any, **kwargs: Any):  # type: ignore[no-untyped-def]
            return _mock_stream(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    stream = await client.stream(messages)
    results = []
    async for chunk in stream:
        results.append(chunk)

    assert results == [
        {"choices": [{"delta": {"content": "hello"}}]},
        {"choices": [{"delta": {}}]},
    ]

"""HTTP routes exposed by the nexus service."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, AsyncIterator, Dict, List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..dependencies import get_llm_client
from ..protocols.llm_client_protocol import LLMClientProtocol
from .models import (
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Usage,
)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    llm_client: LLMClientProtocol = Depends(get_llm_client),
) -> ChatCompletionResponse | StreamingResponse:
    """Create a chat completion compatible with the OpenAI Chat Completions API."""

    payload = request.model_dump(exclude_none=True)
    messages = _normalize_messages(payload.pop("messages"))
    model_name = payload.pop("model")
    stream_enabled = payload.pop("stream", False)
    backend_options = payload

    if stream_enabled:
        return StreamingResponse(
            _stream_chat_completions(
                llm_client,
                messages,
                model_name,
                backend_options,
            ),
            media_type="text/event-stream",
        )

    backend_response = await llm_client.invoke(
        messages,
        model=model_name,
        **backend_options,
    )
    return _build_chat_completion_response(backend_response, model_name)


def _normalize_messages(messages: Any) -> List[Dict[str, Any]]:
    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    return list(messages)


async def _stream_chat_completions(
    llm_client: LLMClientProtocol,
    messages: List[Dict[str, Any]],
    model_name: str,
    backend_options: Dict[str, Any],
) -> AsyncIterator[str]:
    response_id = _generate_response_id()
    created = int(time.time())

    def _format_chunk(chunk: Any) -> Dict[str, Any] | None:
        if chunk is None:
            return None
        if isinstance(chunk, dict):
            chunk.setdefault("id", response_id)
            chunk.setdefault("object", "chat.completion.chunk")
            chunk.setdefault("created", created)
            chunk.setdefault("model", model_name)
            return chunk
        content = str(chunk)
        return {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": content},
                    "finish_reason": None,
                }
            ],
        }

    stream_iterator = llm_client.stream(
        messages,
        model=model_name,
        **backend_options,
    )

    try:
        async for chunk in stream_iterator:
            formatted = _format_chunk(chunk)
            if formatted is None:
                continue
            yield _format_sse(formatted)
    finally:
        yield "data: [DONE]\n\n"


def _build_chat_completion_response(
    backend_response: Any,
    model_name: str,
) -> ChatCompletionResponse:
    response_id = _generate_response_id()
    created = int(time.time())

    choices = _extract_choices(backend_response)
    if not choices:
        message = ChatCompletionMessage(role="assistant", content=str(backend_response))
        choices = [
            ChatCompletionChoice(
                index=0,
                message=message,
                finish_reason="stop",
            )
        ]

    usage = _extract_usage(backend_response)

    return ChatCompletionResponse(
        id=response_id,
        created=created,
        model=model_name,
        choices=choices,
        usage=usage,
    )


def _extract_choices(backend_response: Any) -> List[ChatCompletionChoice]:
    if isinstance(backend_response, dict):
        raw_choices = backend_response.get("choices")
        if isinstance(raw_choices, list):
            parsed_choices: List[ChatCompletionChoice] = []
            for idx, choice in enumerate(raw_choices):
                if not isinstance(choice, dict):
                    continue
                message_payload = choice.get("message")
                if isinstance(message_payload, dict):
                    content = message_payload.get("content")
                    tool_calls = message_payload.get("tool_calls")
                    message = ChatCompletionMessage(
                        role=message_payload.get("role", "assistant"),
                        content=content,
                        tool_calls=tool_calls,
                    )
                else:
                    message = ChatCompletionMessage(
                        role="assistant",
                        content=str(message_payload),
                    )
                finish_reason = choice.get("finish_reason", "stop")
                parsed_choices.append(
                    ChatCompletionChoice(
                        index=choice.get("index", idx),
                        message=message,
                        finish_reason=finish_reason,
                    )
                )
            return parsed_choices

    if isinstance(backend_response, str):
        return [
            ChatCompletionChoice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant", content=backend_response
                ),
                finish_reason="stop",
            )
        ]

    return []


def _extract_usage(backend_response: Any) -> Usage:
    if isinstance(backend_response, dict):
        usage_data = backend_response.get("usage")
        if isinstance(usage_data, dict):
            try:
                return Usage(
                    prompt_tokens=int(usage_data.get("prompt_tokens") or 0),
                    completion_tokens=int(usage_data.get("completion_tokens") or 0),
                    total_tokens=int(usage_data.get("total_tokens") or 0),
                )
            except (ValueError, TypeError):
                pass  # Fall through to default usage
    return Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)


def _format_sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"


def _generate_response_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex}"

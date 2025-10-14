"""HTTP routes exposed by the stella-connector service."""

from typing import Any, Dict

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}


@router.post("/api/v1/chat/invoke")
async def invoke_chat(request: Request, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the configured LLM backend with the provided input."""
    container = request.app.state.container
    llm_client = container.provide_llm_client()

    # Extract messages from input_data - for now, assume input_data has "input" key
    messages = input_data.get("input", "")
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    response = await llm_client.invoke(messages)
    return {"output": response}


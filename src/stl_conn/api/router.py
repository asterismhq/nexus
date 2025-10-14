"""HTTP routes exposed by the stl-conn service."""

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends

from ..dependencies import get_llm_client
from ..protocols.llm_client_protocol import LLMClientProtocol

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}


@router.post("/api/chat/invoke")
async def invoke_chat(
    input_data: Dict[str, Any] = Body(...),
    llm_client: LLMClientProtocol = Depends(get_llm_client),
) -> Dict[str, Any]:
    """Invoke the configured LLM backend with the provided input."""
    request_payload = input_data.get("input_data", {})
    if not isinstance(request_payload, dict):
        request_payload = {}

    messages = request_payload.get("input", "")
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    backend_options = {
        key: value
        for key, value in request_payload.items()
        if key != "input"
    }

    response = await llm_client.invoke(messages, **backend_options)
    return {"output": response}

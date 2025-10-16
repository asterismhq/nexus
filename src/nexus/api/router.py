"""HTTP routes exposed by the nexus service."""

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException

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
    request_payload = input_data.get("input_data")
    if not isinstance(request_payload, dict):
        raise HTTPException(
            status_code=422,
            detail="Request body must contain an 'input_data' object.",
        )

    backend_options = request_payload.copy()
    messages = backend_options.pop("input", "")
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    response = await llm_client.invoke(messages, **backend_options)
    return {"output": response}

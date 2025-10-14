"""HTTP routes exposed by the stella-connector service."""

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
    # Extract messages from input_data - for now, assume input_data has "input" key
    messages = input_data.get("input", "")
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    response = await llm_client.invoke(messages)
    return {"output": response}

"""HTTP routes exposed by the nexus service."""

from fastapi import APIRouter, Depends

from ..dependencies import get_llm_client
from ..protocols.llm_client_protocol import LLMClientProtocol
from .models import ChatInvokeRequest, ChatInvokeResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}


@router.post("/api/chat/invoke")
async def invoke_chat(
    request: ChatInvokeRequest,
    llm_client: LLMClientProtocol = Depends(get_llm_client),
) -> ChatInvokeResponse:
    """Invoke the configured LLM backend with the provided input."""
    request_payload = request.input_data
    backend_options = request_payload.model_dump()
    messages = backend_options.pop("input", "")
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    response = await llm_client.invoke(messages, **backend_options)
    return ChatInvokeResponse(output=response)

from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field


class ChatInvokeRequestPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    input: Union[str, List[Dict[str, Any]]] = Field(
        ..., description="The input for the chat invocation"
    )
    temperature: float = Field(default=0.7, description="Temperature for the model")
    max_tokens: int = Field(
        default=None, description="Maximum number of tokens to generate"
    )
    stream: bool = Field(default=False, description="Whether to stream the response")


class ChatInvokeRequest(BaseModel):
    input_data: ChatInvokeRequestPayload


class ChatInvokeResponse(BaseModel):
    output: Any = Field(..., description="The output from the chat invocation")

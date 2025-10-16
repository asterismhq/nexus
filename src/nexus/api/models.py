from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ChatCompletionMessage(BaseModel):
    role: str = Field(..., description="Role of the message author")
    content: Optional[str] = Field(default=None, description="Content of the message")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Tool calls associated with the message"
    )


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(..., description="Identifier of the model to use")
    messages: Union[str, List[Dict[str, Any]]] = Field(
        ..., description="Conversation history provided to the model"
    )
    temperature: float = Field(
        default=0.7, description="Sampling temperature for the model"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum number of tokens to generate"
    )
    stream: bool = Field(default=False, description="Whether to stream the response")
    top_p: Optional[float] = Field(
        default=1.0, description="Nucleus sampling probability mass"
    )


class ChatCompletionChoice(BaseModel):
    index: int = Field(..., description="Position of this choice in the response")
    message: ChatCompletionMessage = Field(
        ..., description="Message content for this choice"
    )
    finish_reason: str = Field(
        ..., description="Reason the model stopped generating tokens"
    )


class Usage(BaseModel):
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(
        ..., description="Number of tokens in the completion"
    )
    total_tokens: int = Field(..., description="Total number of tokens consumed")


class ChatCompletionResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("chat.completion", description="Type of the returned object")
    created: int = Field(..., description="Unix timestamp for creation")
    model: str = Field(..., description="Model used to generate the response")
    choices: List[ChatCompletionChoice] = Field(
        ..., description="List of generated completion choices"
    )
    usage: Usage = Field(..., description="Token usage statistics for the request")

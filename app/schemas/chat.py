"""Chat-related schemas."""

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Supported chat message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single chat message."""

    role: MessageRole = Field(...)
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """Incoming chat request."""

    session_id: UUID = Field(default_factory=uuid4)
    message: str = Field(..., min_length=1, max_length=5000)
    history: list[ChatMessage] = Field(default_factory=list)
    use_knowledge_base: bool = Field(default=True)


class SourceReference(BaseModel):
    """A source snippet used in the answer."""

    content: str = Field(...)
    source: str = Field(...)
    score: float | None = Field(default=None)


class ChatResponse(BaseModel):
    """Chat response payload."""

    session_id: UUID = Field(...)
    answer: str = Field(...)
    sources: list[SourceReference] = Field(default_factory=list)
    mode: str = Field(default="rag")
    used_knowledge_base: bool = Field(default=True)
    notice: str | None = Field(default=None)

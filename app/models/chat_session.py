from datetime import datetime
import uuid
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class ChatSessionBase(SQLModel):
    title: str = Field(default="新会话", max_length=255)

class ChatSession(ChatSessionBase, table=True):
    __tablename__ = "chat_sessions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ChatMessageBase(SQLModel):
    role: str = Field(..., max_length=50)
    content: str
    sources_json: Optional[str] = Field(default=None)

class ChatMessage(ChatMessageBase, table=True):
    __tablename__ = "chat_messages"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="chat_sessions.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: ChatSession = Relationship(back_populates="messages")

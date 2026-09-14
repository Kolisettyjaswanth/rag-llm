from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


allowed_roles = Literal["user", "assistant", "system"]


class SessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class SessionRead(BaseModel):
    id: str
    user_id: str | None = None
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    role: allowed_roles
    content: str = Field(..., min_length=1, max_length=20000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message content cannot be empty")
        return value.strip()


class MessageRead(BaseModel):
    id: str
    session_id: str
    role: allowed_roles
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=20000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message cannot be empty")
        return value.strip()


class ChatSource(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    similarity: float
    guest: str | None = None
    title: str | None = None
    youtube_url: str | None = None
    video_id: str | None = None
    publish_date: str | None = None


class ArtifactResponse(BaseModel):
    type: Literal["html", "markdown"]
    content: str


class ChatResponse(BaseModel):
    message_id: str
    answer: str
    sources: list[ChatSource]
    skill: str
    route_reason: str
    artifact: ArtifactResponse | None = None

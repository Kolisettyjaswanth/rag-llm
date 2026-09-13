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

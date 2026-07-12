"""Pydantic schemas for users — API shapes."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """What a client SENDS to register (plaintext password — hashed before storage)."""

    email: EmailStr           # validates it's a real email format
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    """What the API RETURNS — note: NO password / hashed_password field. Ever."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime
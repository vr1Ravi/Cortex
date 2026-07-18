"""Chat schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class ChastResponse(BaseModel):
    reply: str
    model: str
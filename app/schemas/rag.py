"""RAG Q&A schemas."""

from pydantic import BaseModel, Field


class RagRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)

class Citation(BaseModel):
    document_id: int
    chunk_index: int

class RagResponse(BaseModel):
    answer: str
    citation: list[Citation]
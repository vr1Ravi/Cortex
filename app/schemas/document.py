"""Pydantic schemas for documents — the API shapes (what goes in/out over HTTP).
live in app/models/. Remember the schemas-vs-models distinction from 0.3.
"""

from pydantic import BaseModel, Field


class Document(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    word_count: int = Field(ge=0, default=0)
    tags: list[str] = []
    is_published: bool = False

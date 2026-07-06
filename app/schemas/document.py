"""Pydantic schemas for documents — the API shapes (what goes in/out over HTTP).
live in app/models/. Remember the schemas-vs-models distinction from 0.3.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """ Field shared by both input and output."""
    title: str = Field(min_length=1, max_length=2000)
    content: str = Field(min_length=1)
    tags: list[str] = []

class DocumentCreate(DocumentBase):
    """ What client SENDS to create a document (No server generated fields)"""

class DocumentResponse(DocumentBase):
    """ What the API RETURNS (adds server-generated field)"""

    id: int
    word_count: int
    is_publsihed: bool = False
    created_at: datetime


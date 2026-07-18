"""Schema for AI document analysis (structured output)."""

from pydantic import BaseModel


class DocumentAnalysis(BaseModel):
    summary: str
    tags: list[str]
    key_points: list[str]
    
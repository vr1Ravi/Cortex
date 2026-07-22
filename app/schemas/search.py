"""Search schemas."""


from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=50)



class SearchResult(BaseModel):
    document_id: int
    chunk_index: int
    content: str
    distance: float
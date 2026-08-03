"""Retrieve the most relevant chunks for a query (nearest-neighbor search)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.services.embeddings import embed_texts


async def retrieve_chunks(session: AsyncSession, query: str, owner_id: int, k: int = 5):
    """Return the k chunks (of THIS user's docs) most similar to the query, with distances."""
    [query_vec] = await embed_texts([query], task_type="RETRIEVAL_QUERY") # embed the question


    distance = DocumentChunk.embedding.cosine_distance(query_vec).label("distance")
    stmt = (
        select(DocumentChunk, distance)                            # Selects two cols
        .join(Document, DocumentChunk.document_id == Document.id) # to reach owner_id
        .where(Document.owner_id == owner_id)                    # only THIS user's chunks
        .order_by(distance)                                     # ASC → nearest first
        .limit(k)
    )
    result = await session.execute(stmt)
    return result.all() # list of (DocumentChunk, distance) rows

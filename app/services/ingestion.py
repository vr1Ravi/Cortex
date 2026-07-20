"""Ingest a document: chunk it, embed the chunks, store them."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts


async def insert_document(session: AsyncSession, document_id: int, content: str) -> int:
    # Re-ingest safe: wipe any existing chunks for this doc first.
    await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

    chunks = chunk_text(content)
    if not chunks:
        await session.commit()
        return 0
    
    vectors = await embed_texts(chunks) # one batched embed call for all chunks
    session.add_all([
        DocumentChunk(document_id=document_id, chunk_index=i, content=chunk, embedding=vec)
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ])
    await session.commit()
    return len(chunks)
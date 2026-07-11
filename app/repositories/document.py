"""Document repository — all database access for documents lives here.

Endpoints call these functions; they never touch SQLAlchemy directly.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


async def create(session: AsyncSession, data: DocumentCreate) -> Document:
    doc = Document(
        **data.model_dump(), # title, content, tags
        word_count=len(data.content.split())  # server-computed
    )
    session.add(doc)            # stage the INSERT
    await session.commit()      # write to DB
    await session.refresh(doc)  # reload → now doc.id and doc.created_at are populated
    return doc


async def get_by_id(session: AsyncSession, doc_id: int) -> Document | None:
    return await session.get(Document, doc_id)  # fetch by primary key, or None


async def list_all(session: AsyncSession, skip: int, limit: int) -> Sequence[Document]:
    result = await session.execute(
        select(Document).order_by(Document.id).offset(skip).limit(limit)
    )
    return result.scalars().all() # list of Document objects

async def update(session: AsyncSession, doc: Document, data: DocumentUpdate) -> Document:
    doc.title = data.title           # mutate the attached ORM object...
    doc.content = data.content
    doc.tags = data.tags
    doc.word_count = len(data.content.split())
    await session.commit()           # ...SQLAlchemy detects changes → UPDATE
    await session.refresh(doc)
    return doc

async def delete(session: AsyncSession, doc: Document) -> None:
    await session.delete(doc) # stage DELETE
    await session.commit()
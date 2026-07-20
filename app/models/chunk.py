"""ORM model for document chunks + their embeddings (pgvector)."""

from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column()   # order within the document
    content:  Mapped[str] = mapped_column(Text)  # the chunk text (to stuff into the prompt)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim)) # the vector!

    document: Mapped["Document"] = relationship()
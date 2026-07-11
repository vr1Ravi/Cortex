"""SQLAlchemy ORM model for documents — the DATABASE TABLE.

This is a *model* (DB shape), distinct from the Pydantic *schemas* in
app/schemas/document.py (API shapes). Same domain, different jobs.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(default=0)
    is_published: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list) 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # foreign key + relationship (the "many" side)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    owner: Mapped["User | None"] = relationship(back_populates="documents")
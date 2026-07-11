"""SQLAlchemy ORM model for documents — the DATABASE TABLE.

This is a *model* (DB shape), distinct from the Pydantic *schemas* in
app/schemas/document.py (API shapes). Same domain, different jobs.
"""


from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


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
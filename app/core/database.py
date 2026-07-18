"""Async database setup — engine, session factory, and the session dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>


# 1. ENGINE — manages the connection pool to Postgres. Created once, app-wide.
#    echo=True logs every SQL statement — great for learning, turn off later.
engine = create_async_engine(settings.database_url, echo=True)

# 2. SESSION FACTORY — makes new AsyncSession objects (one per request).
#    expire_on_commit=False keeps objects usable AFTER commit (needed so we can
#    still read an object's fields when building the HTTP response).
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# 3. BASE — parent class for all ORM models (we define models in 2.2).
class Base(DeclarativeBase):
    """Declarative base — all models inherit from this."""


# 4. THE SESSION DEPENDENCY — a `yield` dependency (the one previewed in 1.3!).
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """One session per request. Opens it, hands it to the endpoint, closes after."""
    async with async_session_maker() as session:
        yield session

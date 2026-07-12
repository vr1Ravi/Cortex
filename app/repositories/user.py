"""User repository — all DB access for users."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def get_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def list_all(session: AsyncSession, skip: int = 0, limit: int = 50) -> Sequence[User]:
    result = await session.execute(select(User).order_by(User.id).offset(skip).limit(limit))
    return result.scalars().all()
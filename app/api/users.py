"""User endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import EmailAlreadyExistsError
from app.models.user import User
from app.repositories import user as user_repo
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: SessionDep) -> User:
    if await user_repo.get_by_email(session, data.email):
        raise EmailAlreadyExistsError(data.email)
    return await user_repo.create(session, data)


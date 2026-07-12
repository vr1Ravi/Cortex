"""Shared auth dependencies."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user as user_repo

# Extracts the token from the "Authorization: Bearer <token>" header.
# tokenUrl points Swagger UI at the login route (enables the "Authorize" button in /docs).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: SessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token) # verifies signature + expiry
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:                   # tampered / expired / malformed
        raise credentials_exception
    user = await user_repo.get_by_id(session, int(user_id))
    if user is None:                         # token valid but user deleted
        raise credentials_exception
    return user

# Reusable alias: add `current_user: CurrentUser` to ANY endpoint to require login.
CurrentUser = Annotated[User, Depends(get_current_user)]

async def require_admin(current_user: CurrentUser) -> User:
    """Depends on get_current_user, then checks the role. 401 if not logged in, 403 if not admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

AdminUser = Annotated[User, Depends(require_admin)]
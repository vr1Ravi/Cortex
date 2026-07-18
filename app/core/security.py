"""Security utilities — password hashing (Argon2 via pwdlib)."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# .recommended() picks a strong modern algorithm (Argon2) with sensible settings.
_password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Salt is generated & embedded automatically."""
    return _password_hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash. Returns True/False."""
    return _password_hasher.verify(plain_password, hashed_password)


# SECRET_KEY signs token; keep it stable & secret


def create_access_token(subject: str) -> str:
    """Create a signed JWT whose `sub` claim is the user id."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)



def decode_access_token(toekn : str) -> dict:
    """Decode & verify a JWT. Raises jwt.PyJWTError if invalid/expired/tampered."""
    return jwt.decode(toekn, settings.secret_key, algorithms=[settings.algorithm])
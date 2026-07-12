"""Security utilities — password hashing (Argon2 via pwdlib)."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

# .recommended() picks a strong modern algorithm (Argon2) with sensible settings.
_password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Salt is generated & embedded automatically."""
    return _password_hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash. Returns True/False."""
    return _password_hasher.verify(plain_password, hashed_password)


# JWT config — hardcoded for now; moves to env-based settings in Phase 3.8.
SECRET_KEY = "dev-secret-change-me-in-production"   #signs token; keep it stable & secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(subject: str) -> str:
    """Create a signed JWT whose `sub` claim is the user id."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



def decode_access_token(toekn : str) -> dict:
    """Decode & verify a JWT. Raises jwt.PyJWTError if invalid/expired/tampered."""
    return jwt.decode(toekn, SECRET_KEY, algorithms=[ALGORITHM])
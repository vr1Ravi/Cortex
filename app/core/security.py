"""Security utilities — password hashing (Argon2 via pwdlib)."""

from pwdlib import PasswordHash

# .recommended() picks a strong modern algorithm (Argon2) with sensible settings.
_password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Salt is generated & embedded automatically."""
    return _password_hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash. Returns True/False."""
    return _password_hasher.verify(plain_password, hashed_password)
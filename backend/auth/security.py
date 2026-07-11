import hashlib

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    if not hashed_password:
        return False

    # Backward compatibility: existing users may still have unsalted SHA-256 hashes.
    if is_legacy_sha256_hash(hashed_password):
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

    return pwd_context.verify(plain_password, hashed_password)


def is_legacy_sha256_hash(value: str) -> bool:
    if len(value) != 64:
        return False
    return all(ch in "0123456789abcdef" for ch in value.lower())
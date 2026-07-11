from fastapi import APIRouter
from pydantic import BaseModel
from backend.auth.security import hash_password, verify_password, is_legacy_sha256_hash
from backend.database.db import SessionLocal
from backend.database.models import User


router = APIRouter(prefix="/auth", tags=["Auth"])

class UserRegister(BaseModel):
    company_id: int
    first_name: str
    last_name: str
    email: str
    password: str
    role: str

@router.post("/register")
def register_user(user: UserRegister):
    db = SessionLocal()

    new_user = User(
        company_id=user.company_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {
        "id": new_user.id,
        "company_id": new_user.company_id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "role": new_user.role
   }

class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
def login_user(user: UserLogin):
    db = SessionLocal()

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user is None:
        db.close()
        return {"error": "User not found"}

    if not verify_password(user.password, existing_user.hashed_password):
        db.close()
        return {"error": "Invalid password"}

    # Migrate old SHA-256 hashes to bcrypt after successful login.
    if is_legacy_sha256_hash(existing_user.hashed_password):
        existing_user.hashed_password = hash_password(user.password)
        db.commit()

    db.close()

    return {
        "message": "Login successful",
        "user_id": existing_user.id,
        "company_id": existing_user.company_id,
        "email": existing_user.email,
        "role": existing_user.role
   }

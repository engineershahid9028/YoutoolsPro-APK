from fastapi import APIRouter, HTTPException
from db import SessionLocal
from models import User
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
@router.post("/register")
def register(email: str, password: str):
    db = SessionLocal()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already exists")

    user = User(
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.close()

    return {"status": "registered"}
@router.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(user.id)

    db.close()

    return {
        "access_token": token,
        "is_premium": user.is_premium,
        "wallet": user.wallet
    }

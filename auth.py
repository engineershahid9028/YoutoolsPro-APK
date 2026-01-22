from fastapi import APIRouter, HTTPException
from db import SessionLocal
from models import User
from security import hash_password, verify_password, create_access_token
import secrets
from models import PasswordReset


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
@router.post("/forgot-password")
def forgot_password(email: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"status": "ok"}  # don't reveal users

    token = secrets.token_urlsafe(32)

    reset = PasswordReset(user_id=user.id, token=token)
    db.add(reset)
    db.commit()

    # TODO: send email later
    print("RESET LINK:", f"https://yourdomain/reset?token={token}")

    db.close()
    return {"status": "sent"}
@router.post("/reset-password")
def reset_password(token: str, new_password: str):
    db = SessionLocal()

    reset = db.query(PasswordReset).filter(PasswordReset.token == token).first()
    if not reset:
        raise HTTPException(400, "Invalid token")

    user = db.query(User).filter(User.id == reset.user_id).first()
    user.password_hash = hash_password(new_password)

    db.delete(reset)
    db.commit()
    db.close()

    return {"status": "password_updated"}
@router.post("/link-telegram")
def link_telegram(email: str, password: str, telegram_id: int):
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(400, "User not found")

    if not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid password")

    user.telegram_id = telegram_id
    db.commit()
    db.close()

    return {"status": "linked"}

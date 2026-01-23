from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import SessionLocal
from models import User, PasswordReset
from security import hash_password, verify_password, create_access_token
import secrets

router = APIRouter(prefix="/auth", tags=["Auth"])

# =========================
# REQUEST MODELS
# =========================

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class LinkTelegramRequest(BaseModel):
    email: str
    password: str
    telegram_id: int


# =========================
# AUTH ROUTES
# =========================

@router.post("/register")
def register(req: RegisterRequest):
    db = SessionLocal()

    # ✅ FIX: ignore rows where email IS NULL (telegram users)
    existing_user = (
        db.query(User)
        .filter(User.email == req.email)
        .filter(User.email.isnot(None))
        .first()
    )

    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {"status": "registered"}


@router.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()

    # ✅ Extra safety: only allow email users here
    user = (
        db.query(User)
        .filter(User.email == req.email)
        .filter(User.email.isnot(None))
        .first()
    )

    if not user or not user.password_hash:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, user.password_hash):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)

    db.close()

    return {
        "access_token": token,
        "is_premium": user.is_premium,
        "wallet": user.wallet
    }


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.email == req.email)
        .filter(User.email.isnot(None))
        .first()
    )

    if not user:
        db.close()
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
def reset_password(req: ResetPasswordRequest):
    db = SessionLocal()

    reset = db.query(PasswordReset).filter(PasswordReset.token == req.token).first()
    if not reset:
        db.close()
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(req.new_password)

    db.delete(reset)
    db.commit()
    db.close()

    return {"status": "password_updated"}


@router.post("/link-telegram")
def link_telegram(req: LinkTelegramRequest):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.email == req.email)
        .filter(User.email.isnot(None))
        .first()
    )

    if not user:
        db.close()
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(req.password, user.password_hash):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid password")

    user.telegram_id = req.telegram_id
    db.commit()
    db.close()

    return {"status": "linked"}
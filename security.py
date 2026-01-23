from passlib.context import CryptContext
import hashlib
import jwt
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================

SECRET_KEY = "CHANGE_THIS_TO_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# =========================
# PASSWORD HASHING
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def _normalize_password(password: str) -> str:
    """
    bcrypt has a hard 72-byte limit.
    We SHA-256 first to make it safe and stable.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    safe_password = _normalize_password(password)
    return pwd_context.hash(safe_password)

def verify_password(password: str, password_hash: str) -> bool:
    safe_password = _normalize_password(password)
    return pwd_context.verify(safe_password, password_hash)

# =========================
# JWT
# =========================

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),  # MUST be string
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
from fastapi import APIRouter, HTTPException
from db import SessionLocal
from models import User
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

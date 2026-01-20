from fastapi import FastAPI, Request
from pydantic import BaseModel
from telegram import Update

from bot import telegram_app
from db import init_db
from db_service import get_user_by_telegram_id, is_premium_user
from tools_engine import keyword_generator, seo_analyzer

app = FastAPI()


# ---------- Startup ----------

@app.on_event("startup")
async def startup():
    init_db()
    await telegram_app.initialize()
    print("✅ Database initialized")
    print("✅ Telegram bot initialized")


# ---------- Telegram Webhook ----------

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ---------- Android API ----------

class LoginRequest(BaseModel):
    telegram_id: int


class ToolRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"status": "YouToolsPro API is running"}


@app.post("/api/login")
def api_login(req: LoginRequest):
    user = get_user_by_telegram_id(req.telegram_id)

    if not user:
        return {"error": "User not found"}

    return {
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "is_premium": user.is_premium
    }


@app.get("/api/status/{telegram_id}")
def api_status(telegram_id: int):
    premium = is_premium_user(telegram_id)
    return {"is_premium": premium}


@app.post("/api/keyword")
def api_keyword(req: ToolRequest):
    result = keyword_generator(req.text)
    return {"result": result}


@app.post("/api/seo")
def api_seo(req: ToolRequest):
    result = seo_analyzer(req.text)
    return {"result": result}

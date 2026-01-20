from fastapi import FastAPI, Request
from pydantic import BaseModel
from telegram import Update

from bot import telegram_app
from db import init_db

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


# ---------- Android API (safe stub) ----------

class LoginRequest(BaseModel):
    telegram_id: int


class ToolRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"status": "YouToolsPro API is running"}


@app.post("/api/login")
def api_login(req: LoginRequest):
    # temporary stub until db_service is wired
    return {
        "telegram_id": req.telegram_id,
        "is_premium": False
    }


@app.get("/api/status/{telegram_id}")
def api_status(telegram_id: int):
    return {"is_premium": False}


@app.post("/api/keyword")
def api_keyword(req: ToolRequest):
    return {"result": f"Keyword result for: {req.text}"}


@app.post("/api/seo")
def api_seo(req: ToolRequest):
    return {"result": f"SEO result for: {req.text}"}

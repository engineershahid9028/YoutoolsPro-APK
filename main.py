from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from telegram import Update

from bot import telegram_app
from db import init_db


# =========================
# APP INIT
# =========================

app = FastAPI()


# =========================
# ENABLE CORS (for React / Web / Mobile)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all frontends (React, Android, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# STARTUP
# =========================

@app.on_event("startup")
async def startup():
    init_db()
    await telegram_app.initialize()
    print("✅ Database initialized")
    print("✅ Telegram bot initialized")


# =========================
# SERVE WEB DASHBOARD
# =========================

app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")

@app.get("/")
def home():
    return FileResponse("dashboard/index.html")


# =========================
# TELEGRAM WEBHOOK
# =========================

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# =========================
# API MODELS
# =========================

class LoginRequest(BaseModel):
    telegram_id: int


class ToolRequest(BaseModel):
    text: str


# =========================
# ANDROID / WEB API
# =========================

@app.post("/api/login")
def api_login(req: LoginRequest):
    # You can later connect this to real DB login
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
    class PaymentRequest(BaseModel):
    telegram_id: int
    txid: str


@app.post("/api/payment")
def api_payment(req: PaymentRequest):
    from binance_verify import verify_usdt_payment
    from db_service import set_premium, log_payment

    if not verify_usdt_payment(req.txid):
        log_payment(req.telegram_id, req.txid, 5, "failed")
        return {"status": "failed"}

    set_premium(req.telegram_id)
    log_payment(req.telegram_id, req.txid, 5, "success")

    return {"status": "success"}


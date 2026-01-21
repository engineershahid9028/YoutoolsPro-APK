from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from telegram import Update

from bot import telegram_app
from db import init_db
from binance_verify import verify_usdt_payment
from db_service import set_premium, log_payment


# =========================
# APP INIT
# =========================

app = FastAPI()


# =========================
# ENABLE CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # React, Android, etc.
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


class PaymentRequest(BaseModel):
    telegram_id: int
    txid: str


# =========================
# API ROUTES
# =========================

from db_service import get_or_create_user, is_premium

ADMIN_ID = 7575476523   # your admin id

@app.post("/api/login")
def api_login(req: LoginRequest):
    user = get_or_create_user(req.telegram_id)

    return {
        "telegram_id": req.telegram_id,
        "is_premium": is_premium(req.telegram_id),
        "is_admin": req.telegram_id == ADMIN_ID
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


# =========================
# PAYMENT API
# =========================

@app.post("/api/payment")
def api_payment(req: PaymentRequest):

    if not verify_usdt_payment(req.txid):
        log_payment(req.telegram_id, req.txid, 5, "failed")
        return {"status": "failed"}

    set_premium(req.telegram_id)
    log_payment(req.telegram_id, req.txid, 5, "success")

    return {"status": "success"}

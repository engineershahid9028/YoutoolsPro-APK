from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from telegram import Update
from sqlalchemy import text
from db import SessionLocal
from bot import telegram_app
from db import init_db
from binance_verify import verify_usdt_payment
from auth import router as auth_router
from models import DeviceToken
from db import SessionLocal


from db_service import (
    get_or_create_user,
    is_premium,
    set_premium,
    revoke_premium,
    ban_user,
    unban_user,
    log_payment,
    get_stats,
    get_all_users,
    get_all_payments,
)

# =========================
# CONFIG
# =========================

ADMIN_ID = 7575476523   # your admin telegram id

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

class AdminAction(BaseModel):
    admin_id: int
    user_id: int

# =========================
# AUTH API
# =========================

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
    return {
        "is_premium": is_premium(telegram_id),
        "is_admin": telegram_id == ADMIN_ID
    }
app.include_router(auth_router)
from db_service import create_ticket

@app.post("/api/support")
def api_support(req: SupportRequest):
    ticket = create_ticket(req.telegram_id, req.message)

    return {
        "status": "success",
        "ticket_id": ticket.id
    }

# =========================
# TOOL APIS
# =========================

@app.post("/api/keyword")
def api_keyword(req: ToolRequest):
    return {"result": f"Keyword result for: {req.text}"}

@app.post("/api/seo")
def api_seo(req: ToolRequest):
    return {"result": f"SEO result for: {req.text}"}

# =========================
# ADMIN APIS
# =========================

@app.get("/api/admin/stats/{admin_id}")
def admin_stats(admin_id: int):
    if admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    users, premium, wallets, total_requests = get_stats()

    return {
        "users": users,
        "premium": premium,
        "wallets": wallets,
        "requests": total_requests
    }

@app.get("/api/admin/users/{admin_id}")
def admin_users(admin_id: int):
    if admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    users = get_all_users()
    return [
        {
            "id": u.telegram_id,
            "premium": u.is_premium,
            "wallet": u.wallet,
            "banned": u.is_banned
        }
        for u in users
    ]

@app.get("/api/admin/payments/{admin_id}")
def admin_payments(admin_id: int):
    if admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    payments = get_all_payments()
    return [
        {
            "user": p.user_id,
            "amount": p.amount,
            "status": p.status,
            "txid": p.txid
        }
        for p in payments
    ]

@app.post("/api/admin/grant")
def admin_grant(req: AdminAction):
    if req.admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    set_premium(req.user_id)
    return {"status": "premium_granted"}

@app.post("/api/admin/revoke")
def admin_revoke(req: AdminAction):
    if req.admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    revoke_premium(req.user_id)
    return {"status": "premium_revoked"}

@app.post("/api/admin/ban")
def admin_ban(req: AdminAction):
    if req.admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    ban_user(req.user_id)
    return {"status": "banned"}

@app.post("/api/admin/unban")
def admin_unban(req: AdminAction):
    if req.admin_id != ADMIN_ID:
        return {"error": "Unauthorized"}

    unban_user(req.user_id)
    return {"status": "unbanned"}

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
# =========================
# ONE-TIME USER MIGRATION
# =========================

# =========================
# ONE-TIME USER MIGRATION
# =========================
# =========================
# PUSH NOTIFICATION DEVICE REGISTRATION
# =========================

class DeviceRegisterRequest(BaseModel):
    user_id: int
    token: str

@app.post("/api/register-device")
def register_device(req: DeviceRegisterRequest):
    db = SessionLocal()

    # Prevent duplicate token
    exists = db.query(DeviceToken).filter(DeviceToken.token == req.token).first()
    if not exists:
        device = DeviceToken(user_id=req.user_id, token=req.token)
        db.add(device)
        db.commit()

    db.close()
    return {"status": "device_registered"}

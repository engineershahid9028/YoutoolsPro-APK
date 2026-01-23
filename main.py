from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update

from bot import telegram_app
from db import init_db
from auth import router as auth_router
from tools_engine import router as tools_router
from db_service import set_premium

from pydantic import BaseModel

# =========================
# APP INIT
# =========================

app = FastAPI(title="YouToolsPro Backend")

# =========================
# MIDDLEWARE
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================

app.include_router(auth_router)
app.include_router(tools_router)

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
# TELEGRAM WEBHOOK
# =========================

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# =========================
# PROMO CODE
# =========================

class PromoRequest(BaseModel):
    telegram_id: int
    code: str

@app.post("/api/promo")
def apply_promo(req: PromoRequest):
    if req.code != "FREE100":
        raise HTTPException(status_code=400, detail="Invalid promo code")

    set_premium(req.telegram_id)
    return {"status": "success", "message": "Premium activated"}

# =========================
# HEALTH
# =========================

@app.get("/")
def home():
    return {"status": "YouToolsPro API running"}

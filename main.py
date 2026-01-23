from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# imports that do NOT use `app`
from tools_engine import router as tools_router
from auth import router as auth_router
from bot import telegram_app
from db import init_db

# =========================
# APP INIT (THIS MUST COME FIRST)
# =========================

app = FastAPI()

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
# ROUTERS (AFTER app EXISTS)
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

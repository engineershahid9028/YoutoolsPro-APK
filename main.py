from fastapi import FastAPI, Request
from telegram import Update
from bot import telegram_app
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    init_db()
    await telegram_app.initialize()
    print("✅ Telegram bot initialized")

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
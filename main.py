from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from telegram import Update
from bot import telegram_app
from db import init_db

app = FastAPI(title="YouToolsPro Backend")

# Serve frontend
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Startup
@app.on_event("startup")
async def startup():
    init_db()
    await telegram_app.initialize()
    print("✅ Telegram bot initialized")
    print("✅ YouToolsPro API is running")

# Telegram webhook
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# API routes
@app.get("/status")
def status():
    return {"service": "online", "bot": "online"}

@app.get("/tools")
def tools():
    return [
        {"name": "Video Downloader", "status": "online"},
        {"name": "Image Converter", "status": "online"},
        {"name": "Audio Extractor", "status": "online"}
    ]

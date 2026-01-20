from fastapi import FastAPI
from pydantic import BaseModel
import db_service  # your existing database logic
import premium     # premium checker
import seo_analyzer

app = FastAPI()

class LoginRequest(BaseModel):
    telegram_id: int

@app.post("/login")
def api_login(req: LoginRequest):
    user = db_service.get_user(req.telegram_id)
    if not user:
        return {"error": "user not found"}
    return {"user_id": user.id, "is_premium": user.is_premium}

@app.get("/status/{telegram_id}")
def api_status(telegram_id: int):
    return {"is_premium": premium.is_premium(telegram_id)}

@app.post("/seo_analyze")
def api_seo_analyze(text: str):
    return seo_analyzer.run(text)

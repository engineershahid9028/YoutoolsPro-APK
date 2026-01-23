import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from googleapiclient.discovery import build
from db_service import is_premium
from db_service import increment_tool_usage, get_today_usage


# ======================
# CONFIG
# ======================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

router = APIRouter(prefix="/api/tools", tags=["Tools"])

# ======================
# REQUEST MODELS
# ======================

class KeywordRequest(BaseModel):
    telegram_id: int
    keyword: str

# ======================
# AI CORE
# ======================

def ai_generate(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# ======================
# KEYWORD GENERATOR
# ======================

def keyword_generator(topic: str) -> str:
    prompt = f"""
Generate a premium SEO keyword report for YouTube.

Topic: {topic}

Format like this:

🔑 YOUTUBE KEYWORD RESEARCH REPORT
━━━━━━━━━━━━━━━━━━━━━━

📌 Topic:
{topic}

🔥 HIGH-RANKING KEYWORDS
List 20 keywords in bullet format

🎯 BEST LONG-TAIL KEYWORDS
List 10 long-tail keywords

🚀 RANKING STRATEGY
Give 5 SEO tips to rank faster

Make it clean, professional and premium looking.
"""
    return ai_generate(prompt)

# ======================
# API ROUTES
# ======================
@router.post("/keyword")
def keyword_tool(req: KeywordRequest):
    if not is_premium(req.telegram_id):
        raise HTTPException(status_code=403, detail="Premium required")

    used = get_today_usage(req.telegram_id)

    if used >= 10:
        raise HTTPException(
            status_code=429,
            detail="Daily tool limit reached"
        )

    increment_tool_usage(req.telegram_id)

    return {
        "success": True,
        "result": keyword_generator(req.keyword)
    }

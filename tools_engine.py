import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from googleapiclient.discovery import build
from db_service import is_premium

# ======================
# CONFIG
# ======================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

router = APIRouter(prefix="/api/tools", tags=["Tools"])

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
# TOOL LOGIC
# ======================

def keyword_generator(topic):
    prompt = f"""
Generate a premium SEO keyword report for YouTube.

Topic: {topic}

🔑 HIGH-RANKING KEYWORDS
🎯 LONG-TAIL KEYWORDS
🚀 SEO STRATEGY
"""
    return ai_generate(prompt)

# ======================
# API ROUTES
# ======================

@router.post("/keyword")
def keyword_tool(telegram_id: int, keyword: str):
    if not is_premium(telegram_id):
        raise HTTPException(status_code=403, detail="Premium required")

    return {
        "success": True,
        "result": keyword_generator(keyword)
    }

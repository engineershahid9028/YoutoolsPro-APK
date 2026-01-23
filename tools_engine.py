import os
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from googleapiclient.discovery import build
from security import get_current_user  # JWT dependency

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

def title_generator(topic):
    return ai_generate(f"Generate viral YouTube titles for: {topic}")

# ======================
# API ROUTES (JWT PROTECTED)
# ======================

@router.post("/keyword")
def keyword_tool(
    keyword: str,
    user=Depends(get_current_user)
):
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword required")

    return {
        "success": True,
        "result": keyword_generator(keyword)
    }

@router.post("/title")
def title_tool(
    topic: str,
    user=Depends(get_current_user)
):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    return {
        "success": True,
        "result": title_generator(topic)
    }

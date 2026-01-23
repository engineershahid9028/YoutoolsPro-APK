import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from googleapiclient.discovery import build
from db_service import is_premium

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

router = APIRouter(prefix="/api/tools", tags=["Tools"])


# ======================
# REQUEST MODEL
# ======================

class ToolRequest(BaseModel):
    telegram_id: int
    text: str


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
# TOOL FUNCTIONS (USED BY BOT)
# ======================

def keyword_generator(topic):
    return ai_generate(f"Generate a premium YouTube keyword research report for: {topic}")

def title_generator(topic):
    return ai_generate(f"Generate viral YouTube titles for: {topic}")

def seo_analyzer(video_url):
    return ai_generate(f"Analyze SEO for this YouTube video: {video_url}")

def competitor_spy(channel):
    return ai_generate(f"Analyze competitor YouTube channel: {channel}")

def viral_ideas(niche):
    return ai_generate(f"Generate viral YouTube ideas for niche: {niche}")

def content_generator(topic):
    return ai_generate(f"Create a YouTube video script for: {topic}")

def thumbnail_ai(topic):
    return ai_generate(f"Create a high CTR YouTube thumbnail idea for: {topic}")

def growth_mentor(niche):
    return ai_generate(f"Give a YouTube growth roadmap for niche: {niche}")

def rank_tracker(keyword):
    req = youtube.search().list(
        q=keyword,
        part="snippet",
        maxResults=5,
        type="video"
    )
    res = req.execute()
    return "\n".join(
        f"#{i+1} {v['snippet']['title']}"
        for i, v in enumerate(res["items"])
    )

def trending_videos(niche):
    req = youtube.search().list(
        q=niche,
        part="snippet",
        maxResults=5,
        order="viewCount",
        type="video"
    )
    res = req.execute()
    return "\n".join(
        f"🔥 {v['snippet']['title']}"
        for v in res["items"]
    )


# ======================
# PREMIUM GUARD (API)
# ======================

def premium_guard(telegram_id: int):
    if not is_premium(telegram_id):
        raise HTTPException(status_code=403, detail="Premium required")


# ======================
# API ENDPOINTS (WEB)
# ======================

@router.post("/keyword")
def api_keyword(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": keyword_generator(req.text)}

@router.post("/title")
def api_title(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": title_generator(req.text)}

@router.post("/seo")
def api_seo(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": seo_analyzer(req.text)}

@router.post("/rank")
def api_rank(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": rank_tracker(req.text)}

@router.post("/competitor")
def api_competitor(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": competitor_spy(req.text)}

@router.post("/viral")
def api_viral(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": viral_ideas(req.text)}

@router.post("/trending")
def api_trending(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": trending_videos(req.text)}

@router.post("/content")
def api_content(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": content_generator(req.text)}

@router.post("/thumbnail")
def api_thumbnail(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": thumbnail_ai(req.text)}

@router.post("/growth")
def api_growth(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": growth_mentor(req.text)}

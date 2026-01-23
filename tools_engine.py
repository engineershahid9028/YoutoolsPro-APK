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

class ToolRequest(BaseModel):
    telegram_id: int
    text: str

def ai_generate(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def premium_guard(telegram_id: int):
    if not is_premium(telegram_id):
        raise HTTPException(status_code=403, detail="Premium required")

@router.post("/keyword")
def keyword(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Generate a premium YouTube keyword research report for: {req.text}")}

@router.post("/title")
def title(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Generate viral YouTube titles for: {req.text}")}

@router.post("/seo")
def seo(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Analyze SEO for this YouTube video: {req.text}")}

@router.post("/competitor")
def competitor(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Analyze competitor YouTube channel: {req.text}")}

@router.post("/viral")
def viral(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Generate viral YouTube ideas for niche: {req.text}")}

@router.post("/content")
def content(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Create a YouTube video script for: {req.text}")}

@router.post("/thumbnail")
def thumbnail(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Create a high-CTR YouTube thumbnail idea for: {req.text}")}

@router.post("/growth")
def growth(req: ToolRequest):
    premium_guard(req.telegram_id)
    return {"result": ai_generate(f"Give a YouTube growth roadmap for niche: {req.text}")}

@router.post("/rank")
def rank(req: ToolRequest):
    premium_guard(req.telegram_id)
    reqq = youtube.search().list(q=req.text, part="snippet", maxResults=5, type="video")
    res = reqq.execute()
    return {"result": "\n".join(f"#{i+1} {v['snippet']['title']}" for i, v in enumerate(res["items"]))}

@router.post("/trending")
def trending(req: ToolRequest):
    premium_guard(req.telegram_id)
    reqq = youtube.search().list(q=req.text, part="snippet", maxResults=5, order="viewCount", type="video")
    res = reqq.execute()
    return {"result": "\n".join(f"🔥 {v['snippet']['title']}" for v in res["items"])}

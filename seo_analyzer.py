import re
import requests
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def analyze_video(video_url):
    video_id = extract_video_id(video_url)

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    if not data["items"]:
        return "❌ Invalid YouTube video link."

    video = data["items"][0]
    title = video["snippet"]["title"]
    description = video["snippet"]["description"]
    views = video["statistics"].get("viewCount", 0)

    score = 0
    tips = []

    if len(title) > 40:
        score += 30
    else:
        tips.append("Title is too short. Add keywords.")

    if len(description) > 200:
        score += 30
    else:
        tips.append("Description is too short. Add more SEO keywords.")

    if views > 1000:
        score += 20

    if "http" in description:
        score += 20

    report = f"""
🎬 Video SEO Report

Title: {title}
Views: {views}

SEO Score: {score}/100

Tips:
- {" | ".join(tips)}
"""

    return report


def extract_video_id(url):
    match = re.search(r"v=([^&]+)", url)
    if match:
        return match.group(1)
    return url.split("/")[-1]

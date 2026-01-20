import requests
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def spy_channel(channel_name):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": channel_name,
        "maxResults": 5,
        "type": "video",
        "order": "viewCount",
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    report = "🔍 Competitor Top Videos:\n\n"

    for item in data["items"]:
        title = item["snippet"]["title"]
        report += f"📺 {title}\n"

    return report

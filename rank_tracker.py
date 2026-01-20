import requests
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def track_rank(keyword, channel_name):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "maxResults": 10,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    results = []
    for i, item in enumerate(data["items"], start=1):
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]

        if channel_name.lower() in channel.lower():
            results.append(f"🎯 Rank {i}: {title}")

    if not results:
        return "❌ Your video is not ranking in top 10."

    return "\n".join(results)

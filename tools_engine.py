import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from googleapiclient.discovery import build
from security import token_required

# ======================
# CONFIG
# ======================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

tool_bp = Blueprint("tools", __name__)

# ======================
# AI CORE
# ======================

def ai_generate(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


# ======================
# KEYWORD GENERATOR
# ======================

def keyword_generator(topic):
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
# TITLE GENERATOR
# ======================

def title_generator(topic):
    prompt = f"""
Generate viral YouTube titles for this topic:

Topic: {topic}

Format like this:

🏷 VIRAL TITLE IDEAS
━━━━━━━━━━━━━━━━━━━━━━

🔥 High CTR Titles:
1. ...
2. ...
3. ...

💡 Emotional Titles:
1. ...
2. ...
3. ...

🚀 SEO Optimized Titles:
1. ...
2. ...
3. ...

Make them catchy, clickable and professional.
"""
    return ai_generate(prompt)


# ======================
# VIRAL IDEAS
# ======================

def viral_ideas(niche):
    prompt = f"""
Generate viral YouTube video ideas.

Niche: {niche}

Format like this:

🔥 VIRAL VIDEO IDEAS REPORT
━━━━━━━━━━━━━━━━━━━━━━

🎯 Trending Topics:
1. ...
2. ...
3. ...

🚀 High Engagement Ideas:
1. ...
2. ...
3. ...

💰 Monetizable Content Ideas:
1. ...
2. ...
3. ...

Make ideas highly clickable and trending.
"""
    return ai_generate(prompt)


# ======================
# CONTENT GENERATOR
# ======================

def content_generator(topic):
    prompt = f"""
Create a professional YouTube video script.

Topic: {topic}

Format like this:

📝 YOUTUBE VIDEO SCRIPT
━━━━━━━━━━━━━━━━━━━━━━

🎬 Hook (First 10 Seconds):
Write a powerful hook

📌 Introduction:
Short engaging intro

🎯 Main Content:
Structured points

🔥 Call To Action:
Strong CTA

Make it ready-to-record.
"""
    return ai_generate(prompt)


# ======================
# GROWTH MENTOR
# ======================

def growth_mentor(niche):
    prompt = f"""
You are a YouTube growth mentor.

Niche: {niche}

Format like this:

🚀 YOUTUBE GROWTH ROADMAP
━━━━━━━━━━━━━━━━━━━━━━

📈 Channel Growth Strategy
Bullet points

🎯 Content Strategy
Bullet points

🔥 Algorithm Hacks
Bullet points

💰 Monetization Strategy
Bullet points

Make it actionable and powerful.
"""
    return ai_generate(prompt)


# ======================
# SEO ANALYZER
# ======================

def seo_analyzer(video_url):
    prompt = f"""
You are a professional YouTube SEO expert.

Analyze this YouTube video URL and create a premium SEO audit report.

Video URL:
{video_url}

FORMAT LIKE THIS:

🏷 TITLE SEO SCORE — X/10
Short explanation

📝 DESCRIPTION SEO SCORE — X/10
Short explanation

🏷 TAG OPTIMIZATION SCORE — X/10
Short explanation

🚀 CTR OPTIMIZATION TIPS
Bullet points

📈 RANKING IMPROVEMENT STRATEGY
Bullet points

🔥 SUGGESTED SEO TITLE
One optimized title

📄 SUGGESTED SEO DESCRIPTION
Optimized description

🏷 BEST TAGS
Comma separated tags

Make it clean, premium and professional.
"""
    return ai_generate(prompt)


# ======================
# RANK TRACKER
# ======================

def rank_tracker(keyword):
    request_yt = youtube.search().list(
        q=keyword,
        part="snippet",
        maxResults=5,
        order="relevance",
        type="video"
    )
    response = request_yt.execute()

    results = []
    rank = 1
    for item in response["items"]:
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        results.append(f"#{rank} {title} — {channel}")
        rank += 1

    return "📊 YOUTUBE RANK TRACKER REPORT\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(results)


# ======================
# COMPETITOR SPY
# ======================

def competitor_spy(channel_name):
    prompt = f"""
Analyze YouTube channel: {channel_name}

Format like this:

🕵️ COMPETITOR CHANNEL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━

🔥 Best Performing Content
Bullet points

📈 Growth Strategy
Bullet points

🏷 Keyword Strategy
Bullet points

💰 Monetization Tips
Bullet points

Make it professional and insightful.
"""
    return ai_generate(prompt)


# ======================
# THUMBNAIL AI
# ======================

def thumbnail_ai(topic):
    prompt = f"""
Create a YouTube thumbnail concept.

Topic: {topic}

Format like this:

🖼 THUMBNAIL DESIGN BLUEPRINT
━━━━━━━━━━━━━━━━━━━━━━

🔥 Text on Thumbnail
🎨 Color Scheme
📸 Visual Idea
🤖 Midjourney Prompt

Make it high CTR focused.
"""
    return ai_generate(prompt)


# ======================
# TRENDING VIDEOS
# ======================

def trending_videos(niche):
    request_yt = youtube.search().list(
        q=niche,
        part="snippet",
        maxResults=5,
        order="viewCount",
        type="video"
    )
    response = request_yt.execute()

    results = []
    for item in response["items"]:
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        results.append(f"🔥 {title} — {channel}")

    return "📈 TRENDING VIDEOS REPORT\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(results)


# ======================
# API ROUTES (JWT PROTECTED)
# ======================

@tool_bp.route("/api/tools/keyword", methods=["POST"])
@token_required
def keyword_api():
    data = request.get_json()
    topic = data.get("keyword") or data.get("topic")

    if not topic:
        return jsonify({"error": "Keyword is required"}), 400

    return jsonify({
        "success": True,
        "result": keyword_generator(topic)
    })


@tool_bp.route("/api/tools/title", methods=["POST"])
@token_required
def title_api():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    return jsonify({
        "success": True,
        "result": title_generator(topic)
    })

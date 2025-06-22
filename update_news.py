
# Middle East War Monitor Bot (Web-Only Version)
# Removed email functionality – all updates are saved to JSON for dashboard viewing

import feedparser
import json
from datetime import datetime
import pytz
import re

# Configuration
KEYWORDS = ['bombing', 'missile', 'airstrike', 'ceasefire', 'escalation', 'Hezbollah', 'Hamas', 'Gaza', 'IDF', 'strike']
RSS_FEEDS = {
    'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'Fox News': 'http://feeds.foxnews.com/foxnews/latest',
    'Times of Israel': 'https://www.timesofisrael.com/feed/',
    'White House': 'https://www.whitehouse.gov/briefing-room/feed/',
    'Department of Defense': 'https://www.defense.gov/Newsroom/News/Transcripts/rss/'
}
COUNTRY_TAGS = {
    'Israel': ['IDF', 'Gaza', 'Tel Aviv'],
    'Iran': ['Iran', 'Tehran', 'Ayatollah'],
    'USA': ['US', 'America', 'Pentagon'],
    'Russia': ['Russia', 'Putin', 'Moscow'],
    'China': ['China', 'Beijing', 'PLA']
}

def analyze_video_url(url):
    if "deepfake" in url or "synthetic" in url:
        return "❗ AI-Generated"
    elif "enhanced" in url or "upscaled" in url:
        return "⚠️ Enhanced"
    else:
        return "✅ Real"

def strategic_outlook_logic(entry):
    discrepancies = []
    resolutions = []
    expert_flags = []

    content = entry.title.lower() + ' ' + entry.summary.lower()

    if 'trump' in content and 'israel' in content and ('support' in content or 'deny' in content):
        discrepancies.append("Potential mismatch in Trump’s statement vs military activity")

    if 'ceasefire' in content or 'negotiation' in content or 'un envoy' in content:
        resolutions.append("Potential diplomatic path to reduce casualties")

    if 'cia' in content or 'former state department' in content:
        if 'darpa' in content or 'lockheed' in content or 'raytheon' in content:
            expert_flags.append("Conflict of interest: expert tied to military supplier")

    return discrepancies, resolutions, expert_flags

def fetch_and_save():
    now = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M UTC')
    breaking_news = []
    structured_updates = {country: [] for country in COUNTRY_TAGS}
    video_reports = []
    strategic_notes = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            title = entry.title.lower()
            summary = entry.summary.lower() if 'summary' in entry else ''
            if any(kw in title or kw in summary for kw in KEYWORDS):
                matched_country = None
                for country, tags in COUNTRY_TAGS.items():
                    if any(tag.lower() in title or tag.lower() in summary for tag in tags):
                        matched_country = country
                        break

                d_notes, r_notes, e_notes = strategic_outlook_logic(entry)
                if d_notes or r_notes or e_notes:
                    note = f"{source}: {entry.title} | ⏱️ {now}"
                    if d_notes:
                        note += f"\n  Discrepancy: {d_notes[0]}"
                    if r_notes:
                        note += f"\n  Resolution Path: {r_notes[0]}"
                    if e_notes:
                        note += f"\n  Expert Note: {e_notes[0]}"
                    strategic_notes.append(note)

                video_url_match = re.search(r'(https?://\S+\.mp4|https?://\S+youtube\.com\S+)', entry.summary)
                if video_url_match:
                    video_url = video_url_match.group(1)
                    ai_tag = analyze_video_url(video_url)
                    video_summary = f"{source}: {entry.title}\n   Video: {video_url}\n   AI Tag: {ai_tag}\n   Reported: ⏱️ {now} 🟢"
                    video_reports.append(video_summary)

                entry_line = f"{source}: {entry.title} | ⏱️ {now} 🟢"
                if matched_country:
                    structured_updates[matched_country].append(entry_line)
                else:
                    breaking_news.append(entry_line)

    full_output = {
        "breaking_news": breaking_news,
        "structured_updates": structured_updates,
        "video_reports": video_reports,
        "strategic_notes": strategic_notes
    }

    with open("war_monitor_data.json", "w") as f:
        json.dump(full_output, f, indent=2)

if __name__ == '__main__':
    fetch_and_save()

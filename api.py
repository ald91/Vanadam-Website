import requests
from keys import GOOGLE_API_V3
import json

API_KEY = GOOGLE_API_V3
UPLOADS_PLAYLIST_ID = "UU4wPP_aSG0kR924KKE2OGWQ"  # Your channel's uploads playlist

videos = []
url = "https://www.googleapis.com/youtube/v3/playlistItems"
params = {
    "part": "snippet",
    "playlistId": UPLOADS_PLAYLIST_ID,
    "maxResults": 50,
    "key": API_KEY
}

while True:
    response = requests.get(url, params=params)
    data = response.json()
    
    for item in data.get("items", []):
        snippet = item["snippet"]
        video_id = snippet["resourceId"]["videoId"]
        title = snippet["title"]
        description = snippet.get("description", "")
        thumbnail = snippet.get("thumbnails", {})

        #thumb quality
        thumbnail_url = thumbnail.get("high", {})

        #format description
        rank = ["bronze", "silver", "gold", "platinum", "diamond", "onyx", "EHL", "HCS"]
        subrank = ["1", "2", "3", "4", "5"]
        mode = ["King of the hill", "KOTH", "slayer", "Oddball", "Assault", "CTF", "Capture the Flag"]
        #maps?
        
        video_rank = next((r for r in rank if r in description), "NO RANK") 
        video_subRank = next((r for r in subrank if r in description), "NO SUBDIVISION")
        video_gameMode = next((r for r in mode if r in description), "NO GAMEMODE")
        videos.append({"id": video_id, "title": title, "url": f"http://youtu.be/{video_id}", "thumbnail": thumbnail_url})

    if "nextPageToken" in data:
        params["pageToken"] = data["nextPageToken"]
    else:
        break

with open ('videos.json', 'w', encoding="utf-8") as file:
    json.dump(videos, file, indent=4, ensure_ascii=False)
import requests

API_KEY = Keys["API_KEY"]
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
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        videos.append({"id": video_id, "title": title})

    if "nextPageToken" in data:
        params["pageToken"] = data["nextPageToken"]
    else:
        break

print(f"Found {len(videos)} videos:")
for v in videos:
    print(v["title"], v["id"])
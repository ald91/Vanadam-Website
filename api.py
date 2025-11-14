#pagination loop error is causing max 50 records...

import requests
import json
import isodate
from pathlib import Path
import os

#internal imports
from keys import GOOGLE_API_V3
from HaloData import HI_MAPS


API_KEY = GOOGLE_API_V3
UPLOADS_PLAYLIST_ID = "UU4wPP_aSG0kR924KKE2OGWQ"  # Your channel's uploads playlist

def initVideoLibaray():
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

        #note -> python imports JSON as dict!!!
        data = response.json()
        
        for item in data.get("items", []):
            snippet = item["snippet"]

            #sometimes videos dont have IDs due to specific criteria... it's a little esoteric tbh.
            resource = snippet.get("resourceId")
            if not resource or "videoId" not in resource:
                continue
            
            video_id = resource["videoId"]
            description = snippet.get("description", "")
            thumbnail = snippet.get("thumbnails", {})
            thumbnail_url = thumbnail.get("high", {}).get("url", "")
            
            #format video title correctly / Vanadam videos contain section in the title split by |. 1st segment is always title. 2nd is generic | 3rd is usually season of upload

            raw_title = snippet["title"].split("|")
            title = raw_title[0].strip()

            #format description
            rank = ["b1", "b2", "b3", "b4", "b5", "s1", "s2", "s3", "s4", "s5", "g1", "g2", "g3", "g4", "g5", "p1", "p2", "p3", "p4", "p5", "p6", "d1", "d2", "d3", "d4", "d5", "d6" , "onyx", "EHL", "HCS"]
            mode = ["king of the hill", "koth", "slayer", "oddball", "assault", "ctf", "capture the flag"]
            #maps?
            
            description = description.lower()
    
            video_rank = next((vr for vr in rank if vr.lower() in description), "NO RANK DETECTED") 
            video_gameMode = next((gm for gm in mode if gm.lower() in description), "NO GAMEMODE DETECTED")
            video_map = next((m for m in HI_MAPS if m.lower() in description), "NO MAP DETECTED")

            #not yet implemented (unsure of logic)
            video_category = None

            videos.append({
                "id": video_id,
                "category": video_category, 
                "title": title,
                "rank": video_rank[0],
                "subrank": video_rank[1],
                "mode": video_gameMode,
                "map": video_map,
                "url": f"http://youtu.be/{video_id}",
                "thumbnail": thumbnail_url,
                #handled later
                "type": None,
                "duration seconds": None,
                "category": None})
        
        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            break

        print(f"Fetched {len(videos)} base records from playlist.")
        
        #handle remaining "None" fields as the Youtube API cant deliver all info needed in 1 call from "videos" playlist
        #this second request sends the ID of all videos as a list and gets back their duration to determine type

        #video type calculation because Youtube API sucks and 2 calls have to be made as playlist doesnt give video length
        #build dictionary of IDs from earlier
        video_lookup = {video["id"]: video for video in videos}
        
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails,liveStreamingDetails",
            "id": ",".join(video_lookup.keys()),
            "key": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()


        for item in data.get("items", []):
            vid_id = item["id"]
            video = video_lookup[vid_id] 
            description = item.get("snippet", {}).get("description", "").lower()


            #duration checks
            if "contentDetails" in item:
                duration_ISO = item["contentDetails"]["duration"]
                video["duration seconds"] = int(isodate.parse_duration(duration_ISO).total_seconds())
            else:
                video["duration seconds"] = None

            #check if the video is or was a livestream, livestreams that have happened always have a finish time in the snippet[""]
            if "this was a livestream" in description.lower():
                video["video type"] = "livestream"
                video["rank"] = None
                video["subrank"] = None

            elif type( video["duration seconds"]) == int and  video["duration seconds"] <= 60:
                video["video type"] = "shortform"

            elif type( video["duration seconds"]) == int and  video["duration seconds"] >= 61:
                video["video type"] = "longform"
            
            else:
                video["video type"] = None

        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            break



    with open ('videos.json', 'w', encoding="utf-8") as file:
        json.dump(videos, file, indent=4, ensure_ascii=False)

def initThumnailLibrary():
    with open("videos.json", "r", encoding="utf-8") as file:
        videos = json.load(file)

    os.makedirs("static/assets/videothumbs", exist_ok=True)
    os.makedirs("errors", exist_ok=True)
    errornails = []

    for video in videos:
        thumb_url = video.get("thumbnail")
        video_id = video.get("id")

        if thumb_url:
            response = requests.get(thumb_url)
            if response.ok:
                thumbnail_path = f"static/assets/videothumbs/{video_id}.jpeg"
                
                if os.path.exists(thumbnail_path):
                    print(f"thumbnail for {video_id} already exists, skipping.")
                    continue
                
                with open(f"assets/thumbnails/{video_id}.jpeg", "wb") as file:
                    file.write(response.content)
            
            else:
                print(f"failed to get thumbail for video: {video_id}")
                errornails.append(video_id)
                with open(f"assets/errorlogs/thumbnailerrors.txt", "wb") as file:
                    file.write("/n".join(errornails))

initVideoLibaray()
print ("successfully initialised Video Library JSON")

#initThumnailLibrary()
print ("successfully initialised thumbnail Library JPEGS")
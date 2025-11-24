#pagination loop error is causing max 50 records...

import requests
import json
import isodate
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

#internal imports
from extensions import app
from HaloData import HALO_INFINITE_DATA
from db import *

# constants
KEY = os.getenv("GOOGLE_API_KEY", "ERROR")
DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, "API_SCRAPE.JSON")
UPLOADS_PLAYLIST_ID = "UU4wPP_aSG0kR924KKE2OGWQ"  # Your channel's uploads playlist

#global list for API pulls
extracted = []

#helper functions
def Calculate_Video_MMR(videoData):
    rank = ["Bronze 1", "Bronze 2", "Bronze 3", "Bronze 4", "Bronze 5", "Silver 1", "Silver 2", "Silver 3", "Silver 4", "Silver 5", "Gold 1", "Gold 2", "Gold 3", "Gold 4", "Gold 5", "Platinum 1", "Platinum 2", "Platinum 3", "Platinum 4", "Platinum 5", "Platinum 6", "Diamond 1", "Diamond 2", "Diamond 3", "Diamond 4", "Diamond 5", "Diamond 6","b1", "b2", "b3", "b4", "b5", "s1", "s2", "s3", "s4", "s5", "g1", "g2", "g3", "g4", "g5", "p1", "p2", "p3", "p4", "p5", "p6", "d1", "d2", "d3", "d4", "d5", "d6" , "onyx", "EHL", "HCS"]

    rankStandardize = { 
    "b1": "Bronze 1",
    "b2": "Bronze 2",
    "b3": "Bronze 3",
    "b4": "Bronze 4",
    "b5": "Bronze 5",
    "s1": "Silver 1",
    "s2": "Silver 2",
    "s3": "Silver 3",
    "s4": "Silver 4",
    "s5": "Silver 5",
    "g1": "Gold 1",
    "g2": "Gold 2",
    "g3": "Gold 3",
    "g4": "Gold 4",
    "g5": "Gold 5",
    "p1": "Platinum 1",
    "p2": "Platinum 2",
    "p3": "Platinum 3",
    "p4": "Platinum 4",
    "p5": "Platinum 5",
    "p6": "Platinum 6",
    "d1": "Diamond 1",
    "d2": "Diamond 2",
    "d3": "Diamond 3",
    "d4": "Diamond 4",
    "d5": "Diamond 5",
    "d6": "Diamond 6",
    "onyx": "Onyx",
    "ehl": "EHL",
    "hcs": "HCS"
    }

    infiniteCSR = {
        "Bronze 1": 0,
        "Bronze 2": 60,
        "Bronze 3": 120,
        "Bronze 4": 180,
        "Bronze 5": 240,

        "Silver 1": 300,
        "Silver 2": 360,
        "Silver 3": 420,
        "Silver 4": 480,
        "Silver 5": 540,

        "Gold 1": 600,
        "Gold 2": 660,
        "Gold 3": 720,
        "Gold 4": 780,
        "Gold 5": 840,

        "Platinum 1": 900,
        "Platinum 2": 960,
        "Platinum 3": 1020,
        "Platinum 4": 1080,
        "Platinum 5": 1140,
        "Platinum 6": 1200,

        "Diamond 1": 1200,
        "Diamond 2": 1260,
        "Diamond 3": 1320,
        "Diamond 4": 1380,
        "Diamond 5": 1440,
        "Diamond 6": 1500,

        "Onyx": 1500
    }

    Dtext = videoData.lower()

    for subrank in rank: 
        if subrank.lower() in Dtext:
            subrank = rankStandardize.get(subrank, subrank)   
            subrank = infiniteCSR.get(subrank, subrank)        
            return subrank

    return None

def Calculate_Video_Map(videoDesc, videoTitle):
    maps = HALO_INFINITE_DATA["Maps"].keys()
    Dtext = videoDesc.lower()
    Ttext = videoTitle.lower()

    for map_name in maps:
        if map_name.lower() in Dtext or map_name.lower() in Ttext:
            return map_name
        
    return None

def Calculate_Video_Gamemode(videoDesc, videoTitle):
    modes = ["king of the hill", "koth", "slayer", "oddball", "assault", "ctf", "capture the flag"]
    Dtext = videoDesc.lower()
    Ttext = videoTitle.lower()

    for gamemode in modes:
        if gamemode in Dtext or gamemode in Ttext:
            return gamemode.capitalize()

    return None

def Calculate_Video_Type(description, duration):
    #only allow these types "Shortform", "Livestream", "Longform"

    if duration == 0:
        return "Livestream" #it hasnt happend yet
    
    elif duration <= 60 and duration > 0:
        return "Shortform"

    elif duration >= 61 and "This was a Livestream" in description:
        return "Livestream"
    
    else:
        return "Longform"
    
def Calculate_Video_Category(videoCsr, videoMap, videoMode, videoType,videoDesc):
    videoCategory = [ "vod review", "map guide", "reaction", "livesteam", "other", "pro breakdown", "stream highlight", "discussion", "macro tips"]
    Dtext = videoDesc.lower()

    if videoType == "Livestream":
        return "Livestream"

    for category in videoCategory:
        if category in Dtext:
            return category.capitalize()

#build video dump file for other functions to use -- prevents API call spam
def Google_API_V3_PULL_Video_Info(extracted):
        
    try:
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": UPLOADS_PLAYLIST_ID,
            "maxResults": 50,
            "key": KEY
        }

        #obtains basic video information
        while True:
            
            #get this set of max 50 of n videos
            response = requests.get(url, params=params)
            data = response.json()

            next_page_token = data.get("nextPageToken")

            if next_page_token:
                params["pageToken"] = next_page_token
            else:
                params.pop("pageToken", None)
        

            videos = data.get("items")

            for video in videos:
                extracted.append(video)

            if next_page_token:
                params["pageToken"] = next_page_token
                print(f"Fetched {len(extracted)} videos so far...")
            else:
                break

    except Exception as e:
        print(f"API contact error with API key: {KEY}, {e}")

    return extracted

#inputted data must be a list containing API call with video IDs (should be extrated, which is type = list)
def Google_API_V3_Pull_Durations(extracted):
    try:

        #obtains video duration information
        video_duration_lookup_ids = []
        next_page_token = None

        for item in extracted:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_duration_lookup_ids.append(video_id)
        
        print(f"got {len(video_duration_lookup_ids)} video Ids")
        
        for i in range(0,len(video_duration_lookup_ids),50):
            chunk = video_duration_lookup_ids[i:i+50]
            
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,contentDetails,liveStreamingDetails",
                "id": ",".join(chunk),
                "key": KEY
            }
            
            while True:

                if next_page_token:
                    params["pageToken"] = next_page_token
                else:
                    params.pop("pageToken", None)

                response = requests.get(url, params=params)
                data = response.json()

                for item in data["items"]:
                        cross_ref_video_id = item["id"]
                        duration_ISO = item["contentDetails"]["duration"]
                        
                        video = next((video for video in extracted if video["snippet"]["resourceId"]["videoId"] == cross_ref_video_id ))
                        video["snippet"]["duration"] = int(isodate.parse_duration(duration_ISO).total_seconds())

                if next_page_token:
                    params["pageToken"] = next_page_token
                else:
                    break
    
    except Exception as e:
        print(f"API contact or list editing error, {e}")

    return extracted

#cleans unwanted data from the list
def Google_API_V3_Clean_Data(extracted):
    for video in extracted:
        video.pop("kind")
        video.pop("id")

        inner_info = video["snippet"]
        thumbnails = inner_info["thumbnails"]

        video["videoId"] = inner_info["resourceId"]["videoId"]
        video["title"] = inner_info["title"]
        video["duration"] = inner_info["duration"]
        video["publishedAt"] = inner_info["publishedAt"]
        video["description"] = inner_info["description"]
        video["thumbnails"] = inner_info["thumbnails"] = {
                                                            "default" : thumbnails["default"]["url"],
                                                            "standard" : thumbnails["standard"]["url"],
                                                            "medium" : thumbnails["medium"]["url"],
                                                            "high" : thumbnails["high"]["url"],
                                                            "maxres" : thumbnails["maxres"]["url"],
                                                         }
        video["kind"] = inner_info["resourceId"]["kind"]
        video["channelId"] = inner_info["channelId"]
        
        #remove extrated useless info
        video.pop("snippet", None)

    return extracted

#write completed list "extrated" to videoDump.Json
def Google_API_V3_Write_JSON(data, where):

    try:
        if where == "clean":
            with open ('videoDump.json', 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        
        elif where == "dbReady":
            with open ('videoDbReady.json', 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"there was a problem writing the file", {e})

    return

#loads file and modifys values stored to be compatible with db system and website
def Google_API_V3_Modify_Values():
    modified = []
    with open ('videoDump.Json', 'r', encoding="utf-8") as file:
            extracted = json.load(file)

    for video in extracted:
    #existing keys
        description = video.get("description")
        duration = video.get("duration")

        #title formatting
        videoTitle = video["title"].split("|")
        videoTitle = videoTitle[0].strip()
        video["title"] = videoTitle

        #new keys  
        video["csr"] = Calculate_Video_MMR(description)
        video["map"] = Calculate_Video_Map(description, videoTitle)
        video["gameMode"] = Calculate_Video_Gamemode(description, videoTitle)
        video["type"] = Calculate_Video_Type(description, duration)
        video["category"] = Calculate_Video_Category(video["csr"], video["map"], video["gameMode"], video["type"], description)

        # Modifications to keep typing consistant
        if video["type"] == "Livestream":
            video["csr"] = None

        if video["category"] == "Other":
            video["csr"] == None
            video["map"] == None
            video["gameMode"] == None

        if video["gameMode"] == None:
            video["csr"] == None
            

        
        modified.append(video)

    return modified

#finally, load in the thumbnails of all assets listed on the site
def Google_API_V3_Write_Thumbnails():
    with open("videoDbReady.json", "r", encoding="utf-8") as file:
        videos = json.load(file)

    os.makedirs("static/assets/videothumbs", exist_ok=True)
    os.makedirs("errors", exist_ok=True)
    errornails = []

    for video in videos:
        thumb_url = video["thumbnails"]["maxres"]
        video_id = video["videoId"]

        if thumb_url:
            response = requests.get(thumb_url)
            if response.ok:
                thumbnail_path = f"static/assets/videothumbs/{video_id}.jpeg"
                
                if os.path.exists(thumbnail_path):
                    print(f"thumbnail for {video_id} already exists, skipping.")
                    continue
                
                with open(f"static/assets/videothumbs/{video_id}.jpeg", "wb") as file:
                    file.write(response.content)
            
            else:
                print(f"failed to get thumbail for video: {video_id}")
                errornails.append(video_id)
                with open("errors/thumbnailerrors.txt", "wb") as file:
                    file.write("/n".join(errornails))

def Commit_to_DB():
    with open("videoDbReady.json", "r", encoding="utf-8") as file:
        videos = json.load(file)

    db = get_database()
    cur = db.cursor()

    for video in videos:
        vidID = video["videoId"]
        title = video["title"]
        duration = video["duration"]
        published = video["publishedAt"]
        description = video["description"]

        thumbnailsdefault = video["thumbnails"]["default"]
        thumbnailsmedium = video["thumbnails"]["medium"]
        thumbnailshigh = video["thumbnails"]["high"]
        thumbnailsmax = video["thumbnails"]["maxres"]

        kind = video["kind"]
        channelid = video["channelId"] 
        csr = video["csr"]
        gameMap = video["map"]
        gamemode = video["gameMode"]
        videotype = video["type"]
        videocategory = video["category"]
        etag = video["etag"]
        
        cur.execute("SELECT etag FROM Videos WHERE vidId = ?", (vidID,))
        result = cur.fetchone()

        if result is None:
            print(f"new video. modifying {vidID}")

            insert_query = """
            INSERT INTO Videos (
                vidID, title, duration, published, description,
                thumbnailsdefault, thumbnailsmedium, thumbnailshigh, thumbnailsmax,
                kind, channelid, csr, map, gameMode, videotype, videocategory, etag
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cur.execute(insert_query, (
                vidID, title, duration, published, description,
                thumbnailsdefault, thumbnailsmedium, thumbnailshigh, thumbnailsmax,
                kind, channelid, csr, gameMap, gamemode, videotype, videocategory, etag
            ))

            db.commit()

        elif  result[0] != etag:
            print(f"upating video. modifying {vidID}")
            update_query = """
                UPDATE Videos
                    SET title = ?, duration = ?, published = ?, description = ?,
                    thumbnailsdefault = ?, thumbnailsmedium = ?, thumbnailshigh = ?, thumbnailsmax = ?,
                    kind = ?, channelid = ?, csr = ?, map = ?, gameMode = ?, videotype = ?, videocategory = ?, etag = ?
                    WHERE vidID = ?
                """

            cur.execute(update_query, (
                    title, duration, published, description,
                    thumbnailsdefault, thumbnailsmedium, thumbnailshigh, thumbnailsmax,
                    kind, channelid, csr, gameMap, gamemode, videotype, videocategory, etag,
                    vidID
                ))

        else:
            print(f"skipping video ({vidID}) record is already up to date.")

    db.commit()
    db.close()  
    return f"db updated"



    db.commit()
    print("Database commit complete.")



##############################################

def Update_Video_Database_Full():
    Google_API_V3_PULL_Video_Info(extracted)
    Google_API_V3_Pull_Durations(extracted)
    Google_API_V3_Clean_Data(extracted)
    Google_API_V3_Write_JSON(extracted, "clean")
    modified = Google_API_V3_Modify_Values()
    Google_API_V3_Write_JSON(modified, "dbReady")
    Google_API_V3_Write_Thumbnails()
    with app.app_context():
        Commit_to_DB()

    return f"successfully carried out full video DB update including thumbnails"


Update_Video_Database_Full()
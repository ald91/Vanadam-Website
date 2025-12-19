from .db import get_database


def Single_Video_Query(vidID: int) -> dict:
   
    """ returns all database info of a single video as a video object"""

    db = get_database()
    cur = db.cursor()
    query =  """SELECT vidID, postID, title, duration, published, description, thumbnailsdefault, thumbnailshigh, thumbnailsmax, kind, channelid, csr, gamemap, gamemode, videotype, hidden, manualedit FROM Videos WHERE vidID = ? """
    
    data = cur.execute(query, (vidID,))
    data = cur.fetchone()

    if data is None:
        return None
    
    data = dict(data)

    return data

def Toggle_Video_Visibility(vidID: str) -> bool:
    
    """ Toggle a video's visibility flag True/False so that it cannot be seen by non admins"""
    
    videoData = Single_Video_Query(vidID)
    
    if not videoData:
        print("video not found:", vidID)
        return False
    
    print(videoData)
    hidden = videoData.get("hidden")
    hidden = 0 if hidden else 1

    try:

        db = get_database()
        cur = db.cursor()
        cur.execute("UPDATE Videos SET hidden = ?, manualedit = ? WHERE vidID = ?",(hidden, 1 , vidID))
        db.commit()
        db.close()

        return True
    
    except Exception as e:
        print("failed to write new status of video", e)
        return False

def All_Videos_Query(showHidden: bool = False) -> list[dict]:
    
    """fetches all video records with Post tags and Post ID video fields are postID / vidID / title / csr / thumbnailsmax / gamemap / gamemode / videotype / hidden / manualedit / date"""

    db = get_database()
    cur = db.cursor()
    query = """
        SELECT 
        'Video' AS type, v.postID, v.vidID, v.title, v.csr, v.thumbnailsmax, v.gamemap, v.gamemode, v.videotype, v.hidden, v.manualedit, p.date,
        GROUP_CONCAT(pt.tagname) AS tags
        FROM Videos v
        
        LEFT JOIN Posts p ON v.postID = p.postID
        LEFT JOIN PostTags pt ON v.postID = pt.postID
        
        GROUP BY v.postID;  
    """

    cur.execute(query)
    videos = [dict(row) for row in cur.fetchall()]

    if not showHidden:
        videos = [video for video in videos if not video.get("hidden")]
        
    return videos
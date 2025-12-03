#external modules
from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_session import Session

#python modules
from functools import wraps

#app imports
from db import get_database

#set admin route
site = Blueprint("site", __name__, template_folder="templates")



##################
#-----Routes-----#
##################

@site.route('/videos/<videoID>', methods=['GET'])
def video(videoID):

    print(f'got ({videoID}) from request')
    
    videoID = videoID.strip()
    db = get_database()
    cur = db.cursor()

    #run query for video resources
    videoInfo_query =  """  SELECT vidID, title, published, description, thumbnailsmax, thumbnailshigh, csr, gamemap, gamemode, videotype FROM Videos WHERE vidID = ? """
    cur.execute(videoInfo_query, (videoID,))
    videoInfo = dict(cur.fetchone())
    print(videoInfo["gamemap"],videoInfo["gamemode"],videoInfo["csr"])
   

    #find same map, mode and rank videos to suggest to use
    videoSameMap_query = """ SELECT vidID, thumbnailsmedium, gamemap, videotype FROM Videos WHERE gamemap = ? AND vidID != ? AND videotype = 'Longform' """
    cur.execute(videoSameMap_query, (videoInfo["gamemap"], videoID))
    videoSameMap = cur.fetchall()
    videoSameMap = [dict(row) for row in videoSameMap]

    videoSameMode_query = """ SELECT vidID, thumbnailsmedium, gamemode, videotype FROM Videos WHERE gamemode = ? AND vidID != ? AND videotype = 'Longform' """
    cur.execute(videoSameMode_query, (videoInfo["gamemode"], videoID))
    videoSameMode = cur.fetchall()
    videoSameMode = [dict(row) for row in videoSameMode]

    
    return render_template('content/video.html', videoInfo=videoInfo, videoSameMap=videoSameMap, videoSameMode=videoSameMode) 
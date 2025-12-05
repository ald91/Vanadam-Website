
#TODO - Implement

from flask import current_app
import requests
import json
import isodate
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

#internal imports
from app.HaloData import HALO_INFINITE_DATA, infiniteCSR
from app.data.db import *
from app.services import checkTags

    # === ARTICLES ===
""" articleID / postID / title / description / content / image_filename """

def Full_Article_Management_Query():
    """fetches all video records with Post tags and Post ID"""

    db = get_database()
    cur = db.cursor()
    query = """
        SELECT 
        'Article' AS type, a.postID, a.articleID, a.title, a.description, a.image_filename, a.content, p.date,
        GROUP_CONCAT(pt.tagname) AS tags
        FROM Articles a
        
        LEFT JOIN Posts p ON a.postID = p.postID
        LEFT JOIN PostTags pt ON a.postID = pt.postID
        
        GROUP BY a.postID;  
    """

    cur.execute(query)
    articles = cur.fetchall()
    articles = [dict(row) for row in articles]

    return articles

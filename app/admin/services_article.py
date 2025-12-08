
#TODO - Implement

from flask import current_app
from werkzeug.utils import secure_filename
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

#directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/admin -> parent
data_dir = os.path.join(base_dir, "data")
assets_dir = os.path.join(base_dir, "static/assets")
articles_dir = os.path.join(data_dir,"articles")
articles_JSON_dir = os.path.join(articles_dir, "ArticlesJSON")
articles_IMG_dir = os.path.join(assets_dir, "ArticlesIMG")

    # === ARTICLES ===
""" articleID / postID / title / description / content / image_filename """

def All_Articles_Management_Query():
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
    print(articles)

    return articles

def Single_Article_Query(articleID):
    """ returns all data of a single article """

    db = get_database()
    cur = db.cursor()
    query =  """
    SELECT articleID, postID, title, description, content, image_filename
    FROM Articles
    WHERE articleID = ?
    """
    article = cur.execute(query, (articleID,))
    article = cur.fetchone()
    articleData = dict(article)

    return articleData

def Register_New_Article(form):
    print("revieved data of:", form)
    articleTitle = form.title.data
    articleContent = form.content.data
    articleTags = form.tags.data

    #runs against DB for tags
    checkTags("Article", articleTags)

    #save new article (sets articleID)
    db = get_database()
    cur = db.cursor()
    query = """INSERT INTO Articles (title) VALUES (?)"""
    cur.execute(query, (articleTitle,))

    #find article just saved to link JSON / IMG to DB
    query =  """
        SELECT articleID, postID, title, description, content, image_filename
        FROM Articles
        WHERE title = ?
    """
    cur.execute(query, (articleTitle,))
    articleInfo = dict(cur.fetchone())
    articleID = articleInfo["articleID"]

    #save image (as A###.jpeg linking it to articleID)
    if form.image.data:
        file = form.image.data
        article_IMG_filename = secure_filename(f"A{articleID}.jpeg")
        image_path = os.path.join(articles_IMG_dir, article_IMG_filename)
        file.save(image_path)
    else:
        article_IMG_filename = None

    
    article_JSON_filename = f"A{articleID}.JSON"

    #update DB record with img filename
    query = """
        UPDATE Articles
        SET image_filename = ?, content = ?
        WHERE articleID = ? ;
    """
    cur.execute(query,(article_IMG_filename, article_JSON_filename, articleID))


    #prep article and store to JSON with all info
    articleData = {
        "articleID" : articleID,
        "articleContent" : articleContent,
        "articleTags" : articleTags,
        "article_IMG_filename" : article_IMG_filename
    }
    
    article_save_location = os.path.join(articles_JSON_dir, article_JSON_filename)

    json_str = json.dumps(articleData, indent=4)
    with open(article_save_location, "w") as f:
        f.write(json_str)

    db.commit()
    db.close()

    return

def Get_Article_Data(articleID: int):
    filePath = os.path.join(f"{articles_JSON_dir}/A{articleID}.JSON")
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)
  
    return data
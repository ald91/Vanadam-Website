
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

""" ARTICLE DB SCHEMA -> articleID / postID / title / description / content / image_filename """

# === ARTICLE HELPERS ===

def Article_Image_save(imagedata: str, articleID: str) -> str: #article_IMG_filename
    #save image (as A###.jpeg linking it to articleID)
    try:
        file = imagedata
        article_IMG_filename = secure_filename(f"A{articleID}.jpeg")
        image_path = os.path.join(articles_IMG_dir, article_IMG_filename)
        file.save(image_path)
        print("image for article:", articleID," saved successfully.")
    except:
        print("no image submitted for article", articleID)
        article_IMG_filename = None
    
    return article_IMG_filename

def Article_JSON_save(articleID: int, articleTitle: str, articleDescription: str, articleContent: str, articleTags:list) -> str: #article_JSON_filename
    
    #prep article and store to JSON with all info
    articleData = {
        "articleID" : articleID,
        "articleTitle": articleTitle,
        "articleDescription" : articleDescription,
        "articleContent" : articleContent,
        "articleTags" : articleTags,
    }
    
    article_JSON_filename = f"A{articleID}.JSON"

    article_save_location = os.path.join(articles_JSON_dir, article_JSON_filename)

    json_str = json.dumps(articleData, indent=4)
    with open(article_save_location, "w") as f:
        f.write(json_str)

# === ARTICLES MAIN FUNCTIONS ===

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

def Single_Article_Query(articleID: str) -> dict:
   
    """ returns all database info of a single article """

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

def Register_New_Article(form: object) -> bool:

    """ registers a new article to the database, saving the JSON file and the Image file using helper functions"""
    
    print("revieved data of:", form)
    articleTitle = form.title.data
    articleDescription = form.description.data
    articleContent = form.content.data
    articleTags = form.tags.data
    articleImage = form.image.data

    #runs against DB for tags
    checkTags("Article", articleTags)

    db = get_database()
    cur = db.cursor()

    #secure PostID FK (sets postID)
    cur.execute("INSERT INTO Posts(date) VALUES (datetime('now'))")
    postID = cur.lastrowid
    
    #save new article (sets articleID relating to post ID)
    cur.execute("INSERT INTO Articles (postID, title) VALUES (?, ?)", (postID, articleTitle))

    #find article just saved to link JSON / IMG to DB
    query =  """
        SELECT articleID, postID, title, description, content, image_filename
        FROM Articles
        WHERE title = ?
    """
    cur.execute(query, (articleTitle,))
    articleInfo = dict(cur.fetchone())
    articleID = articleInfo["articleID"]

    article_IMG_filename = Article_Image_save(articleImage, articleID)
    article_JSON_filename = Article_JSON_save(articleID, articleTitle, articleDescription, articleContent, articleTags)

    #update DB record with img filename
    query = """
        UPDATE Articles
        SET  description = ?, image_filename = ?, content = ? 
        WHERE articleID = ? ;
    """
    cur.execute(query,(articleDescription, article_IMG_filename, article_JSON_filename, articleID))

    db.commit()
    db.close()

    return True

def Get_Article_Data(articleID: int) -> dict:
    
    """ opens article JSON data giving fields  articleID/articleTitle/articleDescription/articleContent/articleTags/article_IMG_filename"""

    filePath = os.path.join(f"{articles_JSON_dir}/A{articleID}.JSON")
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(data)

    return data

def Modify_Article_Data(articleID: int, form: object) -> bool:

    """ Modify the JSON data and IMG data of an article article -> ID / postID / title / description / content / image_filename """

    articleID = articleID
    articleTitle = form.title.data
    articleDescription = form.description.data
    articleContent = form.content.data
    articleImage = form.image.data
    articleTags = form.tags.data

    Article_Image_save(articleImage, articleID)
    Article_JSON_save(articleID, articleTitle, articleDescription, articleContent, articleTags)

    db = get_database()
    cur = db.cursor()
    
    #tag changes?
    query = "UPDATE Articles SET title = ?, description = ? WHERE articleID = ?"
    cur.execute(query, (articleTitle, articleDescription, articleID))
    db.commit()
    print("Article Edited")

    return True

def Delete_Article(articleID: int) -> bool:

    """ fully delete an article from the DB, including JSON and IMG"""

    articleData = Single_Article_Query(articleID)
    articlePostID = articleData.get("postID")

    try:
        db = get_database()
        cur = db.cursor()
        cur.execute("DELETE FROM Posts WHERE postID = ?", (articlePostID,))
        db.commit()

        print(f"Article number {articleID} deleted from DB")

    except Exception as e:
        print(f"error deleting article from DB", {e})
        return False

    print(articleID)
    JSON_Deletion = Delete_Article_JSON(articleID)
    IMG_Deletion = Delete_Article_IMG(articleID)

    if JSON_Deletion and IMG_Deletion == True:
        return True
    else:
        return False

def Delete_Article_JSON(articleID: int) -> bool:
    
    """ Delete an article JSON file"""
    
    JSONArticleFilePath = f"{articles_JSON_dir}/A{articleID}.JSON"
    try:
        os.remove(JSONArticleFilePath)
    except FileNotFoundError as e:
        print("could not find article JSON file", e)
    
    except Exception as e:
        print("could not delete article JSON file", e)
        return False

    print("Article JSON file deleted")
    return True
   
def Delete_Article_IMG(articleID: int) -> bool:
    
    """ Delete an article IMG file"""
    
    IMGArticleFilePath = f"{articles_IMG_dir}/A{articleID}.jpeg"
    try:
        os.remove(IMGArticleFilePath)
    except FileNotFoundError as e:
        print(f"could not find article IMG file", {e})

    
    except Exception as e:
        print(f"could not delete article IMG file", {e})
        return False

    print("Article IMG file deleted")
    return True

def Toggle_Article_Visibility(articleID: int) -> bool:
    
    """ Toggle an articles visibility flag True/False so that it cannot be seen by non admins"""
    
    articleData = Single_Article_Query(articleID)

    if articleData.get("hidden") == True:
        articleData("hidden") == None

    if articleData.get("hidden") == False or articleData.get("hidden") == None:
        articleData("hidden") == True

    
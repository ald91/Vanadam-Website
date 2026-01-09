from flask import current_app
from werkzeug.utils import secure_filename
import json
import os
import shutil

from dotenv import load_dotenv
load_dotenv()

#internal imports
from app.data.db import *
from app.services import checkTags

#directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/admin -> parent
data_dir = os.path.join(base_dir, "data")
assets_dir = os.path.join(base_dir, "static/assets")
articles_dir = os.path.join(data_dir,"articles")
articles_JSON_dir = os.path.join(articles_dir, "articlesJSON")
articles_IMG_dir = os.path.join(articles_dir, "articlesIMG")

os.makedirs(articles_dir, exist_ok=True)
os.makedirs(articles_JSON_dir, exist_ok=True)
os.makedirs(articles_IMG_dir, exist_ok=True)

""" ARTICLE DB SCHEMA -> articleID / postID / title / description / json_filename / image_filename """

# === ARTICLE HELPERS ===

def article_image_save(imagedata: str, articleID: str) -> str: #article_IMG_filename
    """save an image (as A###.jpeg linking it to articleID) in data module /articles/articleIMG"""
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

def article_JSON_save(articleID: int, articleTitle: str, articleDescription: str, article_content: str, articleTags:list) -> str: #article_JSON_filename
    """ saves data to  JSON in data module articles/articleJSON"""
    article_data = {
        "articleID" : articleID,
        "articleTitle": articleTitle,
        "articleDescription" : articleDescription,
        "article_content" : article_content,
        "articleTags" : articleTags,
    }

    article_JSON_filename = f"A{articleID}.JSON"
    article_save_location = os.path.join(articles_JSON_dir, article_JSON_filename)

    json_str = json.dumps(article_data, indent=4)
    with open(article_save_location, "w", encoding="utf-8") as f:
        f.write(json_str)

    return article_JSON_filename

def article_JSON_load(articleID: int) -> str:
    """ loads a JSON file and returns the content as a HTML String that self formats in the users browser """
    file_path = f"{articles_JSON_dir}/A{articleID}.JSON"

    with open(file_path, "r", encoding="utf-8" ) as f:
        data = json.load(f)  
    article_content = data.get("article_content")
    return article_content


# === ARTICLES MAIN FUNCTIONS ===

def all_articles_query(showHidden :bool = False) -> list[dict]:
    
    """fetches all video records with Post tags and Post ID
    visible controls if ALL or just visible articles are returned"""

    db = get_database()
    cur = db.cursor()
    query = """
        SELECT 
        'Article' AS type, a.postID, a.articleID, a.title, a.description, a.image_filename, a.json_filename, a.hidden, p.date,
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

    if not showHidden:
        articles = [article for article in articles if not article.get("hidden")]

    return articles

def single_article_query(articleID: int) -> dict:
   
    """ returns all database info of a single article as an Article object"""

    db = get_database()
    cur = db.cursor()
    query =  """
    SELECT articleID, postID, title, description, json_filename, image_filename, hidden
    FROM Articles
    WHERE articleID = ?
    """
    data = cur.execute(query, (articleID,))
    data = cur.fetchone()

    if data is None:
        return None
    
    data = dict(data)

    return data

def register_new_article(form: object) -> bool:

    """ registers a new article to the database, saving the JSON file and the Image file using helper functions"""
    
    print("revieved data of:", form)

    articleTitle = form.title.data
    articleDescription = form.description.data
    article_content = form.content.data
    articleTags = form.tags.data
    articleImage = form.image.data
    articleHidden = form.hidden.data


    db = get_database()
    cur = db.cursor()

    #secure PostID FK (sets postID)
    cur.execute("INSERT INTO Posts(date) VALUES (datetime('now'))")
    postID = cur.lastrowid

    #runs against DB for tags
    checkTags(cur, "Article", postID, articleTags)
    
    #save new article (sets articleID relating to post ID)
    cur.execute("INSERT INTO Articles (postID, title) VALUES (?, ?)", (postID, articleTitle))

    #find article just saved to link JSON / IMG to DB
    query =  """
        SELECT articleID, postID, title, description, json_filename, image_filename, hidden
        FROM Articles
        WHERE title = ?
    """
    cur.execute(query, (articleTitle,))
    articleInfo = dict(cur.fetchone())
    articleID = articleInfo["articleID"]

    article_IMG_filename = article_image_save(articleImage, articleID)
    article_JSON_filename = article_JSON_save(articleID, articleTitle, articleDescription, article_content, articleTags)

    #update DB record with img filename
    query = """
        UPDATE Articles
        SET  description = ?, image_filename = ?, json_filename = ? 
        WHERE articleID = ? ;
    """
    cur.execute(query,(articleDescription, article_IMG_filename, article_JSON_filename, articleID))

    checkTags(cur, "Article", postID, articleTags)

    db.commit()

    return True

def get_article_data(articleID: int) -> dict:
    
    """ opens article JSON data giving fields  articleID/articleTitle/articleDescription/json_filename/articleTags/img_filename"""

    filePath = os.path.join(f"{articles_JSON_dir}/A{articleID}.JSON")
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(data)

    return data

def modify_article_data(articleID: int, form: object) -> bool:

    """ Modify the JSON data and IMG data of an article article -> ID / postID / title / description / json_filename / image_filename / hidden """

    articleID = articleID
    articleTitle = form.title.data
    articleDescription = form.description.data
    article_content = form.content.data
    articleImage = form.image.data
    articleTags = form.tags.data
    articleHidden = bool(form.hidden.data)

    if articleImage:
        article_image_save(articleImage, articleID)
            
    article_JSON_save(articleID, articleTitle, articleDescription, article_content, articleTags)

    db = get_database()
    cur = db.cursor()
    
    #tag changes?
    query = "UPDATE Articles SET title = ?, description = ?, hidden = ? WHERE articleID = ?"
    cur.execute(query, (articleTitle, articleDescription, articleHidden, articleID))
    db.commit()
    print("Article Edited")

    return True

def delete_article(articleID: int) -> bool:

    """ fully delete an article from the DB, including JSON and IMG"""

    if articleID == 1:
        return False

    article_data = single_article_query(articleID)
    articlePostID = article_data.get("postID")

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
    JSON_Deletion = delete_article_JSON(articleID)
    IMG_Deletion = delete_article_IMG(articleID)

    if JSON_Deletion and IMG_Deletion == True:
        return True
    else:
        return False

def delete_article_JSON(articleID: int) -> bool:
    
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
   
def delete_article_IMG(articleID: int) -> bool:
    
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

def toggle_article_visibility(articleID: int) -> bool:
    
    """ Toggle an articles visibility flag True/False so that it cannot be seen by non admins"""
    
    article_data = single_article_query(articleID)
    if not article_data:
        print("article not found:", articleID)
        return False
    
    print(article_data)
    hidden = article_data.get("hidden")
    hidden = 0 if hidden else 1

    try:

        db = get_database()
        cur = db.cursor()
        cur.execute("UPDATE Articles SET hidden = ? WHERE articleID = ?",(hidden, articleID))
        db.commit()

        return True
    
    except Exception as e:
        print("failed to write new status of article", e)
        return False

def test_article() -> bool:
    testFile_JSON = "test.JSON"
    testFile_JSON_path = f"{articles_JSON_dir}/test.JSON"

    testFile_IMG = "test.Jpeg"

    with open(testFile_JSON_path,"r", encoding="utf-8") as f:
        data = json.load(f)
        print("data= ", data, "\n")

    articleTitle = data["articleTitle"]
    articleDescription = data["articleDescription"]
    articleTags = data["articleTags"]
    articleHidden = 0

    db = get_database()
    cur = db.cursor()

    #secure PostID FK (sets postID)
    cur.execute("INSERT INTO Posts(date) VALUES (datetime('now'))")
    postID = cur.lastrowid
    
    #save new article (sets articleID relating to post ID)
    cur.execute("INSERT INTO Articles (postID, title, description, json_filename, image_filename, hidden) VALUES (?, ?, ?, ?, ?, ?)", (postID, articleTitle, articleDescription, testFile_JSON, testFile_IMG, articleHidden))
    
    cur.execute("SELECT articleID FROM Articles WHERE postID = ?", (postID,))
    articleInfo = dict(cur.fetchone())
    articleID = articleInfo["articleID"]
    

    checkTags(cur, "Article", postID, articleTags)
    
    #copy JSON and IMG file for testing purposes
    src_json = f"{articles_JSON_dir}/test.json"
    dst_json = f"{articles_JSON_dir}/A{articleID}.json"

    src_img = f"{articles_IMG_dir}/test.jpeg"
    dst_img = f"{articles_IMG_dir}/A{articleID}.jpeg"

    shutil.copy2(src_json,dst_json)
    print("json copied")
    shutil.copy2(src_img, dst_img)
    print("thumbcopied")

    db.commit()

    return True
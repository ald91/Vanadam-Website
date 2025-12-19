from ..services import checkTags
from ..data.db import get_database
from flask import session

def post(form):
    title = form.title.data
    content = form.content.data

    username = session.get("username")

    db = get_database()
    cur = db.cursor()

    query = "INSERT INTO Forums (title, content, originalPoster) VALUES (?, ?, ?)"
    cur.execute(query, (title, content, username))
    db.commit()

def comment(form, id):
    content = form.content.data
    username = session["username"]

    db = get_database()
    cur = db.cursor()

    query = "INSERT INTO Messages (forumID, username, content) VALUES (?, ?, ?)"
    cur.execute(query, (id, username, content))
    db.commit()


def delete(id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT originalPoster FROM Forums WHERE forumID = ?"
    cur.execute(query, (id,))
    result = dict(cur.fetchone())

    # Allow only original poster to delete
    if check(result["username"]):
        query = "DELETE FROM Forums WHERE forumID = ?"
        cur.execute(query, (id,))

def prefill(form, id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums WHERE forumID = ?"
    cur.execute(query, (id,))
    result = dict(cur.fetchone())

    form.title.data = result["title"]
    form.content.data = result["content"]

    return form

def modify(form):
    db = get_database()
    cur = db.cursor()

    title = form.title.data
    content = form.content.data
    original_poster = form.content.username
    #Allow only original poster to modify
    if check(original_poster):
        query = "UPDATE Forums SET title = ?, content = ?"
        cur.execute(query, (title, content))
        db.commit()

def fetch_all():
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums"
    cur.execute(query)

    result = cur.fetchall()
    return result

def fetch_one(id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums WHERE forumID = ?"
    cur.execute(query, (id,))

    result = cur.fetchone()
    return result

def fetch_comments(id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Messages WHERE forumID = ?"
    cur.execute(query, (id,))

    result = cur.fetchall()
    return result

#Checks current user from session against provided username (original poster)
def check(user_id):
    if session.get("username") == user_id:
        return True
    else:
        return False
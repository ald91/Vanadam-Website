from ..services import checkTags
from ..data.db import get_database
from flask import session, abort

def post(form, username):
    title = form.title.data
    content = form.content.data

    db = get_database()
    cur = db.cursor()

    query = "INSERT INTO Forums (title, content, originalPoster) VALUES (?, ?, ?)"
    cur.execute(query, (title, content, username))
    db.commit()

def comment(form, id, username):
    content = form.content.data

    db = get_database()
    cur = db.cursor()

    query = "INSERT INTO Messages (forumID, username, content) VALUES (?, ?, ?)"
    cur.execute(query, (id, username, content))
    db.commit()


def delete_post_record(id):
    db = get_database()
    cur = db.cursor()

    # Allow only original poster to delete
    if check(id):
        query = "DELETE FROM Forums WHERE forumID = ?"
        cur.execute(query, (id,))
        db.commit()

def delete_comment_record(id):
    db = get_database()
    cur = db.cursor()

    # Allow only original poster to delete
    if check(id):
        query = "DELETE FROM Messages WHERE msgID = ?"
        cur.execute(query, (id,))
        db.commit()

def prefill(form, id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums WHERE forumID = ?"
    cur.execute(query, (id,))
    result = dict(cur.fetchone())

    form.title.data = result["title"]
    form.content.data = result["content"]

    return form

def modify(form, id):
    db = get_database()
    cur = db.cursor()

    title = form.title.data
    content = form.content.data
    #Allow only original poster to modify
    if check(id):
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

#Checks current user from session against provided username (original poster), optionally, args can provide postID
def check(forumID):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums WHERE forumID = ?"
    cur.execute(query, (forumID,))

    post = dict(cur.fetchone())

    if session.get("username") == post["originalPoster"]:
        return True
    else:
        return False

def file_report(target_type, target_id, current_user):
    db = get_database()
    cur = db.cursor()

    #Ensure target element exists before processing report
    if target_type == "post":
        cur.execute("SELECT 1 FROM Forums WHERE forumID = ?", (target_id,))
    elif target_type == "comment":
        cur.execute("SELECT 1 FROM Messages WHERE msgID = ?", (target_id,))

    if cur.fetchone() is None:
        abort(404)

    cur.execute("""
            INSERT INTO Reports (target_type, target_id, reported_by)
            VALUES (?, ?, ?)
        """, (target_type, target_id, current_user))

    db.commit()



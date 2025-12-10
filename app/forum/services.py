from ..services import checkTags
from ..data.db import get_database
from flask import session

def post(form):
    title = form.title.data
    content = form.content.data

    username = session["username"]

    db = get_database()
    cur = db.cursor()

    query = "INSERT INTO Forums (title, content, username) VALUES (?, ?, ?)"
    cur.execute(query, (title, content, username))
    db.commit()

def prefill(form):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Forums WHERE id = ?"
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

    username = session["username"]

    query = "UPDATE Forums SET title = ?, content = ?, username = ?, WHERE id = ?"
    cur.execute(query, (title, content, username, id))
    db.commit()
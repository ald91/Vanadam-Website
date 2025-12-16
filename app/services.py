from functools import wraps
from flask import session, redirect, url_for
from app.data.db import get_database

def checkTags(postType, tags):

    """ checks if posts has an unknown tag. if it does, adds the new tag to the Tags Table"""

    #for Articles (could have multiple)
    if postType == "Article":
        tags = tags.split(",")

    #for Videos (only ever have 1 tag)
    if postType == "Video":
        tags = [tags]

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT * from Tags")
    existing_tags = {row["tagName"] for row in cur.fetchall()} 

    # Insert only new tags
    for tag in tags:
        if tag not in existing_tags:
            cur.execute("INSERT INTO Tags(tagName) VALUES(?)", (tag,))


#By applying @login_required before after a route definition and before function declaration, you can designate a route to require login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper

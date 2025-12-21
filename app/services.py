from functools import wraps
from flask import session, redirect, url_for
from app.data.db import get_database

def checkTags(cur: object, postType:str, postID:int, tags: str | list ) -> None:

    """ checks if posts has an unknown tag. if it does, adds the new tag to the Tags Table.
        This function does not open its own database connection, it will rely on the parent function to do so,
        make sure the connection is opened using cur BEFORE calling this function"""

    print("post type is: ", postType,"tags revieved are:", tags)

    #if no tags are given (flask forms sends None)
    tags = tags or ""

    if not tags:
        print("No tags provided or detected")
        return

    #for Articles (could have multiple)
    elif postType == "Article" and isinstance(tags, str):
        tags = tags.split(",")

    #for Videos (only ever have 1 tag)
    elif postType == "Video":
        pass
    else:
        print("unrecognised tag format, aborting")
        return  
    
    #normalize to stop duplication on capitalizations ( Tag vs tag )
    tags = [t.strip().lower() for t in tags if isinstance(t, str) and t.strip()]

    for tag in tags:
        print(postID, tag)
        cur.execute("INSERT OR IGNORE INTO Tags(tagName) VALUES(?)", (tag,))
        cur.execute("INSERT OR IGNORE INTO PostTags(PostID, tagName) VALUES(?, ?)", (postID, tag))


#By applying @login_required before after a route definition and before function declaration,
# you can designate a route to require login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "userID" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper

#Delete all but the 16 newest posts to the forums table,
# uses Flask-APScheduler for automation, as defined in __init__.py
def clear_stale_posts():
    db = get_database()
    cur = db.cursor()

    query = """
    DELETE FROM Forums
    WHERE forumID NOT IN (
        SELECT forumID FROM (
            SELECT forumID
            FROM Forums
            ORDER BY forumID DESC
            LIMIT 16
        ) AS newest
    )
    """
    cur.execute(query)
    db.commit()

def check_ban(username:str) -> bool:
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Users WHERE username = ?"
    cur.execute(query, (username,))

    result = dict(cur.fetchone())
    if result["banned"]:
        return True
    else:
        return False
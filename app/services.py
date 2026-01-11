from app.data.db import get_database
from flask import session



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

def clear_stale_posts(app):
    """Delete all but the 16 newest posts to the forums table, uses Flask-APScheduler for automation, as defined in __init__.py"""
    try:
        with app.app_context():
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
    except RuntimeError as e:
        print("Runtime error: ", e)

def video_db_daily_update():
    """ causes video db to update periodically, called in app factory as a daily repeated process"""
    from app.admin.services_video import Update_Video_Database_Full
    Update_Video_Database_Full()
    return

def check_ban(username:str) -> bool:
    """Checks if a user has the banned flag, determines if they are allowed to post"""
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM Users WHERE username = ?"
    cur.execute(query, (username,))
    result = cur.fetchone()
    if result is not None:
        result = dict(result)
    else:
        print("Checked ban on non-existent user")
        return True
    if result["banned"]:
        return True
    else:
        return False   
def post_form_match_case(string: str) -> list[str,str]:
    """ takes a unnamed form from a post request on the dashboard and preps the responce so backend can direct to the correct item (video/article/user) etc."""  
    check = "("
    itemID: str | None = None 
    if check in string:
        string = string.split("(")
        action = str(string[0])
        itemID = string[1].replace("(","").replace(")","")
    else:
        action = str(string)
    match_case = [action, itemID]
    return match_case

from .db import get_database

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


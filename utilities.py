from datetime import datetime
from db import *

#when pulling [{dicts}] from DB you can use this function to mass convert the ISO date into a readable format
def format_date_from_ISO_DB(Dbpull):
    
    """ converts lists of {dicts} from SQLite.row_factory DB pulls ISO8001 dates into readable dates for humans"""

    for row in Dbpull:
        iso = row["published"]
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        row["published"] = dt.strftime("%d %b %Y")
    return Dbpull

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


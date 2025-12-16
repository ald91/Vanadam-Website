from app.data.db import get_database

def checkTags(cur: object, postType:str, postID:int, tags: str | list ) -> None:

    """ checks if posts has an unknown tag. if it does, adds the new tag to the Tags Table. This function does not open its own database
        connection, it will rely on the parent function to do so, make sure the connection is opened using cur BEFORE calling this function"""

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
        tags = [tags]

    else:
        print("unrecognised tag format, aborting")
        return  
    
    #normalize to stop duplication on capitalizations ( Tag vs tag )
    tags = [t.strip().lower() for t in tags if t.strip()]
    
    for tag in tags:
        cur.execute("INSERT OR IGNORE INTO Tags(tagName) VALUES(?)", (tag,))

    return

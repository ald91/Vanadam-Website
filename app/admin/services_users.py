from ..data.db import get_database

# Return list of users
def All_Users_Management_Query() -> list[dict]:
    """ returns all users in the database """
    db = get_database()
    cur = db.cursor()
    query = "SELECT * FROM users"
    res = cur.execute(query)
    return res.fetchall()

def Delete_User(userID: str) -> bool:
    """ deletes a user from the DB"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """DELETE FROM users WHERE userID = ?"""
        cur.execute(query, (userID, ))
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

def Ban_User(userID: str) -> bool:
    """ set a users banned status to TRUE"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET banned = 1 WHERE userID = ?"""
        cur.execute(query, (userID, ))
    except Exception as e:
        print("ban user error: ", e)
        return False
    return True

def Unban_User(userID: str) -> bool:
    """ set a users banned status to false"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET banned = 0 WHERE userID = ?"""
        cur.execute(query, (userID,))
    except Exception as e:
        print("unban user error: ", e)
        return False
    return True

def Update_User_Tags(userID: str, tags: str) -> None:
    """ updates a user tag string """
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET tags = ? WHERE userID = ?"""
        cur.execute(query, (tags, userID))
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

def Update_User_Is_Admin(userID: str, isAdmin: bool) -> None:

    """ switches a users role to ADMIN. BE CAREFUL USING THIS"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET tags = ? WHERE userID = ?"""
        cur.execute(query, (isAdmin, userID))
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

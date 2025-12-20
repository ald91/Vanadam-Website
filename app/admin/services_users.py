from ..data.db import get_database

# Return list of users
def All_Users_Management_Query() -> list[dict]:
    """ returns all users in the database """
    AllUsers = None
    try:
        db = get_database()
        cur = db.cursor()
        query = "SELECT * FROM users"
        res = cur.execute(query)
        AllUsers = [dict(row) for row in res]
    except Exception as e:
        print("could not load user database: ", e)
    return AllUsers

def Delete_User(userID: int) -> bool:
    """ deletes a user from the DB"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """DELETE FROM users WHERE userID = ?"""
        cur.execute(query, (userID, ))
        db.commit()
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

def Ban_User(userID: int) -> bool:
    """ set a users banned status to TRUE"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET banned = 1 WHERE userID = ?"""
        print(cur.fetchone())
        cur.execute(query, (userID, ))
        db.commit()
        if cur.rowcount == 0:
            print(f"couldnt find userID {userID}")
            return False
        return True
    except Exception as e:
        print("ban user error: ", e)
        return False

def Unban_User(userID: int) -> bool:
    """ set a users banned status to false"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET banned = 0 WHERE userID = ?"""
        cur.execute(query, (userID,))
        db.commit()
    except Exception as e:
        print("unban user error: ", e)
        return False
    return True

def Update_User_Tags(userID: int, tags: str) -> None:
    """ updates a user tag string """
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET tags = ? WHERE userID = ?"""
        cur.execute(query, (tags, userID))
        db.commit()
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

def Update_User_Is_Admin(userID: int, isAdmin: bool) -> None:

    """ switches a users role to ADMIN. BE CAREFUL USING THIS"""
    try:
        db = get_database()
        cur = db.cursor()
        query = """UPDATE users SET tags = ? WHERE userID = ?"""
        cur.execute(query, (isAdmin, userID))
        db.commit()
    except Exception as e:
        print("delete user error: ", e)
        return False
    return True

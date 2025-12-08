from ..data.db import get_database

# Return list of users
def All_Users_Management_Query():
    db = get_database()
    cur = db.cursor()
    query = "SELECT * FROM users"
    res = cur.execute(query)
    return res.fetchall()

def Delete_User(userID):
    db = get_database()
    cur = db.cursor()
    query = """DELETE FROM users WHERE userID = ?"""
    cur.execute(query, (userID, ))
    pass

def Ban_User(userID):
    db = get_database()
    cur = db.cursor()
    query = """UPDATE users SET banned = 1 WHERE userID = ?"""
    cur.execute(query, (userID, ))
    pass

def Unban_User(userID):
    db = get_database()
    cur = db.cursor()
    query = """UPDATE users SET banned = 0 WHERE userID = ?"""
    cur.execute(query, (userID,))
    pass

def Update_User_Tags(userID, tags):
    db = get_database()
    cur = db.cursor()
    query = """UPDATE users SET tags = ? WHERE userID = ?"""
    cur.execute(query, (tags, userID))
    pass

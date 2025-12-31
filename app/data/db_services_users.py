from .db import get_database
from flask import session

def Username_Available(requestedName:str, oldName:str) -> bool:

    """ checks the db if a username(PK) is available for use"""
    print(f" Reuqested Username is : {requestedName}, current username is: {oldName}")
    if requestedName == oldName:
        return True
    else:           
        try:
            if Single_User_Query("self", requestedName) and requestedName != oldName:
                print("username already taken")
                return False
        except Exception as e:
            print("couldnt validate the new username: ", e)
            return False
    return True

def Single_User_Query(who: str = "self", userID: int = None) -> dict:
    
    """ returns a dict based on the reuqest tier (public / self / admin).  { userID / username / email / xboxname / timezone / arenarank / isAdmin / banned } from USERS table."""
    
    userData = None

    try:
        db = get_database()
        cur = db.cursor()

        cur.execute("SELECT userID, username, email, xboxname, arenarank, timezone, isAdmin, banned FROM Users WHERE userID = ?", (userID,)) 
        userData = cur.fetchone()

        if userData:
            userData = dict(userData)

        if not userData:
            return None
        
        #public keys
        KEYS = ( "username", "xboxname", "timezone", "arenarank")
                  
        if who == "self":
            KEYS = KEYS + ("email", "banned")

        elif who == "admin":
            KEYS = KEYS + ("userID", "email", "banned", "isAdmin")
            

        #reformate the userdata DICT such that it only contains the keys appropriate for that request level
        userData = {k: userData[k] for k in KEYS if k in userData}
        print(userData)
        return userData
    
    except Exception as e:
        print("Unable to find userdata, database error:", e)

def User_Profile_Update(userID: int, form: object) -> bool:

    """ PUBLIC VERSION. Uses the ProfileEditForm object to check existing user data and edit it. This is the USER version of user edit, use Admin version if admin."""

    if form.validate_on_submit():
        submitted_username= form.username.data
        submitted_email = form.email.data
        submitted_xboxname = form.xboxname.data
        submitted_timezone = form.timezone.data
        submitted_rank = form.arenarank.data


        db = get_database()      
        cur = db.cursor()
        
        #get username
        userData = Single_User_Query("self", session["userID"])
        username:str = userData.get("username")

        #check if username is taken
        if not Username_Available(submitted_username, username):
            print("username already taken")
            return False
                 
        #if username check is okay then continue with edit
        try:
            
            cur.execute('UPDATE Users SET username = ?, email = ?, xboxname = ?, timezone = ?, arenarank = ? WHERE userID = ?',
                        (submitted_username, submitted_email, submitted_xboxname, submitted_timezone, submitted_rank, userID))
            
            db.commit()

            print(f" user {username} is now {submitted_username} and their profile has been updated")
         
            return True
    
        except Exception as e:
            print(f"Unable to update User Profile for {username}: ", e)
            return False
        
def Modify_User_Data(userID:int, form:object) -> bool:
    """ returns all user data for a user including admin fields and contributions to other areas."""

    userData = Single_User_Query("admin", userID)

    print(f"recieved form data to modify {userID}: {form}")
    currentUsername:str = userData.get("username")
    submittedUsername:str = form.username.data
    email:str = form.email.data
    xboxname:str = form.xboxname.data
    timezone:str = form.timezone.data
    arenarank:str = form.arenarank.data
    isAdmin:bool = bool(form.isAdmin.data)
    banned:bool = bool(form.banned.data)

    db = get_database()
    cur = db.cursor()

    if not Username_Available(submittedUsername, currentUsername):
        print("the username submitted is not available")
        return False

    
    try:
        cur.execute('UPDATE Users SET username = ?, email = ?, xboxname = ?, timezone = ?, arenarank = ?, isAdmin = ?, banned = ? WHERE userID = ?',
                    (submittedUsername, email, xboxname, timezone, arenarank, isAdmin, banned, userID))       
        db.commit()

        print(f" user {userID} is now {submittedUsername} and their database record has been updated")
        
    except Exception as e:
        print(f"Unable to update User Profile for {userID}: ", e)
        return False

    return True
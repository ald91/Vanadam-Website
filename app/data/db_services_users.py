from .db import get_database
from flask import session


def User_Data_Query(username: str) -> dict:
    
    """ returns username / email / xboxname / timezone from USERS table. This query is for users, admins should use User_Data_Admin_Query instead."""
    
    try:
        db = get_database()
        cur = db.cursor()

        cur.execute("SELECT username, email, xboxName, arenarank, timezone FROM Users WHERE username = ?", (username,)) 
        userData = cur.fetchone()

        if userData:
            userData = dict(userData)

        if not userData:
            return None
    except Exception as e:
        print("Unable to find userdata, database error:", e)

    return userData

def User_Profile_Update(username: str, form: object) -> bool:

    """ Uses the ProfileEditForm object to check existing user data and edit it. This is the USER version of user edit, use Admin version if admin."""

    if form.validate_on_submit():
        submitted_username= form.username.data
        submitted_email = form.email.data
        submitted_xboxname = form.xboxname.data
        submitted_timezone = form.timezone.data
        submitted_rank = form.arenarank.data


        db = get_database()      
        cur = db.cursor()
        
        #check if username is taken
        try:
            UsernameExists = User_Data_Query(submitted_username)

            if UsernameExists and submitted_username != username:
                print("username already taken")
                return False

        except Exception as e:
            print("couldnt validate the new username: ", e)
            return False
        
        #if username check is okay then continue with edit
        try:
            
            cur.execute('UPDATE Users SET username = ?, email = ?, xboxname = ?, timezone = ?, arenarank = ? WHERE username = ?',
                        (submitted_username, submitted_email, submitted_xboxname, submitted_timezone, submitted_rank, username))
            
            db.commit()
            db.close()

            #makes sure the session and username match
            session['username'] = submitted_username

            print(f" user {username} is now {submitted_username} and their profile has been updated")
         
        except Exception as e:
            print(f"Unable to update User Profile for {username}: ", e)
            return False
        
    return True
#TODO:ADAM
from flask import session
import os
import json

from .db import get_database
from .db_services_users import Single_User_Query

#directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/admin -> parent
data_dir = os.path.join(base_dir, "data")
CoachingJSON_dir = os.path.join(data_dir,"Coaching")


def Coaching_Query(who:str="self", userID:int=-1, crequestID:int=-1) -> list[dict]:
    
    """ Queries COACHING table and returns any active coaching requests for that specific user. user who = "self" or who = "admin" for customization"""
    
    SELF_KEYS = { "crequestID", "crequestTime", "userID", "username", "sessiontype", "coach", "timezone", "agreedtime", "delivered", "paid", "email", "xboxname", "arenarank"}
    ADMIN_KEYS = { "invoiceID", "json" }
    VALID_WHO = {"self" , "admin"}

    db = get_database()
    cur = db.cursor()

    if who not in VALID_WHO:
        raise ValueError("Invalid 'who' Value supplied only valid inputs are: ",VALID_WHO)
    elif who == "admin":
        KEYS = SELF_KEYS.union(ADMIN_KEYS)
    elif who == "self":
        KEYS = SELF_KEYS
    #TODO
    #send all records
    if userID == -1 and who == "admin":
        cur.execute("SELECT * FROM CoachingRequests")
        coachingData = cur.fetchall()
    #send specific record (As admin)
    elif userID == -1 and who == "admin" and crequestID > 0:
        cur.execute("SELECT * FROM CoachingReuqests WHERE crecordID = ?", (crequestID,))
        coachingData = cur.fetchone()

    #send records for a specific user
    elif isinstance(userID, int):
        cur.execute("SELECT * FROM CoachingRequests WHERE userID = ?", (userID,))
        coachingData = cur.fetchall()
    else:
        print("invalid request")
        return False
    
    coachingData = [dict(row) for row in coachingData]
    print(coachingData)
    print(KEYS)

    #apply keys before sending
    coachingData = [{k: entry[k] for k in KEYS} for entry in coachingData]

    return coachingData
    

def Coaching_Record_Modify(crequestID:int, form:object=None, scope:str="full",modification:str="") -> bool:
    
    """ modifies coaching records using "full" or "quick" method, takes CoachingForm object"""

    db = get_database()
    cur = db.cursor()

    #quick modifications
    if scope == "quick":
        try:
            record = Coaching_Query("admin", crequestID=crequestID)
            match modification:
                case "delivered":
                    cur.execute("UPDATE CoachingRequests SET delivered = NOT delivered WHERE crequestID = ?", (crequestID))
                case "paid":
                    cur.execute("UPDATE CoachingRequests SET paid = NOT paid WHERE crequestID = ?", (crequestID))
                case "delete":
                    cur.execute("DELETE FROM CoachingRequests WHERE crequestID = ?",(crequestID,))
                case _:
                    print("Invalid Case, no modification made")
                    return False           
            db.commit()
            print("minor modification successful")
            return True
        except Exception as e:
            print(f"quick modification of crequest ({crequestID}) result in an error: ", e)
            return False

    #full record edits 
    elif scope == "full" and form is not None:
        username = form.username.data
        email = form.email.data
        xboxname = form.xboxname.data
        arenarank = form.arenarank.data
        sessiontype = form.sessiontype.data
        coach = form.coach.data
        timezone = form.timezone.data
        agreedtime = form.agreedtime.data
        delivered = form.delivered.data
        paid = form.paid.data
        invoiceID = form.invoiceID.data

        #json fields
        trackernetwork:str = form.trackernetwork.data
        timeslots:list[list[bool]] = [form.monday.data, form.tuesday.data, form.wednesday.data, form.thursday.data, form.friday.data, form.saturday.data, form.sunday.data]
        details:str= form.details.data
        
        try:

            cur.execute("""
                UPDATE CoachingRequests SET username = ?, email = ?, xboxname = ?, arenarank = ?, sessiontype = ?, coach = ?, timezone = ?, agreedtime = ?, delivered = ?, paid = ?, invoiceID = ?)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, email, xboxname, arenarank, sessiontype, coach, timezone, agreedtime, delivered, paid, invoiceID))
                
            if not Coaching_Save_JSON(crequestID, timeslots, timezone, details):
                return False

            db.commit()
            print(f"coaching request modified and saved")
            return True
        
        except Exception as e:
            db.rollback()
            print("couldnt update request: ", e)
            return False
    else:
        print("invalid request")
        return False
    
#todo
def Coaching_Record_Add_Docx(file) -> bool:
    pass

def Register_New_Coaching_Request(form:object) -> bool:

    userID:int = session.get('userID', 0)
    username:str = session.get('username', form.username.data)     
    sessiontype:str = form.sessiontype.data
    coach:str = "Vanadam"
    timezone:str = form.timezone.data
    email:str = form.email.data
    xboxname:str = form.xboxname.data
    arenarank:str = form.arenarank.data
    trackernetwork:str = form.trackernetwork.data
    timeslots:list[list[bool]] = [form.monday.data, form.tuesday.data, form.wednesday.data, form.thursday.data, form.friday.data, form.saturday.data, form.sunday.data]
    details:str= form.details.data

    try:
        db = get_database()
        cur = db.cursor()
        cur.execute("""
                INSERT INTO CoachingRequests (userID, username, sessiontype, coach, timezone, email, xboxname, arenarank)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (userID, username, sessiontype, coach, timezone, email, xboxname, arenarank))
        
        
        crequestID = cur.lastrowid
        print(crequestID)
        
        if not Coaching_Save_JSON(crequestID, timeslots, timezone, details):
            return False

        print(f"new coaching request saved {crequestID} by {username}")
        db.commit()
        return True
    
    except Exception as e:
        db.rollback()
        print("couldnt add request to database: ", e)
        return False


#TODO
def Coaching_Save_JSON(crequestID:int, availability:list[list[bool]], timezone:str, details:str) -> bool:
    
    """ takes crequestID / availability / timezone / details and saved into JSON format as {crequestID}.JSON"""
    
    fileSaveLocation = f"{CoachingJSON_dir}/{crequestID}.json"

    data = {"crequestID": crequestID,
            "timezone" : timezone,
            "availability" : availability,
            "details" : details
            }
   
    json_str = json.dumps(data, indent=4)

    try:  
        with open(fileSaveLocation, "w") as f:
            f.write(json_str)
        return True
    except Exception as e:
        print("could not write to crequest to JSON", e)
        return False
        


def Coaching_Load_JSON(userID:int, requestID:int) -> dict:
    """ Looks in Dir for associated coaching request JSON"""
    
    pass 

    jsonfile = {
        "tuesday" : [None,None,None,None], 
        "wednesday" : [None,None,None,None], 
        "thursday" : [None,None,None,None],
        "friday" : [None,None,None,None],
        "saturday" : [None,None,None,None],
        "sunday" :  [None,None,None,None],
        "notes" : ""
    }
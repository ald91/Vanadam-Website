import json
import os
from flask import session
from .db import get_database
from app.forms import CoachingForm, YouTubeReviewForm

#directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/admin -> parent
data_dir = os.path.join(base_dir, "data")
CoachingJSON_dir = os.path.join(data_dir,"Coaching")

def coaching_query(who:str="self", userID:int=-1, crequestID:int=-1) -> list[dict]: 
    """ Queries COACHING table and returns any active coaching requests for that specific user. user who = "self" or who = "admin" for customization"""
    keys = { "crequestID", "crequestTime", "userID", "username", "sessiontype", "coach","agreeddate", "agreedtime", "delivered", "paid", "email", "xboxname", "arenarank",  "invoiceID" }
    JSON_keys = { "availability", "trackernetwork", "details", "timezone" }
    valid_who = {"self" , "admin"}
    coaching_data = None

    db = get_database()
    cur = db.cursor()

    if who not in valid_who:
        raise ValueError("Invalid 'who' Value supplied only valid inputs are: ",valid_who)

    #send all records
    if userID == -1 and who == "admin":
        cur.execute("SELECT * FROM CoachingRequests ORDER BY crequesttime DESC")
        coaching_data = cur.fetchall()
    #send specific record (As admin)
    elif userID == -1 and who == "admin" and crequestID > 0:
        cur.execute("SELECT * FROM CoachingReuqests WHERE crecordID = ?", (crequestID,))
        coaching_data = cur.fetchone()
    #send records for a specific user
    elif isinstance(userID, int):
        cur.execute("SELECT * FROM CoachingRequests WHERE userID = ?", (userID,))
        coaching_data = cur.fetchall()
    else:
        print("invalid request")
        return False
    
    coaching_data = [dict(row) for row in coaching_data]

    if crequestID > 0 and who == "admin":
        jsondata = coaching_load_JSON(crequestID)
        keys = keys.union(JSON_keys)
        coaching_data = [{**crecord, **jsondata} for crecord in coaching_data]

    #apply keys before sending
    coaching_data = [{k: entry[k] for k in keys} for entry in coaching_data]
    print(coaching_data)
    return coaching_data

def coaching_record_modify_quick(crequestID, action):

    """ performs simply boolean or delete's of CoachingReuqests table"""
    db = get_database()
    cur = db.cursor()
    try:
        print ("ID sent for modification: ", crequestID)

        match action:
            case "delivered":
                print(f"attempting {action} of crequest id = {crequestID}")
                cur.execute("UPDATE CoachingRequests SET delivered = NOT delivered WHERE crequestID = ?", (crequestID,))
            case "paid":
                print(f"attempting {action} of crequest id = {crequestID}")
                cur.execute("UPDATE CoachingRequests SET paid = NOT paid WHERE crequestID = ?", (crequestID,))
            case "delete":
                print(f"attempting {action} of crequest id = {crequestID}")
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

def coaching_record_modify(crequestID:int, form:object) -> bool:
    """ modifies coaching records using "full" or "quick" method, takes CoachingForm object"""
    db = get_database()
    cur = db.cursor()
   
    username = form.username.data.strip() if form.username.data !="" else None
    email = form.email.data
    xboxname = form.xboxname.data if form.xboxname.data !="" else None
    arenarank = form.arenarank.data
    sessiontype = form.sessiontype.data
    coach = "Vanadam"
    agreedtime = form.agreedtime.data if form.agreedtime.data !="" else None
    agreeddate = form.agreeddate.data if form.agreeddate.data !="" else None
    delivered = form.delivered.data or 0
    paid = form.paid.data or 0
    invoiceID = form.invoiceID.data

    #json fields
    trackernetwork = form.trackernetwork.data or None
    timezone = form.timezone.data 
    details = form.details.data

    monday = {
        "morning": form.monday.morning.data,
        "afternoon": form.monday.afternoon.data,
        "evening": form.monday.evening.data,
        "late": form.monday.late.data,
    }
    tuesday = {
        "morning": form.tuesday.morning.data,
        "afternoon": form.tuesday.afternoon.data,
        "evening": form.tuesday.evening.data,
        "late": form.tuesday.late.data,
    }
    wednesday = {
        "morning": form.wednesday.morning.data,
        "afternoon": form.wednesday.afternoon.data,
        "evening": form.wednesday.evening.data,
        "late": form.wednesday.late.data,
    }
    thursday = {
        "morning": form.thursday.morning.data,
        "afternoon": form.thursday.afternoon.data,
        "evening": form.thursday.evening.data,
        "late": form.thursday.late.data,
    }
    friday = {
        "morning": form.friday.morning.data,
        "afternoon": form.friday.afternoon.data,
        "evening": form.friday.evening.data,
        "late": form.friday.late.data,
    }
    saturday = {
        "morning": form.saturday.morning.data,
        "afternoon": form.saturday.afternoon.data,
        "evening": form.saturday.evening.data,
        "late": form.saturday.late.data,
    }
    sunday = {
        "morning": form.sunday.morning.data,
        "afternoon": form.sunday.afternoon.data,
        "evening": form.sunday.evening.data,
        "late": form.sunday.late.data,
    }

    availability = { "monday" : monday, "tuesday": tuesday, "wednesday" : wednesday, "thursday" : thursday, "friday" : friday, "saturday": saturday, "sunday": sunday }
    
    try:

        cur.execute(""" UPDATE CoachingRequests SET username = ?, email = ?, xboxname = ?, arenarank = ?, sessiontype = ?, coach = ?, agreedtime = ?, agreeddate = ?, delivered = ?, paid = ?, invoiceID = ?
            WHERE crequestID = ?""", (username, email, xboxname, arenarank, sessiontype, coach, agreedtime, agreeddate, delivered, paid, invoiceID, crequestID))
        
        print("availability:", availability)
        print("trackernetwork:", trackernetwork)
        print("timezone:", timezone)
        print("details:", details)

        if not coaching_save_JSON(crequestID, availability, trackernetwork, timezone, details):
            print('couldnt update JSON')
            raise ValueError("Failed to Save to JSON")

        db.commit()
        print(f"coaching request modified and saved")
        return True   
    except Exception as e:
        db.rollback()
        print("couldnt update request: ", e)
        return False

def register_new_coaching_request(form:object) -> bool:
    """ registers a new coaching request in the DB"""
    userID:int = session.get('userID', 0)
    username:str = session.get('username', 'not provided')     
    sessiontype:str = form.sessiontype.data
    coach:str = "Vanadam"
    timezone:str = form.timezone.data
    email:str = form.email.data
    xboxname:str = form.xboxname.data
    arenarank:str = form.arenarank.data
    trackernetwork:str = form.trackernetwork.data
   
    monday = {
        "morning": form.monday.morning.data,
        "afternoon": form.monday.afternoon.data,
        "evening": form.monday.evening.data,
        "late": form.monday.late.data,
    }

    tuesday = {
        "morning": form.tuesday.morning.data,
        "afternoon": form.tuesday.afternoon.data,
        "evening": form.tuesday.evening.data,
        "late": form.tuesday.late.data,
    }

    wednesday = {
        "morning": form.wednesday.morning.data,
        "afternoon": form.wednesday.afternoon.data,
        "evening": form.wednesday.evening.data,
        "late": form.wednesday.late.data,
    }

    thursday = {
        "morning": form.thursday.morning.data,
        "afternoon": form.thursday.afternoon.data,
        "evening": form.thursday.evening.data,
        "late": form.thursday.late.data,
    }

    friday = {
        "morning": form.friday.morning.data,
        "afternoon": form.friday.afternoon.data,
        "evening": form.friday.evening.data,
        "late": form.friday.late.data,
    }

    saturday = {
        "morning": form.saturday.morning.data,
        "afternoon": form.saturday.afternoon.data,
        "evening": form.saturday.evening.data,
        "late": form.saturday.late.data,
    }

    sunday = {
        "morning": form.sunday.morning.data,
        "afternoon": form.sunday.afternoon.data,
        "evening": form.sunday.evening.data,
        "late": form.sunday.late.data,
    }

    availabilty = { "monday" : monday, "tuesday": tuesday, "wednesday" : wednesday, "thursday" : thursday, "friday" : friday, "saturday": saturday, "sunday": sunday }

    details:str= form.details.data

    try:
        db = get_database()
        cur = db.cursor()
        cur.execute("""
                INSERT INTO CoachingRequests (userID, username, sessiontype, coach, email, xboxname, arenarank)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (userID, username, sessiontype, coach, email, xboxname, arenarank))
        
        
        crequestID = cur.lastrowid
        print(crequestID)
        
        if not coaching_save_JSON(crequestID, availabilty, trackernetwork, timezone, details):
            return False

        print(f"new coaching request saved {crequestID} by {username}")
        db.commit()
        return True
    
    except Exception as e:
        db.rollback()
        print("couldnt add request to database: ", e)
        return False

def coaching_save_JSON(crequestID:int, availability:dict[dict[bool]], trackernetwork, timezone:str, details:str) -> bool:
    
    """ takes crequestID / availability / timezone / details and saved into JSON format as {crequestID}.JSON"""
    
    fileSaveLocation = f"{CoachingJSON_dir}/{crequestID}.json"

    data = {"crequestID": crequestID,
            "timezone" : timezone,
            "trackernetwork": trackernetwork,
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
        
def coaching_load_JSON(crequestID:int) -> dict:
    """ Looks in Dir for associated coaching request JSON"""
    fileSaveLocation = f"{CoachingJSON_dir}/{crequestID}.json"
    try:
        with open(fileSaveLocation,"r") as f:
            data = json.load(f)

        return data
    
    except FileNotFoundError as e:
        print("could not find request file: ", e)

def coaching_form_data_prep(crequestData:dict) -> object:
    
    """ takes a db entry from CoachingRequests with JSON data added in and preps for form prefill on admin dash"""
    print(crequestData)


    form = CoachingForm()
    
    form.username.data = crequestData["username"]
    form.email.data = crequestData["email"]
    form.sessiontype.data = crequestData["sessiontype"]
    form.coach.data = crequestData["coach"]
    form.timezone.data = crequestData["timezone"]
    form.xboxname.data = crequestData["xboxname"]
    form.arenarank.data = crequestData["arenarank"]
    form.timezone.data = crequestData["timezone"]
    form.agreeddate.data = crequestData["agreeddate"]
    form.agreedtime.data = crequestData["agreedtime"]
    form.paid.data = crequestData["paid"]
    form.delivered.data = crequestData["delivered"]
    
    #should be loaded from JSON
    form.trackernetwork.data = crequestData["trackernetwork"]
    form.details.data = crequestData["details"]
    
    # Monday
    form.monday.morning.data   = crequestData["availability"]["monday"]["morning"]
    form.monday.afternoon.data = crequestData["availability"]["monday"]["afternoon"]
    form.monday.evening.data   = crequestData["availability"]["monday"]["evening"]
    form.monday.late.data      = crequestData["availability"]["monday"]["late"]

    # Tuesday
    form.tuesday.morning.data   = crequestData["availability"]["tuesday"]["morning"]
    form.tuesday.afternoon.data = crequestData["availability"]["tuesday"]["afternoon"]
    form.tuesday.evening.data   = crequestData["availability"]["tuesday"]["evening"]
    form.tuesday.late.data      = crequestData["availability"]["tuesday"]["late"]

    # Wednesday
    form.wednesday.morning.data   = crequestData["availability"]["wednesday"]["morning"]
    form.wednesday.afternoon.data = crequestData["availability"]["wednesday"]["afternoon"]
    form.wednesday.evening.data   = crequestData["availability"]["wednesday"]["evening"]
    form.wednesday.late.data      = crequestData["availability"]["wednesday"]["late"]

    # Thursday
    form.thursday.morning.data   = crequestData["availability"]["thursday"]["morning"]
    form.thursday.afternoon.data = crequestData["availability"]["thursday"]["afternoon"]
    form.thursday.evening.data   = crequestData["availability"]["thursday"]["evening"]
    form.thursday.late.data      = crequestData["availability"]["thursday"]["late"]

    # Friday
    form.friday.morning.data   = crequestData["availability"]["friday"]["morning"]
    form.friday.afternoon.data = crequestData["availability"]["friday"]["afternoon"]
    form.friday.evening.data   = crequestData["availability"]["friday"]["evening"]
    form.friday.late.data      = crequestData["availability"]["friday"]["late"]

    # Saturday
    form.saturday.morning.data   = crequestData["availability"]["saturday"]["morning"]
    form.saturday.afternoon.data = crequestData["availability"]["saturday"]["afternoon"]
    form.saturday.evening.data   = crequestData["availability"]["saturday"]["evening"]
    form.saturday.late.data      = crequestData["availability"]["saturday"]["late"]

    # Sunday
    form.sunday.morning.data   = crequestData["availability"]["sunday"]["morning"]
    form.sunday.afternoon.data = crequestData["availability"]["sunday"]["afternoon"]
    form.sunday.evening.data   = crequestData["availability"]["sunday"]["evening"]
    form.sunday.late.data      = crequestData["availability"]["sunday"]["late"]

    return form

#for youtube requests which are still coaching

def register_new_YT_request(form:object, sessionUserID) -> bool:

    """ takes a YT request form and registers it on the YTrequests Database user must be logged in"""

    form = YouTubeReviewForm()
    username       = form.username.data
    userID         = sessionUserID
    xboxname       = form.xboxname.data
    arenarank      = form.arenarank.data
    videoURL       = form.videoURL.data
    trackernetwork = form.trackernetwork.data
    playlist       = form.playlist.data
    matchmap       = form.matchmap.data
    matchgamemode  = form.matchgamemode.data
    status         = "recieved"

    try:
        db = get_database()
        cur = db.cursor()
        cur.execute(" INSERT INTO YTRequests (username, userID, xboxname, arenarank, videoURL, trackernetwork, playlist, matchmap, matchgamemode, status) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, userID, xboxname, arenarank, videoURL, trackernetwork, playlist, matchmap, matchgamemode, status))
        db.commit()

    except Exception as e:
        print("could not add new record to Database, error: ", e)
        return False
    
    return True

def youtube_query(who="self", userID:int = -1, YTrequestID:int = -1) -> list[dict]:
 
    """ Queries YTRequests table and returns any Youtube requests for that specific user. user who = "self" or who = "admin" for customization"""

    valid_who = {"self" , "admin"}

    db = get_database()
    cur = db.cursor()

    if who not in valid_who:
        raise ValueError("Invalid 'who' Value supplied only valid inputs are: ",valid_who)

    #send all records
    if userID == -1 and who == "admin":
        cur.execute("SELECT * FROM YTRequests ORDER BY YTrequestTime DESC")
        coaching_data = cur.fetchall()
    #send specific record (As admin)
    elif userID == -1 and who == "admin" and YTrequestID > 0:
        cur.execute("SELECT * FROM YTRequests WHERE crecordID = ?", (YTrequestID,))
        coaching_data = cur.fetchone()
    #send records for a specific user
    elif isinstance(userID, int):
        cur.execute("SELECT * FROM YTRequests WHERE userID = ?", (userID,))
        coaching_data = cur.fetchall()
    else:
        print("invalid request")
        return False
    
    YT_request_data = [dict(row) for row in coaching_data]
    return YT_request_data

def YT_record_modify_quick(YTrequestID:int, action:str) -> bool :
    """ performs simple string change or delete's of record from  YTRequests table"""
    db = get_database()
    cur = db.cursor()
    try:
        print ("ID sent for modification: ", YTrequestID)

        match action:
            case "uploaded":
                print(f"attempting {action} of YTrequest id = {YTrequestID}")
                cur.execute("UPDATE YTRequests SET status = 'uploaded' WHERE YTrequestID = ?", (YTrequestID,))
            case "recorded":
                print(f"attempting {action} of YTrequest id = {YTrequestID}")
                cur.execute("UPDATE YTRequests SET status = 'recorded' WHERE YTrequestID = ?", (YTrequestID,))
            case "queued":
                print(f"attempting {action} of YTrequest id = {YTrequestID}")
                cur.execute("UPDATE YTRequests SET status = 'queued' WHERE YTrequestID = ?",(YTrequestID,))
            case "recieved":
                print(f"attempting {action} of YTrequest id = {YTrequestID}")
                cur.execute("UPDATE YTRequests SET status = 'recieved' WHERE YTrequestID = ?",(YTrequestID,))
            case "delete":
                print(f"attempting {action} of YTrequest id = {YTrequestID}")
                cur.execute("DELETE FROM YTRequests WHERE YTrequestID = ?",(YTrequestID,))
            case _:
                print("Invalid Case, no modification made")
                return False           
        db.commit()
        print("minor modification successful")
        return True
    except Exception as e:
        print(f"quick modification of crequest ({YTrequestID}) result in an error: ", e)
        return False
    
def youtube_record_modify(YTrequestID:int, form:object) -> bool:
    
    """ modifies youtube request records takes youtubeform object"""

    db = get_database()
    cur = db.cursor()

    YTrequestID = YTrequestID  
    username =          form.username.data       
    xboxname =          form.xboxname.data       
    arenarank =         form.arenarank.data      
    videoURL =          form.videoURL.data       
    trackernetwork =    form.trackernetwork.data 
    playlist =          form.playlist.data       
    matchmap =          form.matchmap.data       
    matchgamemode =     form.matchgamemode.data  
    status =            form.status.data         
    youtubevideoID =   form.youtubevideoID.data     

    try:

        cur.execute(""" UPDATE YTRequests SET username = ?, xboxname = ?, arenarank = ?, videoURL = ?, trackernetwork = ?, playlist = ?, matchmap = ?, matchgamemode = ?, status = ?, youtubevideoID = ? WHERE YTrequestID = ? """,
                     (username, xboxname, arenarank, videoURL, trackernetwork, playlist, matchmap, matchgamemode, status, youtubevideoID))

        db.commit()
        print(f"youtube request modified and saved")
        return True
    
    except Exception as e:
        db.rollback()
        print("couldnt update request: ", e)
        return False
 
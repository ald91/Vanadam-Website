#TODO:ADAM
from flask import session
import os
import json

from .db import get_database
from .db_services_users import Single_User_Query

from app.forms import CoachingForm, TimeSlotForm

#directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/admin -> parent
data_dir = os.path.join(base_dir, "data")
CoachingJSON_dir = os.path.join(data_dir,"Coaching")

def Coaching_Query(who:str="self", userID:int=-1, crequestID:int=-1) -> list[dict]:
    
    """ Queries COACHING table and returns any active coaching requests for that specific user. user who = "self" or who = "admin" for customization"""
    
    KEYS = { "crequestID", "crequestTime", "userID", "username", "sessiontype", "coach","agreeddate", "agreedtime", "delivered", "paid", "email", "xboxname", "arenarank",  "invoiceID" }
    JSON_KEYS = { "availability", "trackernetwork", "details", "timezone" }
    VALID_WHO = {"self" , "admin"}

    db = get_database()
    cur = db.cursor()

    if who not in VALID_WHO:
        raise ValueError("Invalid 'who' Value supplied only valid inputs are: ",VALID_WHO)

    #send all records
    if userID == -1 and who == "admin":
        cur.execute("SELECT * FROM CoachingRequests ORDER BY crequesttime DESC")
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

    if crequestID > 0 and who == "admin":
        jsondata = Coaching_Load_JSON(crequestID)
        KEYS = KEYS.union(JSON_KEYS)
        coachingData = [{**crecord, **jsondata} for crecord in coachingData]

    #apply keys before sending
    coachingData = [{k: entry[k] for k in KEYS} for entry in coachingData]
    print(coachingData)
    return coachingData

def Coaching_Record_Modify_Quick(crequestID, action):

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

def Coaching_Record_Modify(crequestID:int, form:object) -> bool:
    
    """ modifies coaching records using "full" or "quick" method, takes CoachingForm object"""
    print(form)

    db = get_database()
    cur = db.cursor()

    username = form.username.data
    email = form.email.data
    xboxname = form.xboxname.data
    arenarank = form.arenarank.data
    sessiontype = form.sessiontype.data
    coach = form.coach.data
    agreedtime = form.agreedtime.data
    delivered = form.delivered.data or 0
    paid = form.paid.data or 0
    invoiceID = form.invoiceID.data

    #json fields
    trackernetwork:str = form.trackernetwork.data
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

        cur.execute(""" UPDATE CoachingRequests SET username = ?, email = ?, xboxname = ?, arenarank = ?, sessiontype = ?, coach = ?, agreedtime = ?, delivered = ?, paid = ?, invoiceID = ?
            WHERE crequestID = ?""", (username, email, xboxname, arenarank, sessiontype, coach, agreedtime, delivered, paid, invoiceID, crequestID))
        
        print("availability:", availability)
        print("trackernetwork:", trackernetwork)
        print("timezone:", timezone)
        print("details:", details)

        if not Coaching_Save_JSON(crequestID, availability, trackernetwork, timezone, details):
            print('couldnt update JSON')
            raise ValueError("Failed to Save to JSON")

        db.commit()
        print(f"coaching request modified and saved")
        return True
    
    except Exception as e:
        db.rollback()
        print("couldnt update request: ", e)
        return False
 
#todo
def Coaching_Record_Add_Docx(file) -> bool:
    pass

def Register_New_Coaching_Request(form:object) -> bool:

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
        
        if not Coaching_Save_JSON(crequestID, availabilty, trackernetwork, timezone, details):
            return False

        print(f"new coaching request saved {crequestID} by {username}")
        db.commit()
        return True
    
    except Exception as e:
        db.rollback()
        print("couldnt add request to database: ", e)
        return False

def Coaching_Save_JSON(crequestID:int, availability:dict[dict[bool]], trackernetwork, timezone:str, details:str) -> bool:
    
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
        
def Coaching_Load_JSON(crequestID:int) -> dict:
    """ Looks in Dir for associated coaching request JSON"""
    fileSaveLocation = f"{CoachingJSON_dir}/{crequestID}.json"
    try:
        with open(fileSaveLocation,"r") as f:
            data = json.load(f)

        return data
    
    except FileNotFoundError as e:
        print("could not find request file: ", e)

def Coaching_Form_Data_Prep(crequestData:dict) -> object:
    
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

#TODO:ADAM
from .db import get_database
from .db_services_users import Single_User_Query


def Coaching_Query(who:str="self", userID:int=None) -> list[dict]:
    
    """ Queries COACHING table and returns any active coaching requests for that specific user. user who = "self" or who = "admin" for customization"""
    
    SELF_KEYS = { "crequestID", "userID", "username", "sessiontype", "coach", "timezone", "agreedtime", "delivered", "paid", "email", "xboxname", "arenarank"}
    ADMIN_KEYS = { "invoiceID", "json" }
    VALID_WHO = {"self" , "admin"}

    db = get_database()
    cur = db.cursor()

    if who not in VALID_WHO:
        raise ValueError("Invalid 'who' Value supplied only valid inputs are: ",VALID_WHO)

    if who == "admin":
        KEYS = SELF_KEYS.union(ADMIN_KEYS)

    elif who == "self":
        KEYS = SELF_KEYS

    if userID == None and who == "admin":
        cur.execute("SELECT * FROM Coaching")
    
    elif isinstance(userID, int):
        cur.execute("SELECT * FROM Coaching WHERE userID = ?", (userID,))

    coachingData = cur.fetchall()
    coachingData = [dict(row) for row in coachingData]

    #apply keys before sending
    coachingData = [{k: entry[k] for k in KEYS} for entry in coachingData]

    return coachingData
    

def Register_New_Coaching_Request(form:object) -> bool:

    #crequestID = None
    userID = session["userID"] | None
    username = form.username.data    
    sessiontype = form.sessiontype.data
    coach = "Vanadam"
    timezone = form.timezone.data
    email = form.email.data
    xboxname = form.xboxname.data
    arenarank = form.arenarank.data

    try:
        db = get_database()
        cur = db.cursor()
        cur.execute("INSERT INTO Coaching (username = ?, sessiontype = ?, coach = ?, timezone = ?, email = ?, xboxname = ?, arenarank = ?)", 
                    (username, sessiontype, coach, timezone, email, xboxname, arenarank))
        Create_Coaching_JSON
        return True
    
    except Exception as e:
        print("couldnt add request to database: ", e)

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
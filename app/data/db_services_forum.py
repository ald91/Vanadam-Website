from db import get_database
#TODO:RYAN
def User_Posts_Query(who:str="self", userID:int=0) -> list[dict]:
    """ Queries MESSAGES table and returns all currently active forum messages"""
    db = get_database()
    cursor = db.cursor()

    query = "SELECT * FROM Messages"
    pass
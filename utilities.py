from datetime import datetime

#when pulling [{dicts}] from DB you can use this function to mass convert the ISO date into a readable format
def format_date_from_ISO_DB(Dbpull):
    
    """ converts lists of {dicts} from SQLite.row_factory DB pulls ISO8001 dates into readable dates for humans"""

    for row in Dbpull:
        iso = row["published"]
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        row["published"] = dt.strftime("%d %b %Y")
    return Dbpull

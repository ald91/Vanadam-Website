#Flask
from flask import g

#Databases
import sqlite3, os, hashlib, base64

#internal imports
import dbconstructor 



dbpath = "database.db"
if not os.path.exists(dbpath):
    dbconstructor.create_database()



def get_database():
    if 'db' not in g:
        dbpath = "database.db"
        if not os.path.exists(dbpath):
            dbconstructor.create_database()

        g.db = sqlite3.connect("database.db")
        g.db.row_factory = sqlite3.Row

        print("Connected to database!")
    return g.db
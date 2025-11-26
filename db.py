#Flask
from flask import g

#Databases
import sqlite3, os, hashlib, base64

def get_database():
    if 'db' not in g:
        dbpath = "database.db"
        if not os.path.exists(dbpath):

        g.db = sqlite3.connect("database.db")
        g.db.row_factory = sqlite3.Row

        print("Connected to database!")
    return g.db
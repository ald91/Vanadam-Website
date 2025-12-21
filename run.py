# run.py
from app import app_create
from app.data import db
from flask import g

app = app_create()

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(host="0.0.0.0", port=81)
# run.py
from app import app_create
from app.data import db
from flask import g

app = app_create()

#This route is called at the end of a request, removing db connection from g, ready for the next request
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(host="0.0.0.0", port=81)
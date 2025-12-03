# run.py
from app import app_create

app = app_create()

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(host="0.0.0.0", port=81)
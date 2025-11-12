from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_testing_only")
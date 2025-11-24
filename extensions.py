from flask import Flask
from flask_mail import Mail
from flask_wtf import FlaskForm, CSRFProtect
from flask_session import Session

import os, hashlib
from dotenv import load_dotenv

import os

#security and config
app = Flask(__name__)
app.config.from_pyfile("config.py")
load_dotenv()

#email functionality 
mail = Mail(app)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# temp folder for storing session files (make SQL?)
SESSION_DIR = './flask_session'
os.makedirs(SESSION_DIR, exist_ok=True)

#cross site protection
csrf = CSRFProtect(app)
Session(app)

#hash object
hash = hashlib.sha256()



app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_testing_only")
app.security_password_salt = os.environ.get('SECURITY_PASSWORD_SALT')




print("MAIL_SERVER:", app.config['MAIL_SERVER'])
print("MAIL_PORT:", app.config['MAIL_PORT'])
print("MAIL_USERNAME:", app.config['MAIL_USERNAME'])
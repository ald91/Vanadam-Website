#Flask
from flask import Flask
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_wtf import CSRFProtect


#Security
from itsdangerous import URLSafeTimedSerializer
import os, hashlib

#Sessions
from flask_session import Session

from dotenv import load_dotenv

#security and config
app = Flask(__name__)
app.config.from_pyfile("config.py")
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_testing_only")
app.security_password_salt = os.environ.get('SECURITY_PASSWORD_SALT')
securitySalt = app.security_password_salt

#password recovery serializer
serializer = URLSafeTimedSerializer(app.secret_key)

#load environment variables
load_dotenv()

#Apply config settings from our file
app.config.from_object('config')
DEBUG_MODE = False

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

#Set upload location for article thumbnails
UPLOAD_FOLDER = 'static/Assets/articleThumbs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Run application
#=========================================================
# This code executes when the script is run directly.
if __name__ == '__main__':
    print("Starting Flask application...")
    print("Open Your Application in Your Browser: http://localhost:81")
    # The app will run on port 81, accessible from any local IP address
    app.run(host='0.0.0.0', port=81)

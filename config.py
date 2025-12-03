# App Configuration
import os


# =========================
# flask
# =========================

#flask_sessions
SESSION_COOKIE_NAME = "Vanadam Halo"  # optional custom cookie name
SESSION_DIR = './flask_session'      # directory for session files
SESSION_PERMANENT = False #session persistance
SESSION_USE_SIGNER = True            # sign session ID for security
PERMANENT_SESSION_LIFETIME = 86400 # time a session is valid for using cookies (seconds)
SESSION_TYPE = "filesystem" #Store session data on the filesystem

#SECRET KEY
SECRET_KEY= '42ccfba0cfc3bb634078bddd17f4ade1584bf1047d468832006aef75f7d5148f'
DEV_KEY_FOR_TESTING_ONLY= '416e63ffc59b683f9e5eaf1c1d1307a229ce3a96e07fc986f4eb0d6d92f6f102'
SECURITY_PASSWORD_SALT= '81e140bf3a006c8e5eb38e23bfc93fe3'

#flask_mail
MAIL_SERVER = os.environ.get('MAIL_SERVER') 
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
MAIL_USERNAME =  os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')

#flask_debug_mode
DEBUG = True


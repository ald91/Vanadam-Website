# App Configuration
import os


# =========================
# flask
# =========================

#flask_sessions
SESSION_COOKIE_NAME = "vanadam"  # optional custom cookie name
SESSION_DIR = './flask_session'      # directory for session files
SESSION_PERMANENT = False #session persistance
SESSION_USE_SIGNER = True            # sign session ID for security
PERMANENT_SESSION_LIFETIME = 86400 # time a session is valid for using cookies (seconds)
SESSION_TYPE = "filesystem" #Store session data on the filesystem

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


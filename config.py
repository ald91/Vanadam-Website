# App Configuration

# =========================
# flask
# =========================

#sessions
SESSION_COOKIE_NAME = "vanadam"  # optional custom cookie name
SESSION_DIR = './flask_session'      # directory for session files
SESSION_PERMANENT = False #session persistance
SESSION_USE_SIGNER = True            # sign session ID for security
PERMANENT_SESSION_LIFETIME = 86400 # time a session is valid for using cookies (seconds)
SESSION_TYPE = "filesystem" #Store session data on the filesystem

#debugging
DEBUG = True

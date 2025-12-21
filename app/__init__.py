#Flask
from flask import Flask, session
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_apscheduler import APScheduler

#Security
from itsdangerous import URLSafeTimedSerializer

#python modules
import os, hashlib

#Sessions
from flask_session import Session
from app.services import clear_stale_posts

#env file loader
from dotenv import load_dotenv

#import modules
from .auth import auth
from .content import content
from .forum import forum
from .admin import admin
from .data import data
from .HaloData import *
from .data.db import g
from .extensions import mail, serializer, security_salt

scheduler = APScheduler()

def app_create():
    app = Flask(__name__)

    #load environment variables
    load_dotenv()
    DEBUG_MODE = True

    #config
    app.config.from_object("config")
    app.secret_key = os.environ.get("SECRET_KEY", app.config.get("SECRET_KEY"))
    
    #cross site protection
    CSRFProtect(app)
    mail.init_app(app)

    #security items
    serializer = URLSafeTimedSerializer(app.secret_key)
    hash = hashlib.sha256()

    #email functionality 
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

    #Set upload location for article thumbnails
    UPLOAD_FOLDER = 'static/Assets/articleThumbs'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Register all modules
    load_modules(app)

    #Inject required data for navbar for all routes
    @app.context_processor
    def inject_nav_data():
        return {
            "HALO_INFINITE_DATA": HALO_INFINITE_DATA,
            "DEBUG_MODE" : DEBUG_MODE
    }

    # This route is called at the end of a request, removing db connection from g, ready for the next request
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    #Scheduling for automated tasks
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(
        id='clear_stale_posts',
        func=clear_stale_posts,
        trigger='interval',
        minutes=30
    )

    print(app.url_map)

    return app


def load_modules(app):
    #prevents circular imports for db routes.py
    app.register_blueprint(content) # lists site as '/'
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(forum, url_prefix="/forums")
    app.register_blueprint(data, url_prefix="/data")
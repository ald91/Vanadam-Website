from flask import Flask

#initiates primary flask instance
def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    #import each blueprint
    from .auth import auth
    from .content import content
    from .forum import forum
    from .admin import admin

    # Register module blueprints
    app.register_blueprint(content) # lists site as '/'
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(forum, url_prefix="/forum")
    app.register_blueprint(admin, url_prefix="/admin")

    return app
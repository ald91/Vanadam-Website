from flask import Flask

#initiates primary flask instance
def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    #import each blueprint
    from app.auth.routes import auth
    from app.site.routes import site
    from app.forum.routes import forum
    from app.admin.routes import admin

    # Register module blueprints
    app.register_blueprint(site) # lists site as '/'
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(forum, url_prefix="/forum")
    app.register_blueprint(admin, url_prefix="/admin")

    return app
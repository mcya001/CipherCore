from flask import Flask
from .routes.auth import auth_bp
from .routes.messages import messages_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.register_blueprint(auth_bp)
    app.register_blueprint(messages_bp)

    return app
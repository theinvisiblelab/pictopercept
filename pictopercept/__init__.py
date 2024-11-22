from flask import Flask, render_template, session
from flask_wtf import CSRFProtect

from .views import main_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('pictopercept.config.Config')
    app.register_blueprint(main_routes)
    CSRFProtect(app)
    return app

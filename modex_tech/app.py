#!/usr/bin/python3
"""
Main Flask application file for Modex Technologies.
This file initializes the Flask app and registers all Blueprints.
"""

from flask import Flask, session,  redirect, url_for, request, g  
from config import Config
from routes import blueprints
from extensions import db, login_manager, mail
from sqlalchemy import text
from models import User
from datetime import timedelta, datetime, date, timezone  # ✅ Add datetime imports


# Global timeout config
SESSION_TIMEOUT = timedelta(minutes=15)
LAST_CHECKED_DATE = None


def register_blueprints(app):
    """
    Registers all Blueprints from the routes module.
    Supports both plain Blueprint objects and (Blueprint, url_prefix) tuples.
    """
    for bp in blueprints:
        if isinstance(bp, tuple):
            app.register_blueprint(bp[0], url_prefix=bp[1])
        else:
            app.register_blueprint(bp)

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'process.logout'

    mail.init_app(app)
    app.extensions['mail'] = mail
    register_blueprints(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(process_id=user_id).first()

    # ✅ Session timeout logic
    @app.before_request
    def check_session_timeout():
        g.tables_used = set()
        exempt_routes = ["pages.maintenance","pages.printing", "pages.signin","pages.signup", "process.logout"]
        now = datetime.now(timezone.utc)  # Always timezone-aware
        last_activity = session.get('last_activity')
        # 🔥 Fix: handle missing session value
        if last_activity is None:
            session['last_activity'] = now
            return  # allow request to proceed
        # If stored as string, convert (common mistake)
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        if (now - last_activity) > SESSION_TIMEOUT:
            session.clear()
            return redirect(url_for('process.logout'))
        # update activity
        session['last_activity'] = now

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

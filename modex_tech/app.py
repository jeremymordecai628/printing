#!/usr/bin/python3
"""
Main Flask application file for Ressen Technologies.
This file initializes the Flask app and registers all Blueprints.
"""

from flask import Flask, session,  redirect, url_for, request, g  
from config import Config
from routes import blueprints
from extensions import db, login_manager, mail
from sqlalchemy import text
from models import Staff
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
    login_manager.login_view = 'auth.login'

    mail.init_app(app)
    app.extensions['mail'] = mail
    
    @login_manager.user_loader
    def load_user(user_id):
        return Staff.query.filter_by(process_id=user_id).first()

    # ✅ Session timeout logic
    @app.before_request
    def check_session_timeout():
        g.tables_used = set()
        exempt_routes = ["auth.callback","auth.access", "auth.confirmation", "auth.dashboard",
                         "auth.login","auth.logout","auth.get_notification","auth.manage_display",
                         "auth.register","auth.validation","public.about","public.cirricular",
                         "public.contact","public.faq","public.galary","public.home","public.login_page","public.perfomance", "static"]
        now = datetime.now(timezone.utc)  # Always timezone-aware
        last_activity = session.get("last_activity")

        if  request.endpoint in exempt_routes:
            # Update last activity
            session["last_activity"] = now.isoformat()
            return None 

        # Prefer last_activity, else fall back to initial_activity
        if  last_activity:
            # Only parse if it's a string
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity)

        if (now - last_activity) > SESSION_TIMEOUT:
            return redirect(url_for("auth.logout")) 

        # Update last activity
        session["last_activity"] = now.isoformat()

    register_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


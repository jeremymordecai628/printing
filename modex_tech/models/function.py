#!/usr/bin/python3
"""
utils.py

Common utility functions for Flask application:
- Authentication helpers
- File handling
- Email sending
- Security helpers
- System detection
"""

import os
import hashlib
import secrets
import string
import smtplib
import platform

from functools import wraps
from urllib.parse import urlparse, urljoin
from email.mime.text import MIMEText

from flask import session, redirect, url_for, flash, request
from flask_login import current_user


# =========================
# FILE HANDLING
# =========================

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'doc', 'docx',
    'xml', 'xlsx', 'pptx', 'pdf', 'txt'
}


def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# USER HELPERS
# =========================

def user_id():
    """
    Get current logged-in user ID.
    """
    if current_user.is_authenticated:
        return current_user.get_id()
    return None


def hash_value(value: str) -> str:
    """
    Hash a string using SHA-256.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# =========================
# AUTH DECORATORS
# =========================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required", "error")
            return redirect(url_for("signin", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session or session["role"] not in roles:
                flash("Access denied", "error")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


# =========================
# SECURITY
# =========================

def is_safe_url(target: str) -> bool:
    """
    Validate redirect URL safety.
    """
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


# =========================
# FILE SYSTEM HELPERS
# =========================

def get_images(app, folder: str):
    """
    Get images from static/images/<folder>

    Args:
        app: Flask app instance
        folder: folder name inside images
    """
    path = os.path.join(app.static_folder, "images", folder)

    if not os.path.exists(path):
        return []

    return [
        f for f in os.listdir(path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]


# =========================
# EMAIL SENDING
# =========================

def send_email(recipient_email: str, subject: str, body: str):
    """
    Send email using SMTP from environment variables.
    """

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = MAIL_USERNAME
    msg["To"] = recipient_email

    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls()

        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, [recipient_email], msg.as_string())
        server.quit()

        return "Email sent successfully"

    except Exception as e:
        return f"Failed: {str(e)}"


# =========================
# CODE GENERATION
# =========================

def generate_unique_code(length: int = 8) -> str:
    """
    Generate secure alphanumeric code.
    """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# =========================
# DATABASE CHECK (PyMySQL)
# =========================

def user_exists_with_media_role(conn, user_id: int) -> bool:
    """
    Check if user exists with role 'media'
    """
    sql = "SELECT 1 FROM users WHERE id = %s AND role = %s LIMIT 1"

    with conn.cursor() as cursor:
        cursor.execute(sql, (user_id, "media"))
        return cursor.fetchone() is not None


# =========================
# SYSTEM DETECTION
# =========================

def detect_os():
    """
    Detect client OS from user agent.
    """
    ua = request.user_agent.platform

    return {
        "windows": "windows",
        "linux": "linux",
        "macos": "macos",
        "android": "android"
    }.get(ua, None)


def detect_arch():
    """
    Detect CPU architecture.
    """
    machine = platform.machine().lower()

    if "arm" in machine:
        return "arm64"
    return "x64"

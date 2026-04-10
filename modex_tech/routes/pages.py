#!/usr/bin/env python3
"""
pages blueprint (Flask-SQLAlchemy version)
"""

import os
import traceback
import subprocess
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request, redirect,
    session, url_for, flash
)

from db import db
from models import User, PromoCode, Payment

from utils import (
    get_images,
    login_required,
    hash_value,
    generate_unique_code,
    user_exists_with_media_role,
    send_email
)

pages_bp = Blueprint('pages', __name__)


# =========================
# HOME
# =========================

@pages_bp.route("/")
def home():
    return render_template(
        "index.html",
        maintenance_imgs=get_images(request.app, "maintainance"),
        printing_imgs=get_images(request.app, "cyber"),
        game_imgs=get_images(request.app, "games"),
        library_imgs=get_images(request.app, "store"),
        support_imgs=get_images(request.app, "customer_care")
    )


# =========================
# STATIC PAGES
# =========================

@pages_bp.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")


@pages_bp.route("/printing")
@login_required
def printing():
    return render_template("print.html")


@pages_bp.route("/networking")
def networking():
    return render_template("networking.html")


# =========================
# LIST DATA (ORM VERSION)
# =========================

@pages_bp.route("/pages_bgs")
@login_required
def pages_bgs():
    data = Payment.query.filter_by(status="active").all()
    return render_template("pages_bg.html", pages_bgs=data)


# =========================
# ADMIN PANEL
# =========================

@pages_bp.route("/admin", methods=["GET", "POST"])
def admin():
    file_info = None

    if request.method == "POST":
        repo = request.form.get("link_value")
        initiate = request.form.get("value")
        doc_id = request.form.get("doc_id")

        try:
            # =========================
            # 1. CREATE PROMO CODE
            # =========================
            if initiate:
                user = session.get("user_id")
                future_date = datetime.now() + timedelta(days=30)

                if user_exists_with_media_role(db.engine.raw_connection(), user):
                    promo = PromoCode(
                        user_id=user,
                        code=generate_unique_code(),
                        expires_at=future_date
                    )
                    db.session.add(promo)
                    db.session.commit()
                    flash("Promo code created successfully", "success")
                else:
                    flash("Unauthorized: role must be media", "error")


            # =========================
            # 2. GIT CLONE
            # =========================
            elif repo:
                destination = os.getenv("REPO_BASE_PATH")

                if not destination:
                    flash("Destination folder not set", "error")
                else:
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    result = subprocess.run(
                        ["git", "clone", repo, destination],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        flash(f"Git clone failed: {result.stderr}", "error")
                    else:
                        flash(f"Repository cloned to {destination}", "success")


            # =========================
            # 3. FETCH PAYMENT INFO
            # =========================
            elif doc_id:
                result = Payment.query.get(doc_id)

                if not result:
                    flash("Record not found", "error")
                else:
                    if not os.path.exists(result.file_name):
                        flash("File not found", "error")
                    else:
                        file_info = {
                            "charges": getattr(result, "charges", None),
                            "amount_paid": getattr(result, "amount_paid", None),
                            "status": result.status,
                            "file_path": result.file_name
                        }
                        flash("File ready", "success")

            else:
                flash("Invalid input", "error")

            return render_template("admin.html", file_info=file_info)

        except Exception as e:
            traceback.print_exc()
            flash(str(e), "error")

    return render_template("admin.html", file_info=file_info)


# =========================
# LOGIN
# =========================

@pages_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        next_page = request.form.get("next")

        hashed_password = hash_value(password)

        user = User.query.filter_by(user_name=username).first()

        if not user:
            flash("Invalid credentials", "danger")
            return redirect(url_for("pages.signin"))

        if user.password == hashed_password:
            session["user_id"] = user.id
            session["username"] = user.user_name
            session["role"] = user.role

            flash("Login successful", "success")
            return redirect(next_page or url_for("pages.home"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("pages.signin"))

    return render_template("signin.html")


# =========================
# SIGNUP
# =========================

@pages_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            hashed = hash_value(password)

            user = User(
                user_name=email,
                password=hashed,
                role="customer"
            )

            db.session.add(user)
            db.session.commit()

            send_email(
                email,
                "Welcome to Ressen Technologies",
                "<h3>Account created successfully</h3>"
            )

            flash("Account created successfully", "success")
            return redirect(url_for("pages.signin"))

        except Exception as e:
            traceback.print_exc()
            flash(str(e), "error")
            return redirect(url_for("pages.home"))

    return render_template("signup.html")

#!/usr/bin/python3
"""
data.py

Flask-SQLAlchemy ORM models for school_db

"""

from extensions import db
from datetime import datetime
from enum import Enum

class StatusEnum(Enum):
    """
    Enum for user status
    """
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "Active"
    PENDING = "PENDING"
    TERMINATED = "Terminated"

class User(db.Model):
    """
    users table
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')
    registration_date=db.Column(db.DateTime,  nullable=False, default=datetime.utcnow) 

    # Relationships
    promo_codes = db.relationship('PromoCode', backref='user', lazy=True, cascade="all, delete-orphan")
    assigned_codes = db.relationship('AssignCode', backref='user', lazy=True, cascade="all, delete-orphan")


class Payment(db.Model):
    """

    payment table
    """
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    trans = db.Column(db.String(50), unique=True, nullable=True)
    services = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')


class PromoCode(db.Model):
    """
    promo_codes table
    """
    __tablename__ = 'promo_codes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, default=0)
    used_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)


class AssignCode(db.Model):
    """
    assign_code table
    """
    __tablename__ = 'assign_code'

    code = db.Column(db.String(50), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class App(db.Model):
    """
    Apps table
    """
    __tablename__ = "apps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(100), nullable=False)

    slug = db.Column(db.String(100), nullable=False)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

    active = db.Column(db.Boolean, default=True)

    package = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    status = db.Column(
        db.Enum(StatusEnum),
        nullable=False
    )

class Application(db.Model):
    """
    Application table
    """
    __tablename__ = "application"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requested_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    description = db.Column(db.Text, nullable=True)

    version = db.Column(db.String(50), nullable=True)

    status = db.Column(
        db.Enum(StatusEnum),
        nullable=False,
        default=StatusEnum.PENDING
    )

    # Relationship (one-to-many)
    apps = db.relationship(
        "App",
        backref="application",
        cascade="all, delete-orphan"
    )
class Download(db.Model):
    """
    Represents a record of a user downloading an app.
    """

    __tablename__ = "downloads"

    download_id = db.Column(
            db.String(36),
            primary_key=True,
            nullable=False
            )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    app_id = db.Column(
        db.Integer,
        db.ForeignKey("apps.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    download_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Download user_id={self.user_id} app_id={self.app_id}>"

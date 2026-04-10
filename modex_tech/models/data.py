#!/usr/bin/python3
"""
data.py

Flask-SQLAlchemy ORM models for school_db

"""

from extensions import db
from datetime import datetime

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
    apps table
    """
    __tablename__ = 'apps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

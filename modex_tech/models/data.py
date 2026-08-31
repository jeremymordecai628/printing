#!/usr/bin/python3
"""
data.py

Flask-SQLAlchemy ORM models for school_db

"""
import uuid
from extensions import db
from datetime import datetime
from enum import Enum


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
    promo_codes = db.relationship('PromoCode', backref='users', lazy=True, cascade="all, delete-orphan")
    assigned_codes = db.relationship('UserPromotions', backref='users', lazy=True, cascade="all, delete-orphan")

class Login(db.Model):
    """
    Tracks users login activity with status
    """
    __tablename__ = 'login'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    status = db.Column(db.Enum('APPROVED','REJECTED','Active','PENDING','Terminated'),nullable=False,default="PENDING") 
    login_time = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    last_login = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow)


class UserPromotions(db.Model):
    """
    Association table linking userss to promo codes
    """
    __tablename__ = 'users_promotions'

    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='CASCADE'),primary_key=True,unique=True,nullable=False)
    code = db.Column(db.String(50),db.ForeignKey('promo_codes.code', ondelete='CASCADE'),primary_key=True,unique=True,nullable=False)

    def __repr__(self):
        return f"<UserPromotions users_id={self.users_id} code={self.code}>"

class Payment(db.Model):
    """

    payment table
    """
    __tablename__ = 'payment'
    transaction_id=db.Column(db.String(50), primary_key=True)
    amount=db.Column(db.Float,nullable=False)
    phone_number=db.Column(db.String(50),nullable=False)
    account_number=db.Column(db.String(100),db.ForeignKey('gift_registrations.account',ondelete='CASCADE'),nullable=False)


class PromoCode(db.Model):
    """
    promo_codes table
    """
    __tablename__ = 'promo_codes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, default=0)
    used_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)




class Library(db.Model):
    """
    Apps table
    """
    __tablename__ = "apps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    application_id = db.Column(db.Integer,db.ForeignKey("application.id"),nullable=False)
    active = db.Column(db.Boolean, default=True)
    package = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime,server_default=db.func.current_timestamp())
    status = db.Column(db.Enum('APPROVED','REJECTED','Active','PENDING','Terminated'),nullable=False)

class Application(db.Model):
    """
    Application table
    """
    __tablename__ = "application"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requested_at = db.Column(db.DateTime,server_default=db.func.current_timestamp())
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum('APPROVED','REJECTED','Active','PENDING','Terminated'),nullable=False,default="PENDING")
    # Relationship (one-to-many)
    apps = db.relationship("Library",backref="application",cascade="all, delete-orphan")
class Download(db.Model):
    """
    Represents a record of a users downloading an app.
    """

    __tablename__ = "downloads"

    download_id = db.Column(db.String(36),primary_key=True,nullable=False)
    users_id = db.Column(db.Integer,db.ForeignKey("users.id", ondelete="CASCADE"),primary_key=True,nullable=False)
    app_id = db.Column(db.Integer,db.ForeignKey("apps.id", ondelete="CASCADE"),primary_key=True,nullable=False)
    download_date = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f"<Download users_id={self.users_id} app_id={self.app_id}>"

class GiftRegistration(db.Model):
    """
     Gift registration model.
    """

    __tablename__ = "gift_registrations"

    id = db.Column(db.String(4),primary_key=True,default=uuid)
    account=db.Column(db.String(100),nullable=False)
    sender_email = db.Column(db.String(150),nullable=False)
    recipient_name = db.Column(db.String(100),nullable=False)
    recipient_email = db.Column(db.String(150),nullable=False)
    charges=db.Column(db.Float,nullable=False)   
    offer = db.Column(db.Enum("Valentine","Birthday","Graduation",name="gift_offer_enum"),nullable=False)
    delivery_date = db.Column(db.Date,nullable=True)
    message = db.Column(db.Text,nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

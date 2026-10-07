#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import logging

load_dotenv()  # load .env file

# File upload folder
DESTINATION = os.getenv("REPO_BASE_PATH")
UPLOAD_FOLDER = os.getenv('mdir')
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'doc', 'docx',
    'xml', 'xlsx', 'pptx', 'pdf', 'txt'
}

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # Fallback to a default key
    MAIL_USERNAME=os.getenv('sender_email')
    MAIL_DEFAULT_SENDER=os.getenv('sender_email')
    MAIL_SERVER = 'smtp.zoho.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_PASSWORD = os.getenv('sender_pass')  # Zoho app password

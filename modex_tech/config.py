#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import logging

# File upload folder
DESTINATION = os.getenv("REPO_BASE_PATH")
UPLOAD_FOLDER = os.getenv('mdir')

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # Fallback to a default key

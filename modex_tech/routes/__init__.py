#!/usr/bin/env python3
"""
Initialize and register all blueprints for the Flask application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint

# Initialize SQLAlchemy without binding to Flask app yet
db = SQLAlchemy()

from .pages  import pages_bp
from .process import  process_bp

blueprints = [
        (pages_bp, "/"),
        (process_bp, "/manage")
        ]

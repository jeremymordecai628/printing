#!/usr/bin/python3
"""
models package initializer

This file:
- Imports all ORM models
- Makes them accessible when importing the package
- Ensures SQLAlchemy registers models before create_all()
"""

from .data import User, Payment, PromoCode, Library, Application,StatusEnum, Download,UserPromotions,Login,GiftRegistration
from .function import (allowed_file,generate_tracking_code,user_id,  hash_value, login_required, role_required, is_safe_url,generate_uuid,
                       get_images,   send_email,   generate_unique_code,   user_exists_with_media_role,
                       detect_os,   detect_arch, verify, apply_code,  assign_id)

__all__ = [
    "User",
    "Payment",
    "PromoCode",
    "UserPromotions",
    "GiftRegistration",
    "Login",
    "generate_uuid",
    "Library",
    "Application",
    "StatusEnum",
    "Download"
]

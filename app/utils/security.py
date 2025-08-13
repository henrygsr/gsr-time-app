# app/utils/security.py
import os
from functools import wraps
from flask import abort
from flask_login import current_user

def _email_in_env_list(user_email: str, env_key: str) -> bool:
    raw = os.getenv(env_key, "")
    allowed = [e.strip().lower() for e in raw.split(",") if e.strip()]
    return user_email.lower() in allowed

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if getattr(current_user, "is_admin", False):
            return fn(*args, **kwargs)
        if _email_in_env_list(getattr(current_user, "email", ""), "BOOTSTRAP_ADMIN_EMAILS"):
            return fn(*args, **kwargs)
        abort(403)
    return wrapper

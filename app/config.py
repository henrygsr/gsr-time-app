import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def _normalize_db_uri(uri: str) -> str:
    # Use psycopg v3 driver
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg://", 1)
    elif uri.startswith("postgresql://"):
        uri = uri.replace("postgresql://", "postgresql+psycopg://", 1)

    # Add sslmode=require for hosted DBs if not specified
    try:
        parsed = urlparse(uri)
        if parsed.scheme.startswith("postgresql+psycopg"):
            q = dict(parse_qsl(parsed.query))
            host = (parsed.hostname or "").lower()
            if "sslmode" not in q and host not in {"localhost", "127.0.0.1", "::1"}:
                q["sslmode"] = "require"
                uri = urlunparse(parsed._replace(query=urlencode(q)))
    except Exception:
        pass
    return uri

def _pick_database_url() -> str:
    # Prefer Render's DATABASE_URL; fall back to other common envs
    for key in ("DATABASE_URL", "SQLALCHEMY_DATABASE_URI", "POSTGRES_URL", "POSTGRESQL_URL"):
        val = os.environ.get(key)
        if val:
            return _normalize_db_uri(val)
    return "sqlite:///app.db"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = _pick_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_EMAIL_DOMAIN = os.environ.get("ALLOWED_EMAIL_DOMAIN", "gsrconstruct.com")
    DAILY_TOLERANCE_MINUTES = float(os.environ.get("DAILY_TOLERANCE_MINUTES", "6"))

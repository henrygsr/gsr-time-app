import os

def _normalize(uri: str | None) -> str | None:
    """
    Normalize Postgres URLs for SQLAlchemy + psycopg v3:
    - Accepts postgres:// or postgresql:// or postgresql+psycopg://
    - Rewrites to postgresql+psycopg:// when needed
    """
    if not uri:
        return None
    if uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql+psycopg://", 1)
    if uri.startswith("postgresql://") and "+psycopg" not in uri:
        return uri.replace("postgresql://", "postgresql+psycopg://", 1)
    return uri

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # Prefer SQLALCHEMY_DATABASE_URI; fall back to DATABASE_URL (used by Render)
    _url = os.environ.get("SQLALCHEMY_DATABASE_URI") or os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = _normalize(_url) or "sqlite:///app.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Keeps pooled connections healthy in PaaS environments
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    ALLOWED_EMAIL_DOMAIN = os.environ.get("ALLOWED_EMAIL_DOMAIN", "gsrconstruct.com")
    DAILY_TOLERANCE_MINUTES = float(os.environ.get("DAILY_TOLERANCE_MINUTES", "6"))

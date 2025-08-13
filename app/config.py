import os

def _normalize_db_uri(uri: str) -> str:
    if uri.startswith("postgres://"):
        # Render often provides this; make it explicit for SQLAlchemy + psycopg v3
        return uri.replace("postgres://", "postgresql+psycopg://", 1)
    if uri.startswith("postgresql://"):
        # Also handle the explicit postgresql scheme
        return uri.replace("postgresql://", "postgresql+psycopg://", 1)
    return uri

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = _normalize_db_uri(
        os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EMAIL_DOMAIN = os.environ.get("ALLOWED_EMAIL_DOMAIN", "gsrconstruct.com")
    DAILY_TOLERANCE_MINUTES = float(os.environ.get("DAILY_TOLERANCE_MINUTES", "6"))

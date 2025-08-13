# app/models/settings.py
import os
from typing import Any, Callable, Optional

from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError, OperationalError

from . import db


def _settings_table_exists() -> bool:
    """Best-effort check so the app won’t crash before migrations run."""
    try:
        # Ensure we can connect
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        insp = inspect(db.engine)
        return "app_settings" in insp.get_table_names()
    except Exception:
        # If the engine isn’t ready yet, treat as not existing.
        return False


class AppSetting(db.Model):
    """Simple key/value store for app configuration with string values."""
    __tablename__ = "app_settings"

    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(512), nullable=False)

    # ---------- helpers ----------
    @staticmethod
    def get(
        key: str,
        default: Optional[Any] = None,
        cast: Callable[[str], Any] = str,
    ) -> Any:
        """
        Read setting from DB, falling back to ENV, then default.
        Never crashes if the table doesn’t exist yet.
        """
        # 1) Try DB (only if table exists)
        if _settings_table_exists():
            try:
                rec = AppSetting.query.get(key)
                if rec is not None:
                    if cast is str:
                        return rec.value
                    try:
                        return cast(rec.value)
                    except Exception:
                        return default
            except (ProgrammingError, OperationalError):
                # Table/query problem: ignore and fall through to ENV/default
                pass

        # 2) Try environment
        env_val = os.getenv(key)
        if env_val is not None:
            try:
                return cast(env_val) if cast is not str else env_val
            except Exception:
                return default

        # 3) Default
        return default

    @staticmethod
    def set(key: str, value: Any) -> "AppSetting":
        """
        Write to DB if possible; otherwise, no-op (so startup never crashes).
        Always returns an AppSetting-like object.
        """
        svalue = str(value)
        if _settings_table_exists():
            try:
                rec = AppSetting.query.get(key)
                if rec is None:
                    rec = AppSetting(key=key, value=svalue)
                    db.session.add(rec)
                else:
                    rec.value = svalue
                db.session.commit()
                return rec
            except (ProgrammingError, OperationalError):
                pass  # fall through to dummy

        # Dummy object if the table isn’t ready yet
        dummy = AppSetting.__new__(AppSetting)
        dummy.key = key
        dummy.value = svalue
        return dummy

    @staticmethod
    def seed_from_env(keys: list[str]) -> None:
        """
        Convenience to copy selected ENV vars into the DB if the table exists.
        Safe to call at startup.
        """
        if not _settings_table_exists():
            return
        for k in keys:
            val = os.getenv(k)
            if val is not None:
                try:
                    AppSetting.set(k, val)
                except Exception:
                    # Never let a bad single key prevent startup
                    continue


class GlobalSettings:
    """
    Typed accessors around AppSetting for the handful of app-wide settings.
    These mirror your environment variables and provide sensible defaults.
    """

    # keys (match your ENV names)
    DAILY_TOLERANCE_MINUTES = "DAILY_TOLERANCE_MINUTES"
    REPORT_BURDEN_PERCENT = "REPORT_BURDEN_PERCENT"
    ALLOWED_EMAIL_DOMAIN = "ALLOWED_EMAIL_DOMAIN"
    BOOTSTRAP_ADMIN_EMAILS = "BOOTSTRAP_ADMIN_EMAILS"
    BOOTSTRAP_ACCOUNTING_EMAILS = "BOOTSTRAP_ACCOUNTING_EMAILS"
    ADMIN_SEED_EMAIL = "ADMIN_SEED_EMAIL"

    @classmethod
    def daily_tolerance_minutes(cls, default: int = 6) -> int:
        return AppSetting.get(cls.DAILY_TOLERANCE_MINUTES, default=default, cast=int)

    @classmethod
    def report_burden_percent(cls, default: float = 30.0) -> float:
        return AppSetting.get(cls.REPORT_BURDEN_PERCENT, default=default, cast=float)

    @classmethod
    def allowed_email_domain(cls, default: Optional[str] = None) -> Optional[str]:
        return AppSetting.get(cls.ALLOWED_EMAIL_DOMAIN, default=default, cast=str)

    @classmethod
    def bootstrap_admin_emails(cls, default: str = "") -> list[str]:
        raw = AppSetting.get(cls.BOOTSTRAP_ADMIN_EMAILS, default=default, cast=str) or ""
        return [e.strip() for e in raw.split(",") if e.strip()]

    @classmethod
    def bootstrap_accounting_emails(cls, default: str = "") -> list[str]:
        raw = AppSetting.get(cls.BOOTSTRAP_ACCOUNTING_EMAILS, default=default, cast=str) or ""
        return [e.strip() for e in raw.split(",") if e.strip()]

    @classmethod
    def admin_seed_email(cls, default: Optional[str] = None) -> Optional[str]:
        return AppSetting.get(cls.ADMIN_SEED_EMAIL, default=default, cast=str)

    @classmethod
    def seed_from_env(cls) -> None:
        """Optional: call this during startup to persist ENV into DB when available."""
        AppSetting.seed_from_env(
            [
                cls.DAILY_TOLERANCE_MINUTES,
                cls.REPORT_BURDEN_PERCENT,
                cls.ALLOWED_EMAIL_DOMAIN,
                cls.BOOTSTRAP_ADMIN_EMAILS,
                cls.BOOTSTRAP_ACCOUNTING_EMAILS,
                cls.ADMIN_SEED_EMAIL,
            ]
        )

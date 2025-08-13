from datetime import datetime
from sqlalchemy.exc import ProgrammingError, OperationalError

from ..extensions import db


class AppSetting(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AppSetting {self.key}={self.value!r}>"

    @staticmethod
    def get(key: str, default=None):
        """Return the value for a key, or default if missing or table not ready."""
        try:
            rec = AppSetting.query.filter_by(key=key).first()
            return rec.value if rec else default
        except (ProgrammingError, OperationalError):
            # Table may not exist yet (first boot before migrations) — fail soft.
            return default

    @staticmethod
    def set(key: str, value) -> "AppSetting":
        """Create/update a setting and commit."""
        try:
            rec = AppSetting.query.filter_by(key=key).first()
            if rec:
                rec.value = str(value)
            else:
                rec = AppSetting(key=key, value=str(value))
                db.session.add(rec)
            db.session.commit()
            return rec
        except (ProgrammingError, OperationalError):
            # If the table doesn't exist yet, bubble up a clearer message
            raise RuntimeError(
                "app_settings table is missing. Run migrations or create tables."
            )

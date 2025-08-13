# Keep this minimal and avoid importing models here to prevent circular imports.
# Import db from extensions so `from app.models import db` continues to work.
from ..extensions import db

__all__ = ["db"]

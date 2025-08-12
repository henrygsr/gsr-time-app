import json
from flask_login import current_user
from ..extensions import db
from ..models.changelog import ChangeLog

def log_change(table, record_id, action, details=None):
    entry = ChangeLog(
        table_name=table,
        record_id=str(record_id),
        action=action,
        changed_by=(current_user.id if getattr(current_user, 'is_authenticated', False) else None),
        details=json.dumps(details or {})
    )
    db.session.add(entry)

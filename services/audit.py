from sqlalchemy.orm import Session

from models.audit_log import AuditLog


def log_action(db: Session, username: str, role_name: str, action: str, detail: str | None = None) -> None:
    db.add(AuditLog(username=username, role_name=role_name, action=action, detail=detail))
    db.commit()

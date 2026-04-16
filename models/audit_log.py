from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class AuditLog(Base):
    __tablename__ = 'rag_audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    role_name: Mapped[str] = mapped_column(String(50), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

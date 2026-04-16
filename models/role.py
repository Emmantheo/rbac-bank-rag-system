from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Role(Base):
    __tablename__ = "rag_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
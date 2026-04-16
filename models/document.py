from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Document(Base):
    __tablename__ = 'rag_documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    blob_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default='upload')
    full_text: Mapped[str] = mapped_column(Text)

    chunks = relationship("Chunk", back_populates="document")
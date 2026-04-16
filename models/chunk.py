from sqlalchemy import ARRAY, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from core.config import settings
from db.base import Base


class Chunk(Base):
    __tablename__ = 'rag_chunks'

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('rag_documents.id'), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, index=True)
    content: Mapped[str] = mapped_column(Text)
    allowed_roles: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dimension))

    document = relationship("Document", back_populates="chunks")

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class DocumentHash(Base):
    __tablename__ = 'rag_document_hashes'

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey('rag_documents.id'), nullable=True)
    sha256_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

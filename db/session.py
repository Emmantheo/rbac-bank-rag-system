from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from core.config import settings
from db.base import Base

from models.audit_log import AuditLog
from models.chunk import Chunk
from models.document import Document
from models.document_hash import DocumentHash
from models.role import Role
from models.user import User


sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg2://",
    1,
)

engine = create_engine(
    sync_database_url,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db() -> None:
    with engine.begin() as connection:
        connection.execute(text("create extension if not exists vector"))
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
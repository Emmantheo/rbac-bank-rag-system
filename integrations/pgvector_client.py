from sqlalchemy import text
from sqlalchemy.orm import Session


def ensure_vector_extension(db: Session) -> None:
    db.execute(text('create extension if not exists vector'))
    db.commit()

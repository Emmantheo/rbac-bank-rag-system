# services/retrieval.py

from sqlalchemy.orm import Session, joinedload

from models.chunk import Chunk
from services.embedding import embed_text


def retrieve_chunks(
    db: Session,
    query: str,
    user_role: str,
    top_k: int = 5,
) -> list[Chunk]:
    query_embedding = embed_text(query)
    normalized_user_role = user_role.strip().lower()

    chunks = (
        db.query(Chunk)
        .options(joinedload(Chunk.document))
        .filter(Chunk.allowed_roles.any(normalized_user_role))
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    return chunks


def build_citations(chunks: list[Chunk]) -> list[str]:
    citations: list[str] = []

    for chunk in chunks:
        title = "Untitled document"
        if chunk.document and chunk.document.title:
            title = chunk.document.title

        citations.append(f"{title} (section {chunk.chunk_index + 1})")

    return citations
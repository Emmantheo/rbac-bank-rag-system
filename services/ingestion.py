from sqlalchemy.orm import Session

from integrations.blob_client import BlobStorageClient
from integrations.llamaindex_client import parse_document_bytes, split_text_into_chunks
from models.chunk import Chunk
from models.document import Document
from models.document_hash import DocumentHash
from services.embedding import embed_text
from services.hashing import generate_sha256


def ingest_document_bytes(
    db: Session,
    file_name: str,
    file_bytes: bytes,
    allowed_roles: list[str],
    source_type: str = "upload",
) -> dict:
    full_text = parse_document_bytes(file_bytes=file_bytes, file_name=file_name)
    if not full_text:
        return {"status": "failed", "message": "no text could be extracted from document"}

    sha256_hash = generate_sha256(full_text)
    existing_hash = (
        db.query(DocumentHash)
        .filter(DocumentHash.sha256_hash == sha256_hash)
        .first()
    )
    if existing_hash:
        return {"status": "duplicate", "message": "document already ingested"}

    blob_client = BlobStorageClient()
    blob_name = blob_client.upload_file(file_name=file_name, file_bytes=file_bytes)
    blob_url = blob_client.get_blob_url(blob_name)

    document = Document(
        title=file_name,
        blob_name=blob_name,
        source_type=source_type,
        full_text=full_text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    db.add(DocumentHash(document_id=document.id, sha256_hash=sha256_hash))
    db.commit()

    chunks = split_text_into_chunks(full_text)
    created_count = 0

    normalized_roles = [role.strip().lower() for role in allowed_roles if role.strip()]

    for idx, chunk_text in enumerate(chunks):
        embedding = embed_text(chunk_text)
        db.add(
            Chunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk_text,
                allowed_roles=normalized_roles,
                embedding=embedding,
            )
        )
        created_count += 1

    db.commit()

    return {
        "status": "ingested",
        "document_id": document.id,
        "blob_name": blob_name,
        "blob_url": blob_url,
        "chunk_count": created_count,
        "message": "document ingested successfully",
    }
# schemas/ingestion.py

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    status: str
    document_id: int | None = None
    blob_name: str | None = None
    blob_url: str | None = None
    chunk_count: int | None = None
    message: str
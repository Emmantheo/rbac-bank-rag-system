from __future__ import annotations
import uuid
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContentSettings
from core.config import settings


class BlobStorageClient:
    def __init__(self) -> None:
        self.client = BlobServiceClient.from_connection_string(
            settings.blob_connection_string
        )
        self.container_name = settings.blob_container

    def upload_file(self, file_name: str, file_bytes: bytes) -> str:
        suffix = Path(file_name).suffix
        unique_name = f"{uuid.uuid4().hex}{suffix}"

        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=unique_name,
        )

        content_type = self._guess_content_type(file_name)

        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

        return unique_name

    def get_blob_url(self, blob_name: str) -> str:
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=blob_name,
        )
        return blob_client.url

    @staticmethod
    def _guess_content_type(file_name: str) -> str:
        lowered = file_name.lower()

        if lowered.endswith(".pdf"):
            return "application/pdf"
        if lowered.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if lowered.endswith(".txt"):
            return "text/plain"

        return "application/octet-stream"
# routes/ingestion.py

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from deps import get_current_user
from db.session import get_db
from integrations.langfuse_client import langfuse_client
from models.user import User
from schemas.ingestion import IngestionResponse
from services.audit import log_action
from services.ingestion import ingest_document_bytes

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IngestionResponse:
    file_bytes = file.file.read()

    with langfuse_client.trace(
        name="document_upload",
        user_id=current_user.username,
        input_payload={
            "file_name": file.filename,
            "file_size_bytes": len(file_bytes),
            "allowed_role": current_user.role_name,
        },
        metadata={
            "feature": "ingestion",
            "source_type": "upload",
        },
    ) as trace:
        result = ingest_document_bytes(
            db=db,
            file_name=file.filename or "uploaded_document",
            file_bytes=file_bytes,
            allowed_roles=[current_user.role_name.strip().lower()],
            source_type="upload",
        )

        with langfuse_client.span(
            trace,
            name="ingestion_result",
            input_payload={"file_name": file.filename},
            metadata={"role_name": current_user.role_name},
        ) as result_span:
            if result_span:
                result_span.update(output=result)

    log_action(
        db=db,
        username=current_user.username,
        role_name=current_user.role_name,
        action="document_upload",
        detail=(
            f"file={file.filename}, "
            f"status={result['status']}, "
            f"allowed_role={current_user.role_name}, "
            f"blob_name={result.get('blob_name')}"
        ),
    )

    return IngestionResponse(**result)
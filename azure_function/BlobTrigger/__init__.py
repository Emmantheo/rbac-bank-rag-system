import logging

import azure.functions as func

from db.session import SessionLocal
from services.ingestion import ingest_document_bytes


def main(blob: func.InputStream) -> None:
    logging.info('blob trigger fired for %s', blob.name)
    db = SessionLocal()
    try:
        result = ingest_document_bytes(
            db=db,
            file_name=blob.name.split('/')[-1],
            file_bytes=blob.read(),
            allowed_roles=['compliance_officer', 'legal_counsel'],
            source_type='blob_trigger',
        )
        logging.info('ingestion result: %s', result)
    except Exception:
        logging.exception('blob ingestion failed')
        raise
    finally:
        db.close()

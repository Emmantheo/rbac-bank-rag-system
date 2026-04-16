# main.py

from fastapi import FastAPI
from sqlalchemy.orm import Session

from db.session import SessionLocal, init_db
from integrations.langfuse_client import langfuse_client
from router import api_router
from services.auth import seed_roles


app = FastAPI(
    title="CBN Policy and Compliance RAG",
    version="1.0.0",
)


@app.on_event("startup")
async def startup() -> None:
    init_db()
    db: Session = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown() -> None:
    langfuse_client.flush()


@app.get("/")
def root():
    return {"message": "CBN Policy and Compliance RAG API is running"}


app.include_router(api_router)
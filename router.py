from __future__ import annotations
from routes import auth, chat, health, ingestion
from fastapi import APIRouter
from core.config import settings


api_router = APIRouter()

api_router.include_router(health.router, prefix=settings.api_prefix, tags=['health'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(ingestion.router, prefix='/ingestion', tags=['ingestion'])
api_router.include_router(chat.router, prefix='/chat', tags=['chat'])
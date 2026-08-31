# backend/app/api/router.py
# Aggregated API router for MEEV Core

from fastapi import APIRouter
from backend.app.api.cases import router as cases_router
from backend.app.api.ambiguity import router as ambiguity_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.ingest import router as ingest_router

api_router = APIRouter()
api_router.include_router(cases_router, prefix="/cases", tags=["Investigation Cases"])
api_router.include_router(ambiguity_router, prefix="/ambiguity-queue", tags=["Ambiguity Resolution"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["District Analytics"])
api_router.include_router(ingest_router, prefix="/ingest", tags=["Real-Time Ingestion"])


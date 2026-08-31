# backend/app/main.py
# FastAPI application entry point for MEEV Core

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.router import api_router
from backend.app.db.session import engine, Base
import backend.app.db.models # Ensure models are loaded

# Initialize database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Database auto-table creation: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from backend.app.db.session import get_db_context
from backend.app.db.models import School
from backend.scripts.load_realtime_data import load_realtime_data

@app.on_event("startup")
def startup_event():
    """Ensure database schema is created and authentic real-time baseline data is loaded."""
    try:
        Base.metadata.create_all(bind=engine)
        with get_db_context() as db:
            count = db.query(School).count()
            if count < 100:
                print("Ingesting authentic Karnataka State 28-Constituency UDISE+ and e-SAKSHI claims...")
                load_realtime_data(clear_first=True)
    except Exception as e:
        print(f"Startup initialization notice: {e}")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "MEEV Core API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

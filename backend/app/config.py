import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "MEEV — MPLADS Education Ecosystem Validator"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://meev_admin:meev_secure_password_2026@localhost:5432/meev_core"
    )
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "false").lower() == "true"
    SQLITE_URL: str = "sqlite:///./meev_dev.db"

settings = Settings()

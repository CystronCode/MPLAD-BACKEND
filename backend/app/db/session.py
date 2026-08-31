# backend/app/db/session.py
# Database engine and session factory with PostgreSQL and SQLite support

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

Base = declarative_base()

try:
    if settings.USE_SQLITE_FALLBACK:
        engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
except Exception:
    engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})

from contextlib import contextmanager

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


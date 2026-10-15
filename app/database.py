import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to SQLite local database file (allows complete offline demo at Olympiad)
# In production, DATABASE_URL environment variable can point to PostgreSQL (e.g. Render / Supabase)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pawconnect.db")

# Fix for Render / Heroku postgres:// -> postgresql:// URL schema
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for API routes to obtain a database session and safely close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

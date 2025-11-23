"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for development
# Use absolute path for Railway deployment
import sys
if os.getenv("RAILWAY_ENVIRONMENT"):
    # Railway deployment - use absolute path
    DB_PATH = "/app/skaters.db"
    DEFAULT_DB_URL = f"sqlite:///{DB_PATH}"
else:
    # Local development
    DEFAULT_DB_URL = "sqlite:///./skaters.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency for getting database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    from app.models import venue  # Import models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_db():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")

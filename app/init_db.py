"""
Database initialization script
Run this to create all tables
"""

from app.database import init_db, engine
from app.models.venue import Base

if __name__ == "__main__":
    print("🔧 Creating database tables...")
    init_db()
    print("✅ Database initialization complete!")
    print(f"📊 Database: {engine.url}")

"""
Database connection and session management for Budul AI
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logging
from typing import AsyncGenerator

from app.core.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

# Create async engine for database operations
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.ENVIRONMENT == "development",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("📚 Database tables created successfully")
        
        # Set up full-text search for Arabic and English content
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
            CREATE EXTENSION IF NOT EXISTS unaccent;
        """)
        
        # Create custom indexes for Islamic content search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_islamic_content_arabic_text_gin 
            ON islamic_content USING gin(to_tsvector('arabic', arabic_text));
            
            CREATE INDEX IF NOT EXISTS idx_islamic_content_english_text_gin 
            ON islamic_content USING gin(to_tsvector('english', english_text));
            
            CREATE INDEX IF NOT EXISTS idx_islamic_content_arabic_trigram 
            ON islamic_content USING gin(arabic_text gin_trgm_ops);
        """)
        
        logger.info("🔍 Full-text search indexes created")

# Database health check
async def check_db_health():
    """Check database connection health"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
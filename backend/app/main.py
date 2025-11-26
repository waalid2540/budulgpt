"""
Global Waqaf Tech - Digital Waqf Network Platform
Multi-tenant SaaS platform for masajid and Islamic organizations
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import init_db
from app.api.v1.router import api_router
from app.services.price_monitor import start_price_monitoring, stop_price_monitoring
# from app.core.logging import setup_logging

# Setup logging
# setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🕌 Starting Global Waqaf Tech - Digital Waqf Network Platform")

    # Initialize database
    await init_db()
    logger.info("📚 Islamic knowledge database initialized")

    # Start price monitoring service in background
    monitoring_task = asyncio.create_task(start_price_monitoring())
    logger.info("🔔 Umrah price monitoring service started")

    yield

    # Stop price monitoring
    await stop_price_monitoring()
    logger.info("🔔 Umrah price monitoring service stopped")

    logger.info("🌙 Global Waqaf Tech shutting down gracefully")

# Create FastAPI app
app = FastAPI(
    title="Global Waqaf Tech API",
    description="Digital Waqf Network - Multi-tenant platform empowering masajid and Islamic organizations worldwide with AI-powered tools",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint - Global Waqaf Tech welcome message"""
    return {
        "message": "🕌 Welcome to Global Waqaf Tech - Empowering Masajid & Islamic Organizations",
        "version": "2.0.0",
        "description": "Multi-tenant digital waqf platform providing AI-powered tools for masajid and Islamic organizations worldwide",
        "platform_type": "Digital Waqf Network",
        "features": [
            "Du'a & Dhikr Studio - AI-powered Islamic supplications",
            "Kids Story Studio - Islamic stories with moral lessons",
            "Umrah & Hajj Alerts - Travel deal finder with price monitoring",
            "Grant Finder - Search and track grant opportunities",
            "Marketplace - Connect Muslim businesses and services",
            "Learning Hub - Islamic courses and educational content",
            "Social Media Studio - AI-powered content generation for masajid"
        ],
        "waqf_info": "20% of subscription proceeds support selected masajid operations and community programs",
        "documentation": "/docs" if settings.ENVIRONMENT == "development" else "Contact support for API documentation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Global Waqaf Tech Backend",
        "version": "2.0.0",
        "platform": "multi-tenant",
        "features": {
            "dua_studio": "active",
            "story_studio": "active",
            "umrah_alerts": "active",
            "grant_finder": "active",
            "marketplace": "active",
            "learning_hub": "active",
            "social_studio": "active"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "May Allah guide us through this technical difficulty",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
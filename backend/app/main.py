"""
Budul AI - Islamic Artificial Intelligence Platform
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import init_db
from app.api.v1.router import api_router
# from app.core.logging import setup_logging

# Setup logging
# setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🕌 Starting Budul AI - Islamic Intelligence Platform")
    
    # Initialize database
    await init_db()
    logger.info("📚 Islamic knowledge database initialized")
    
    yield
    
    logger.info("🌙 Budul AI shutting down gracefully")

# Create FastAPI app
app = FastAPI(
    title="Budul AI API",
    description="Islamic Artificial Intelligence Platform - Serving 1.8 billion Muslims worldwide",
    version="1.0.0",
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
    """Root endpoint - Budul AI welcome message"""
    return {
        "message": "🕌 Welcome to Budul AI - Islamic Intelligence for the Modern World",
        "version": "1.0.0",
        "description": "Authentic Islamic knowledge powered by cutting-edge AI technology",
        "features": [
            "Budul GPT - Islamic Conversational AI",
            "Budul API - Islamic AI for Developers", 
            "Budul Studio - Islamic Video Generation",
            "Budul Vision - Islamic Image Creation"
        ],
        "documentation": "/docs" if settings.ENVIRONMENT == "development" else "Contact support for API documentation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Budul AI Backend",
        "version": "1.0.0"
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
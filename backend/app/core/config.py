"""
Configuration settings for Budul AI
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "Budul AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "budul-ai-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:budul_secure_2024@localhost:5432/budul_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Services - Your Custom Islamic Model
    ISLAMIC_MODEL_PATH: str = "./models/islamic-ai"  # Path to your trained model
    ISLAMIC_MODEL_TYPE: str = "custom"  # custom, llama, mistral, etc.
    USE_GPU: bool = True  # Set to False if no GPU available
    MODEL_MAX_LENGTH: int = 2048  # Maximum input length
    GENERATION_MAX_LENGTH: int = 1024  # Maximum generation length
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "*",
        "https://budulgpt-frontend.onrender.com",
        "https://budulai.com", 
        "https://www.budulai.com",
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "budulai.com",
        "www.budulai.com",
        "budulgpt-backend.onrender.com",
        "budulgpt-frontend.onrender.com"
    ]
    
    # Islamic Sources Configuration
    ISLAMIC_SOURCES: dict = {
        "sunnah_com": {
            "base_url": "https://sunnah.com",
            "rate_limit": 2,  # requests per second
            "collections": [
                "bukhari", "muslim", "abudawud", "tirmidhi", 
                "nasai", "ibnmajah", "malik", "ahmad"
            ]
        },
        "quran_com": {
            "base_url": "https://api.quran.com",
            "rate_limit": 5,
            "features": ["verses", "translations", "tafsir", "recitations"]
        },
        "islamweb_net": {
            "base_url": "https://islamweb.net",
            "rate_limit": 1,
            "language_support": ["ar", "en", "fr", "es"]
        }
    }
    
    # Scraping Configuration
    SCRAPING_CONFIG: dict = {
        "max_concurrent_requests": 10,
        "request_timeout": 30,
        "retry_attempts": 3,
        "respect_robots_txt": True,
        "user_agent": "BudulAI/1.0 (+https://budulai.com/bot)"
    }
    
    # File Storage
    UPLOAD_DIR: str = "/app/data/uploads"
    DATASET_DIR: str = "/app/data/datasets"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
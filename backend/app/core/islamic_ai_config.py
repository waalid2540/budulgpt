"""
Islamic AI Configuration System
Production-ready configuration for serving 1.8 billion Muslims worldwide
"""

import os
from typing import List, Dict, Optional
from pydantic import BaseSettings, validator
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class IslamicLanguage(str, Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    URDU = "ur"
    TURKISH = "tr"
    PERSIAN = "fa"
    MALAY = "ms"
    FRENCH = "fr"
    INDONESIAN = "id"
    HINDI = "hi"
    BENGALI = "bn"

class IslamicMadhab(str, Enum):
    HANAFI = "hanafi"
    MALIKI = "maliki"
    SHAFII = "shafii"
    HANBALI = "hanbali"
    JAFARI = "jafari"
    GENERAL = "general"

class IslamicAISettings(BaseSettings):
    """
    Comprehensive settings for Islamic AI platform
    """
    
    # Environment Configuration
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    app_name: str = "Budul AI - Islamic Intelligence Platform"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_connections: int = 1000
    keepalive_timeout: int = 65
    
    # Database Configuration
    postgres_url: str = "postgresql+asyncpg://budul_admin:password@localhost:5432/budul_islamic_ai"
    mongodb_url: str = "mongodb://budul_admin:password@localhost:27017/islamic_knowledge"
    redis_url: str = "redis://localhost:6379"
    elasticsearch_url: str = "http://localhost:9200"
    
    # AI Model Configuration
    openai_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Islamic AI Model Paths
    islamic_gpt_model_path: str = "./models/islamic-ai"
    hadith_model_path: str = "./models/hadith-classifier"
    quran_model_path: str = "./models/quran-embeddings"
    arabic_nlp_model_path: str = "./models/arabic-nlp"
    
    # Model Configuration
    max_context_length: int = 32768  # Support for long Islamic texts
    temperature: float = 0.3  # Conservative for religious accuracy
    top_p: float = 0.9
    max_tokens: int = 2048
    
    # Islamic Content Configuration
    supported_languages: List[IslamicLanguage] = [
        IslamicLanguage.ARABIC,
        IslamicLanguage.ENGLISH,
        IslamicLanguage.URDU,
        IslamicLanguage.TURKISH
    ]
    
    default_language: IslamicLanguage = IslamicLanguage.ENGLISH
    default_madhab: IslamicMadhab = IslamicMadhab.GENERAL
    
    # Content Quality Settings
    min_authenticity_score: float = 0.7
    min_scholarly_consensus: float = 0.6
    require_citation: bool = True
    auto_verify_hadith: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000
    
    # Security Configuration
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "https://budulai.com",
        "https://app.budulai.com"
    ]
    
    # Monitoring and Logging
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = True
    sentry_dsn: Optional[str] = None
    
    # Content Filtering
    enable_content_filter: bool = True
    inappropriate_content_threshold: float = 0.8
    enable_controversial_topic_warning: bool = True
    
    # Caching Configuration
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_max_size: int = 10000
    enable_response_caching: bool = True
    
    # Arabic Text Processing
    enable_diacritic_normalization: bool = True
    enable_root_word_matching: bool = True
    arabic_font_preference: str = "Uthmani"
    
    # Search Configuration
    max_search_results: int = 100
    search_relevance_threshold: float = 0.5
    enable_semantic_search: bool = True
    enable_fuzzy_matching: bool = True
    
    # API Documentation
    enable_docs: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Third-party Integrations
    prayer_times_api_key: Optional[str] = None
    qibla_direction_api_key: Optional[str] = None
    islamic_calendar_api_key: Optional[str] = None
    
    # Content Sources Configuration
    enable_quran_com_integration: bool = True
    enable_sunnah_com_integration: bool = True
    enable_islamqa_integration: bool = True
    enable_seekersguidance_integration: bool = True
    
    # Video Generation Configuration
    video_generation_enabled: bool = True
    max_video_length_minutes: int = 60
    default_video_resolution: str = "1080p"
    enable_arabic_calligraphy: bool = True
    enable_geometric_patterns: bool = True
    
    # Business Configuration
    free_tier_daily_limit: int = 100
    premium_tier_daily_limit: int = 10000
    enterprise_tier_daily_limit: int = 100000
    
    # Scholarly Verification
    enable_auto_verification: bool = True
    require_scholar_approval: bool = False  # For non-controversial content
    scholar_review_queue_size: int = 1000
    
    # Backup and Recovery
    enable_automated_backups: bool = True
    backup_frequency_hours: int = 6
    backup_retention_days: int = 30
    
    # Performance Optimization
    enable_query_optimization: bool = True
    enable_connection_pooling: bool = True
    max_pool_size: int = 20
    pool_timeout_seconds: int = 30
    
    # Regional Settings
    enable_regional_customization: bool = True
    default_timezone: str = "UTC"
    enable_local_prayer_times: bool = True
    
    # Feature Flags
    enable_experimental_features: bool = False
    enable_beta_features: bool = False
    enable_advanced_analytics: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "BUDUL_"
        case_sensitive = False
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("postgres_url")
    def validate_postgres_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("PostgreSQL URL must start with postgresql:// or postgresql+asyncpg://")
        return v
    
    @validator("mongodb_url")
    def validate_mongodb_url(cls, v):
        if not v.startswith("mongodb://"):
            raise ValueError("MongoDB URL must start with mongodb://")
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v):
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v
    
    @validator("min_authenticity_score", "min_scholarly_consensus")
    def validate_score_range(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Score must be between 0 and 1")
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    @validator("jwt_secret")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters long")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    def get_database_url(self, async_driver: bool = True) -> str:
        """Get database URL with appropriate driver"""
        if async_driver:
            return self.postgres_url
        else:
            return self.postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    
    def get_supported_languages_list(self) -> List[str]:
        """Get list of supported language codes"""
        return [lang.value for lang in self.supported_languages]
    
    def get_model_config(self) -> Dict:
        """Get AI model configuration"""
        return {
            "max_context_length": self.max_context_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "min_authenticity_score": self.min_authenticity_score,
            "require_citation": self.require_citation
        }
    
    def get_cache_config(self) -> Dict:
        """Get caching configuration"""
        return {
            "ttl_seconds": self.cache_ttl_seconds,
            "max_size": self.cache_max_size,
            "enabled": self.enable_response_caching
        }
    
    def get_rate_limit_config(self) -> Dict:
        """Get rate limiting configuration"""
        return {
            "per_minute": self.rate_limit_per_minute,
            "per_hour": self.rate_limit_per_hour,
            "per_day": self.rate_limit_per_day
        }
    
    def get_business_tier_limits(self) -> Dict:
        """Get business tier limits"""
        return {
            "free": self.free_tier_daily_limit,
            "premium": self.premium_tier_daily_limit,
            "enterprise": self.enterprise_tier_daily_limit
        }

# Global settings instance
settings = IslamicAISettings()

# Islamic-specific constants
ISLAMIC_MONTHS = [
    "Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-thani",
    "Jumada al-awwal", "Jumada al-thani", "Rajab", "Sha'ban",
    "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
]

PRAYER_TIMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

HADITH_COLLECTIONS = [
    "Sahih al-Bukhari", "Sahih Muslim", "Sunan Abu Dawood",
    "Jami` at-Tirmidhi", "Sunan an-Nasa'i", "Sunan Ibn Majah",
    "Muwatta Malik", "Musnad Ahmad", "Sahih Ibn Hibban"
]

QURAN_CHAPTERS = 114  # Total number of Surahs
QURAN_VERSES = 6236  # Total number of Ayahs

# Model performance targets
PERFORMANCE_TARGETS = {
    "response_time_ms": 500,
    "accuracy_percentage": 95,
    "uptime_percentage": 99.9,
    "concurrent_users": 1000000,
    "daily_api_calls": 100000000
}

# Scholarly verification levels
VERIFICATION_LEVELS = {
    "auto_approved": 0.9,  # Auto-approve if confidence > 90%
    "scholar_review": 0.7,  # Send to scholar if confidence 70-90%
    "requires_expert": 0.7  # Requires expert review if < 70%
}
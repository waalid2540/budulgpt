"""
Database models for Budul AI Islamic content
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Index, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

Base = declarative_base()

class IslamicSource(Base):
    """Table for Islamic knowledge sources"""
    __tablename__ = "islamic_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)  # e.g., "Sahih Bukhari"
    source_type = Column(String(50), nullable=False)  # hadith, quran, tafsir, fatwa
    authority_level = Column(String(20), nullable=False)  # sahih, hasan, daif, authentic
    language = Column(String(10), nullable=False, default="ar")
    website_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    content_items = relationship("IslamicContent", back_populates="source")

class IslamicContent(Base):
    """Main table for Islamic content (Quran, Hadith, etc.)"""
    __tablename__ = "islamic_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("islamic_sources.id"), nullable=False)
    content_type = Column(String(50), nullable=False)  # quran_verse, hadith, tafsir, fatwa
    
    # Core text content
    arabic_text = Column(Text, nullable=False)
    english_text = Column(Text)
    transliteration = Column(Text)
    
    # Quranic specific fields
    surah_number = Column(Integer)
    verse_number = Column(Integer)
    verse_key = Column(String(20))  # e.g., "2:255"
    
    # Hadith specific fields
    narrator_chain = Column(Text)  # Isnad
    hadith_number = Column(String(50))
    collection_book = Column(String(100))
    authenticity_grade = Column(String(20))  # sahih, hasan, daif
    
    # Topic categorization
    topics = Column(ARRAY(String))  # Islamic topic tags
    fiqh_category = Column(String(100))  # Worship, Transactions, Family, etc.
    
    # Attribution and metadata
    attribution = Column(JSON)  # Full source attribution details
    content_metadata = Column(JSON)  # Additional structured data
    
    # Search and indexing
    search_vector = Column(Text)  # For full-text search
    embedding_vector = Column(ARRAY(Float))  # AI embeddings for semantic search
    
    # Quality and verification
    verification_status = Column(String(20), default="pending")  # verified, pending, disputed
    quality_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime)
    
    # Relationships
    source = relationship("IslamicSource", back_populates="content_items")
    translations = relationship("ContentTranslation", back_populates="content")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_type', 'content_type'),
        Index('idx_surah_verse', 'surah_number', 'verse_number'),
        Index('idx_authenticity', 'authenticity_grade'),
        Index('idx_topics', 'topics'),
        Index('idx_search_vector', 'search_vector'),
    )

class ContentTranslation(Base):
    """Translations of Islamic content in different languages"""
    __tablename__ = "content_translations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    language_code = Column(String(10), nullable=False)  # en, ur, tr, fr, etc.
    translated_text = Column(Text, nullable=False)
    translator_name = Column(String(255))
    translation_methodology = Column(String(100))  # literal, interpretive, etc.
    quality_rating = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content = relationship("IslamicContent", back_populates="translations")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_content_language', 'content_id', 'language_code'),
    )

class Scholar(Base):
    """Islamic scholars and their credentials"""
    __tablename__ = "scholars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    arabic_name = Column(String(255))
    era = Column(String(50))  # classical, contemporary
    birth_year = Column(Integer)
    death_year = Column(Integer)
    nationality = Column(String(100))
    specialization = Column(ARRAY(String))  # hadith, fiqh, tafsir, etc.
    madhab = Column(String(50))  # hanafi, maliki, shafii, hanbali
    biography = Column(Text)
    credentials = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scholarly_opinions = relationship("ScholarlyOpinion", back_populates="scholar")

class ScholarlyOpinion(Base):
    """Scholarly opinions and interpretations"""
    __tablename__ = "scholarly_opinions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    
    opinion_type = Column(String(50))  # tafsir, sharh, commentary, ruling
    opinion_text = Column(Text, nullable=False)
    language = Column(String(10), default="ar")
    
    # Contextual information
    historical_context = Column(Text)
    applicable_conditions = Column(Text)
    madhab_perspective = Column(String(50))
    
    # Verification
    verification_status = Column(String(20), default="pending")
    source_citation = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scholar = relationship("Scholar", back_populates="scholarly_opinions")

class IslamicTopic(Base):
    """Islamic knowledge taxonomy"""
    __tablename__ = "islamic_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    arabic_name = Column(String(255))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("islamic_topics.id"))
    category_level = Column(Integer, default=1)  # 1=main, 2=sub, 3=detailed
    
    description = Column(Text)
    keywords = Column(ARRAY(String))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for hierarchical topics
    children = relationship("IslamicTopic", backref="parent", remote_side=[id])

class User(Base):
    """User accounts for Budul AI platform"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Islamic preferences
    preferred_language = Column(String(10), default="en")
    madhab_preference = Column(String(50))
    knowledge_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    
    # Subscription
    subscription_tier = Column(String(20), default="free")  # free, basic, premium, enterprise
    subscription_expires = Column(DateTime)
    
    # Usage tracking
    api_calls_count = Column(Integer, default=0)
    last_login = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    """User chat sessions with Budul GPT"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255))
    language = Column(String(10), default="en")
    
    # Session metadata
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    """Individual messages in chat sessions"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Islamic content references
    referenced_content_ids = Column(ARRAY(UUID))
    citations = Column(JSON)  # Structured citation data
    
    # AI metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class APIUsage(Base):
    """Track API usage for billing and analytics"""
    __tablename__ = "api_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    
    # Usage metrics
    tokens_consumed = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    
    # Request metadata
    request_metadata = Column(JSON)
    response_metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_user_endpoint', 'user_id', 'endpoint'),
        Index('idx_created_at', 'created_at'),
    )
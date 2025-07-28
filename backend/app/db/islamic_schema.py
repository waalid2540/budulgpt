"""
Advanced Islamic Database Schema
Scalable architecture for billions of Islamic texts with hierarchical knowledge taxonomy
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

# Islamic Knowledge Taxonomy Enums
class IslamicTopicEnum(enum.Enum):
    AQEEDAH = "aqeedah"  # Islamic Beliefs
    FIQH = "fiqh"  # Islamic Jurisprudence
    SEERAH = "seerah"  # Prophet's Biography
    TAFSEER = "tafseer"  # Quran Commentary
    HADITH = "hadith"  # Prophetic Traditions
    AKHLAQ = "akhlaq"  # Islamic Ethics
    TAZKIYAH = "tazkiyah"  # Spiritual Purification
    HISTORY = "history"  # Islamic History
    DAWA = "dawa"  # Islamic Propagation
    COMPARATIVE = "comparative"  # Comparative Religion

class FiqhMadhab(enum.Enum):
    HANAFI = "hanafi"
    MALIKI = "maliki"
    SHAFII = "shafii"
    HANBALI = "hanbali"
    JAFARI = "jafari"  # Shia jurisprudence
    ZAHIRI = "zahiri"
    GENERAL = "general"

class AuthenticityLevel(enum.Enum):
    SAHIH = "sahih"  # Authentic
    HASAN = "hasan"  # Good
    DAIF = "daif"  # Weak
    MAWDU = "mawdu"  # Fabricated
    UNKNOWN = "unknown"

class ContentLanguage(enum.Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    URDU = "ur"
    TURKISH = "tr"
    PERSIAN = "fa"
    MALAY = "ms"
    FRENCH = "fr"
    INDONESIAN = "id"

# Core Tables
class IslamicSource(Base):
    """Authoritative Islamic sources with scholarly verification"""
    __tablename__ = "islamic_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    author = Column(String(200))
    hijri_date = Column(String(50))  # Hijri calendar date
    gregorian_date = Column(DateTime)
    language = Column(Enum(ContentLanguage), default=ContentLanguage.ARABIC)
    source_type = Column(String(50))  # quran, hadith_collection, tafseer, etc.
    authenticity_level = Column(Enum(AuthenticityLevel), default=AuthenticityLevel.UNKNOWN)
    scholarly_consensus = Column(Float)  # 0.0-1.0 scholarly agreement score
    access_url = Column(Text)
    isbn = Column(String(20))
    publisher = Column(String(200))
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    verified_by_scholar = Column(Boolean, default=False)
    verification_notes = Column(Text)
    
    # Relationships
    content_items = relationship("IslamicContent", back_populates="source")
    
    __table_args__ = (
        Index('idx_source_type_auth', 'source_type', 'authenticity_level'),
        Index('idx_source_language', 'language'),
    )

class IslamicContent(Base):
    """Main table for Islamic content with comprehensive metadata"""
    __tablename__ = "islamic_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("islamic_sources.id"), nullable=False)
    
    # Content Classification
    topic = Column(Enum(IslamicTopicEnum), nullable=False)
    subtopic = Column(String(100))
    content_type = Column(String(50))  # verse, hadith, scholarly_opinion, fatwa
    
    # Core Text Content
    arabic_text = Column(Text, nullable=False)
    english_text = Column(Text)
    transliteration = Column(Text)
    
    # Islamic-Specific Fields
    surah_number = Column(Integer)  # For Quran verses
    verse_number = Column(Integer)  # For Quran verses
    hadith_number = Column(String(20))  # For Hadith collections
    chain_of_narration = Column(Text)  # Isnad for Hadith
    narrator_reliability = Column(Float)  # 0.0-1.0 reliability score
    madhab_perspective = Column(Enum(FiqhMadhab))
    ruling_strength = Column(String(50))  # wajib, mustahab, mubah, etc.
    
    # Content Analysis
    authenticity_score = Column(Float)  # AI-calculated authenticity
    topic_confidence = Column(Float)  # AI confidence in topic classification
    scholarly_consensus_score = Column(Float)  # Agreement among scholars
    contradiction_flags = Column(ARRAY(String))  # Potential contradictions
    
    # Multi-language Support
    translations = Column(JSON)  # {language: translation}
    language = Column(Enum(ContentLanguage), default=ContentLanguage.ARABIC)
    
    # Search and Indexing
    search_vector = Column(TSVECTOR)  # Full-text search
    arabic_search_vector = Column(TSVECTOR)  # Arabic-specific search
    keywords = Column(ARRAY(String))  # Extracted keywords
    semantic_embedding = Column(ARRAY(Float))  # AI embeddings for semantic search
    
    # Quality Metrics
    quality_score = Column(Float)  # Overall content quality
    citation_count = Column(Integer, default=0)  # How often referenced
    user_rating = Column(Float)  # Community rating
    scholarly_rating = Column(Float)  # Scholar rating
    
    # Attribution and Verification
    original_source = Column(Text)  # Original source reference
    page_number = Column(String(20))
    volume_number = Column(String(20))
    verification_status = Column(String(20), default='pending')
    verified_by = Column(String(200))  # Scholar who verified
    verification_date = Column(DateTime)
    
    # Metadata
    content_metadata = Column(JSON)  # Additional structured data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    source = relationship("IslamicSource", back_populates="content_items")
    translations_rel = relationship("ContentTranslation", back_populates="content")
    citations = relationship("ContentCitation", back_populates="content")
    
    __table_args__ = (
        Index('idx_content_topic_type', 'topic', 'content_type'),
        Index('idx_content_surah_verse', 'surah_number', 'verse_number'),
        Index('idx_content_authenticity', 'authenticity_score'),
        Index('idx_content_quality', 'quality_score'),
        Index('idx_content_search', 'search_vector'),
        Index('idx_content_arabic_search', 'arabic_search_vector'),
        Index('idx_content_language', 'language'),
        Index('idx_content_madhab', 'madhab_perspective'),
    )

class ContentTranslation(Base):
    """Multi-language translations with quality tracking"""
    __tablename__ = "content_translations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    language = Column(Enum(ContentLanguage), nullable=False)
    translated_text = Column(Text, nullable=False)
    translator_name = Column(String(200))
    translation_quality = Column(Float)  # 0.0-1.0 quality score
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(200))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    content = relationship("IslamicContent", back_populates="translations_rel")
    
    __table_args__ = (
        Index('idx_translation_content_lang', 'content_id', 'language'),
        Index('idx_translation_quality', 'translation_quality'),
    )

class ContentCitation(Base):
    """Citation and cross-reference tracking"""
    __tablename__ = "content_citations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citing_content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    cited_content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    citation_type = Column(String(50))  # supporting, contradicting, clarifying
    confidence = Column(Float)  # AI confidence in citation relevance
    context = Column(Text)  # Why this citation is relevant
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    content = relationship("IslamicContent", back_populates="citations", foreign_keys=[citing_content_id])
    
    __table_args__ = (
        Index('idx_citation_citing', 'citing_content_id'),
        Index('idx_citation_cited', 'cited_content_id'),
        Index('idx_citation_type', 'citation_type'),
    )

class ScholarlyVerification(Base):
    """Scholarly review and verification tracking"""
    __tablename__ = "scholarly_verification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"), nullable=False)
    scholar_name = Column(String(200), nullable=False)
    scholar_credentials = Column(Text)
    verification_status = Column(String(20))  # approved, rejected, needs_revision
    accuracy_rating = Column(Float)  # 0.0-1.0
    theological_soundness = Column(Float)  # 0.0-1.0
    source_authenticity = Column(Float)  # 0.0-1.0
    notes = Column(Text)
    recommendations = Column(Text)
    
    verified_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_verification_content', 'content_id'),
        Index('idx_verification_status', 'verification_status'),
        Index('idx_verification_scholar', 'scholar_name'),
    )

class IslamicKnowledgeGraph(Base):
    """Knowledge graph for Islamic concept relationships"""
    __tablename__ = "islamic_knowledge_graph"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_a = Column(String(200), nullable=False)
    concept_b = Column(String(200), nullable=False)
    relationship_type = Column(String(50))  # prerequisite, related, contradicts, supports
    strength = Column(Float)  # Relationship strength 0.0-1.0
    evidence_count = Column(Integer, default=0)
    scholarly_consensus = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_knowledge_graph_concepts', 'concept_a', 'concept_b'),
        Index('idx_knowledge_graph_type', 'relationship_type'),
    )

class AITrainingData(Base):
    """Curated training data for Islamic AI models"""
    __tablename__ = "ai_training_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"))
    instruction = Column(Text, nullable=False)
    input_text = Column(Text)
    output_text = Column(Text, nullable=False)
    quality_score = Column(Float)
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    topic = Column(Enum(IslamicTopicEnum))
    language = Column(Enum(ContentLanguage))
    
    # Training metadata
    model_version = Column(String(50))
    training_round = Column(Integer)
    validation_score = Column(Float)
    human_reviewed = Column(Boolean, default=False)
    reviewer_notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_training_topic_lang', 'topic', 'language'),
        Index('idx_training_quality', 'quality_score'),
        Index('idx_training_difficulty', 'difficulty_level'),
    )

class UserInteraction(Base):
    """User interactions for continuous learning"""
    __tablename__ = "user_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))  # Will link to user table
    content_id = Column(UUID(as_uuid=True), ForeignKey("islamic_content.id"))
    interaction_type = Column(String(50))  # view, like, share, cite, flag
    feedback_score = Column(Integer)  # 1-5 rating
    feedback_text = Column(Text)
    session_id = Column(UUID(as_uuid=True))
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_interaction_user', 'user_id'),
        Index('idx_interaction_content', 'content_id'),
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_interaction_date', 'created_at'),
    )
"""
Global Waqaf Tech - Multi-Tenant Database Models
Comprehensive database schema for digital waqf platform
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Index, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

Base = declarative_base()

# ============================================================================
# CORE MULTI-TENANT MODELS
# ============================================================================

class Organization(Base):
    """
    Organizations - Masajid, Islamic organizations, schools, etc.
    Central entity for multi-tenancy
    """
    __tablename__ = "organizations"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    # Organization Type
    type = Column(String(50), nullable=False)  # masjid, organization, school, business, other

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color (#000000)

    # Location
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), index=True)
    timezone = Column(String(50), default="UTC")

    # Contact Information
    website_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    social_links = Column(JSON)  # {facebook, instagram, twitter, youtube, tiktok, linkedin}

    # About
    description = Column(Text)
    mission_statement = Column(Text)
    founding_year = Column(Integer)

    # Subscription & Billing
    plan = Column(String(20), nullable=False, default="basic", index=True)  # basic, pro, enterprise
    subscription_status = Column(String(20), default="active")  # active, suspended, cancelled, trial
    subscription_started = Column(DateTime, default=datetime.utcnow)
    subscription_expires = Column(DateTime)
    trial_ends_at = Column(DateTime)

    # Billing
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))

    # Settings
    settings = Column(JSON, default={})  # Organization-specific settings and preferences

    # Features enabled (for custom plans)
    enabled_features = Column(ARRAY(String), default=[])

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)

    # Admin notes (for super admin only)
    admin_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    dua_generations = relationship("DuaGeneration", back_populates="organization", cascade="all, delete-orphan")
    story_generations = relationship("StoryGeneration", back_populates="organization", cascade="all, delete-orphan")
    saved_grants = relationship("SavedGrant", back_populates="organization", cascade="all, delete-orphan")
    marketplace_listings = relationship("MarketplaceListing", back_populates="organization", cascade="all, delete-orphan")
    social_posts = relationship("SocialPost", back_populates="organization", cascade="all, delete-orphan")
    social_profile = relationship("SocialProfile", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="organization", cascade="all, delete-orphan")
    feature_usage = relationship("FeatureUsage", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """
    Users with role-based access control
    Roles: super_admin, org_admin, org_user
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    phone = Column(String(50))
    bio = Column(Text)

    # Multi-tenancy & Authorization
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    role = Column(String(20), nullable=False, index=True)  # super_admin, org_admin, org_user

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)

    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    theme = Column(String(20), default="light")  # light, dark

    # Activity Tracking
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    last_activity = Column(DateTime)

    # Password Reset
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime)

    # Email Verification
    verification_token = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    dua_generations = relationship("DuaGeneration", back_populates="user")
    story_generations = relationship("StoryGeneration", back_populates="user")
    saved_grants = relationship("SavedGrant", back_populates="user")
    marketplace_listings_created = relationship("MarketplaceListing", foreign_keys="MarketplaceListing.user_id")
    social_posts = relationship("SocialPost", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="user")
    feature_usage = relationship("FeatureUsage", back_populates="user")


# ============================================================================
# DU'A & DHIKR STUDIO
# ============================================================================

class DuaGeneration(Base):
    """Track all dua generations with organization and user context"""
    __tablename__ = "dua_generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Request Parameters
    topic = Column(String(255))
    situation = Column(String(500))
    language = Column(String(10), default="en")
    level = Column(String(20))  # kids, adults
    custom_prompt = Column(Text)

    # Generated Content
    arabic_text = Column(Text)
    transliteration = Column(Text)
    translation = Column(Text)
    explanation = Column(Text)
    source_reference = Column(String(500))
    benefits = Column(JSON)  # Array of benefits

    # AI Metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    generation_time_ms = Column(Integer)

    # User Actions
    is_saved = Column(Boolean, default=False, index=True)
    is_favorite = Column(Boolean, default=False)
    times_copied = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="dua_generations")
    user = relationship("User", back_populates="dua_generations")


# ============================================================================
# KIDS STORY STUDIO
# ============================================================================

class StoryGeneration(Base):
    """Track all story generations"""
    __tablename__ = "story_generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Request Parameters
    age_range = Column(String(20))  # 3-5, 6-8, 9-12
    theme = Column(String(100), index=True)  # kindness, salah, honesty, etc.
    style = Column(String(20))  # short, medium, long
    language = Column(String(10), default="en")
    custom_prompt = Column(Text)

    # Generated Content
    title = Column(String(500))
    content = Column(Text)
    moral_lesson = Column(Text)
    islamic_teaching = Column(Text)
    discussion_questions = Column(JSON)  # Array of questions
    related_verses = Column(JSON)  # Array of Quran/Hadith references

    # AI Metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    generation_time_ms = Column(Integer)

    # User Actions
    is_saved = Column(Boolean, default=False, index=True)
    is_favorite = Column(Boolean, default=False)
    read_count = Column(Integer, default=0)
    rating = Column(Integer)  # 1-5 stars

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="story_generations")
    user = relationship("User", back_populates="story_generations")


# ============================================================================
# GRANT FINDER MODULE
# ============================================================================

class Grant(Base):
    """Grant opportunities database"""
    __tablename__ = "grants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    title = Column(String(500), nullable=False)
    funder_name = Column(String(255), nullable=False, index=True)
    funder_website = Column(String(500))

    # Location
    country = Column(String(100), index=True)
    region = Column(String(100))  # US, EU, Middle East, Global, etc.

    # Categorization
    type = Column(String(50), index=True)  # masjid, nonprofit, education, youth, immigrant, general
    categories = Column(ARRAY(String), index=True)  # Multiple categories

    # Amounts
    amount_min = Column(Integer)
    amount_max = Column(Integer)
    currency = Column(String(3), default="USD")

    # Dates
    deadline = Column(DateTime, index=True)
    opens_at = Column(DateTime)
    notification_sent = Column(Boolean, default=False)

    # Content
    link_url = Column(String(500))
    summary = Column(Text)
    requirements = Column(Text)
    eligibility = Column(Text)
    application_process = Column(Text)

    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)

    # Admin
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedGrant(Base):
    """Track organizations' saved grants and application progress"""
    __tablename__ = "saved_grants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    grant_id = Column(UUID(as_uuid=True), ForeignKey("grants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Tracking
    status = Column(String(20), default="interested", index=True)
    # Status options: interested, researching, drafting, submitted, awarded, rejected

    # Notes & AI
    notes = Column(Text)
    ai_summary = Column(Text)  # AI-generated grant summary
    ai_draft_response = Column(Text)  # AI-generated draft application
    ai_why_fit = Column(Text)  # AI explanation of why org fits

    # Dates
    submitted_date = Column(Date)
    decision_date = Column(Date)
    follow_up_date = Column(Date)

    # Award info
    amount_requested = Column(Integer)
    amount_awarded = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="saved_grants")
    user = relationship("User", back_populates="saved_grants")
    grant = relationship("Grant")

    # Unique constraint: one org can't save the same grant twice
    __table_args__ = (
        Index('idx_org_grant_unique', 'organization_id', 'grant_id', unique=True),
    )


# ============================================================================
# MARKETPLACE MODULE
# ============================================================================

class MarketplaceListing(Base):
    """Marketplace listings for Muslim businesses and services"""
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Basic Info
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, index=True)
    category = Column(String(50), index=True)  # business, service, course, event, product, tool

    # Content
    short_description = Column(String(500))
    long_description = Column(Text)

    # Media
    images = Column(JSON)  # Array of image URLs
    video_url = Column(String(500))
    logo_url = Column(String(500))

    # Location
    country = Column(String(100), index=True)
    city = Column(String(100))
    is_online = Column(Boolean, default=False)

    # Links
    website_url = Column(String(500))
    contact_email = Column(String(255))
    phone = Column(String(50))

    # Pricing (optional)
    price_min = Column(Float)
    price_max = Column(Float)
    currency = Column(String(3), default="USD")
    pricing_note = Column(String(500))

    # Status & Moderation
    is_active = Column(Boolean, default=True, index=True)
    is_approved = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)

    # Moderation
    rejection_reason = Column(Text)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # SEO & Tags
    tags = Column(ARRAY(String))
    meta_description = Column(String(500))

    # Stats
    view_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="marketplace_listings")


# ============================================================================
# LEARNING HUB MODULE
# ============================================================================

class Course(Base):
    """Islamic courses and educational content"""
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, index=True)

    # Categorization
    category = Column(String(50), index=True)  # Quran, Seerah, Fiqh, Kids, Parents, New Muslims
    level = Column(String(20), index=True)  # beginner, intermediate, advanced
    language = Column(String(10), default="en")

    # Content
    short_description = Column(String(500))
    long_description = Column(Text)
    learning_objectives = Column(JSON)  # Array of objectives
    prerequisites = Column(JSON)  # Array of prerequisites

    # Media
    thumbnail_url = Column(String(500))
    preview_video_url = Column(String(500))

    # Authorship
    created_by_org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    instructor_name = Column(String(255))
    instructor_bio = Column(Text)
    instructor_photo_url = Column(String(500))

    # Metadata
    duration_minutes = Column(Integer)
    lesson_count = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)
    is_free = Column(Boolean, default=True)

    # Stats
    enrollment_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order_index")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Individual lessons within courses"""
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Info
    title = Column(String(500), nullable=False)
    order_index = Column(Integer, nullable=False)

    # Content
    content_type = Column(String(20))  # text, video, audio
    content_text = Column(Text)
    content_url = Column(String(500))

    # Additional Resources
    resources = Column(JSON)  # Array of {title, url, type}

    # Metadata
    duration_minutes = Column(Integer)
    is_preview = Column(Boolean, default=False)  # Can be viewed without enrollment

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    """Track user enrollments in courses"""
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Progress
    completed_lessons = Column(JSON, default=[])  # Array of lesson IDs
    progress_percentage = Column(Integer, default=0)

    # Status
    status = Column(String(20), default="in_progress", index=True)  # in_progress, completed, dropped

    # Dates
    enrolled_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime)

    # Feedback
    rating = Column(Integer)  # 1-5 stars
    review = Column(Text)

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    organization = relationship("Organization", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")

    # Unique constraint
    __table_args__ = (
        Index('idx_user_course_unique', 'user_id', 'course_id', unique=True),
    )


# ============================================================================
# SOCIAL MEDIA STUDIO MODULE
# ============================================================================

class SocialProfile(Base):
    """Organization's social media profile settings"""
    __tablename__ = "social_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Audience
    main_audience = Column(String(100))  # local community, youth, parents, converts, general
    age_demographics = Column(ARRAY(String))  # teens, young_adults, adults, seniors

    # Platforms
    platforms = Column(JSON)  # {facebook: true, instagram: true, tiktok: false, youtube: true, twitter: false}

    # Preferences
    preferred_languages = Column(ARRAY(String), default=['en'])
    tone = Column(String(20), default="warm")  # formal, warm, youthful, simple, inspirational

    # Guidelines
    custom_hashtags = Column(ARRAY(String))
    topics_to_avoid = Column(ARRAY(String))
    special_guidelines = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="social_profile")


class SocialPost(Base):
    """Generated social media posts"""
    __tablename__ = "social_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Template & Input
    template_type = Column(String(50), index=True)
    # Options: event_reminder, jumuah_reminder, daily_dua, hadith_reflection,
    # quran_reflection, fundraising, volunteer_call, announcement, general

    input_description = Column(Text)

    # Generated Content
    caption_short = Column(Text)  # For Twitter/X (280 chars)
    caption_medium = Column(Text)  # For Instagram
    caption_long = Column(Text)  # For Facebook/LinkedIn
    hashtags = Column(ARRAY(String))
    image_prompt = Column(Text)  # For future image AI integration

    # AI Metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)

    # User Actions
    is_saved = Column(Boolean, default=False, index=True)
    is_posted = Column(Boolean, default=False)
    posted_platforms = Column(ARRAY(String))  # Which platforms it was posted to
    posted_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="social_posts")
    user = relationship("User", back_populates="social_posts")


# ============================================================================
# USAGE TRACKING & ANALYTICS
# ============================================================================

class FeatureUsage(Base):
    """Track feature usage for analytics and billing"""
    __tablename__ = "feature_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Feature Tracking
    feature_name = Column(String(50), index=True)
    # Options: dua_studio, story_studio, umrah_alerts, grant_finder,
    # marketplace, learning_hub, social_studio

    action = Column(String(50), index=True)  # generate, save, search, view, etc.

    # Metadata
    request_data = Column(JSON)  # Anonymized request parameters
    response_summary = Column(JSON)  # Summary of response

    # AI Costs (optional)
    tokens_used = Column(Integer)
    estimated_cost = Column(Float)

    # Performance
    processing_time_ms = Column(Integer)

    # Success
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="feature_usage")
    user = relationship("User", back_populates="feature_usage")

    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_org_feature_created', 'organization_id', 'feature_name', 'created_at'),
        Index('idx_feature_action_created', 'feature_name', 'action', 'created_at'),
    )


# ============================================================================
# LEGACY MODELS (Keep for backward compatibility)
# These are the original Islamic content models
# ============================================================================

class IslamicSource(Base):
    """Table for Islamic knowledge sources"""
    __tablename__ = "islamic_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)
    authority_level = Column(String(20), nullable=False)
    language = Column(String(10), nullable=False, default="ar")
    website_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    content_items = relationship("IslamicContent", back_populates="source")


class IslamicContent(Base):
    """Main table for Islamic content (Quran, Hadith, etc.)"""
    __tablename__ = "islamic_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("islamic_sources.id"), nullable=False)
    content_type = Column(String(50), nullable=False)

    arabic_text = Column(Text, nullable=False)
    english_text = Column(Text)
    transliteration = Column(Text)

    surah_number = Column(Integer)
    verse_number = Column(Integer)
    verse_key = Column(String(20))

    narrator_chain = Column(Text)
    hadith_number = Column(String(50))
    collection_book = Column(String(100))
    authenticity_grade = Column(String(20))

    topics = Column(ARRAY(String))
    fiqh_category = Column(String(100))

    attribution = Column(JSON)
    content_metadata = Column(JSON)

    search_vector = Column(Text)
    embedding_vector = Column(ARRAY(Float))

    verification_status = Column(String(20), default="pending")
    quality_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime)

    source = relationship("IslamicSource", back_populates="content_items")

    __table_args__ = (
        Index('idx_content_type', 'content_type'),
        Index('idx_surah_verse', 'surah_number', 'verse_number'),
        Index('idx_authenticity', 'authenticity_grade'),
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_db_models():
    """
    Initialize all database models
    This function can be called to create all tables
    """
    return Base.metadata


def get_all_models():
    """Return all model classes for migrations"""
    return [
        Organization,
        User,
        DuaGeneration,
        StoryGeneration,
        Grant,
        SavedGrant,
        MarketplaceListing,
        Course,
        Lesson,
        Enrollment,
        SocialProfile,
        SocialPost,
        FeatureUsage,
        IslamicSource,
        IslamicContent,
    ]

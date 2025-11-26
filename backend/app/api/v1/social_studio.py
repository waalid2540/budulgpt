"""
Social Media Studio API Endpoints - Multi-tenant Social Media Management
AI-powered social media content generation for masajid and Islamic organizations.

Plan-based access:
- Basic: Not available
- Pro: 50 posts/month
- Enterprise: Unlimited posts

Routes:
- GET /api/v1/social - Get my social profiles
- POST /api/v1/social/profiles - Create/update social profile
- GET /api/v1/social/profiles - List my profiles
- DELETE /api/v1/social/profiles/{id} - Delete profile

Post Generation:
- POST /api/v1/social/generate - Generate AI post
- GET /api/v1/social/posts - Get my generated posts
- GET /api/v1/social/posts/{id} - Get post details
- PATCH /api/v1/social/posts/{id} - Update post
- DELETE /api/v1/social/posts/{id} - Delete post
- POST /api/v1/social/posts/{id}/regenerate - Regenerate post

Templates:
- GET /api/v1/social/templates - Browse templates
- GET /api/v1/social/templates/{id} - Get template details
- POST /api/v1/social/templates/{id}/use - Generate from template

Statistics:
- GET /api/v1/social/stats - Usage statistics

Admin Routes:
- POST /api/v1/social/admin/templates - Create template (super admin)
- PATCH /api/v1/social/admin/templates/{id} - Update template (super admin)
- DELETE /api/v1/social/admin/templates/{id} - Delete template (super admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models_multitenant import (
    SocialProfile,
    SocialPost,
    Organization,
    User,
    FeatureUsage
)
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_organization,
    require_roles,
    require_feature
)
from app.core.permissions import UserRole, check_usage_limit
from pydantic import BaseModel, Field, validator

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class SocialProfileCreate(BaseModel):
    """Request body for creating a social profile"""
    platform: str = Field(..., description="facebook, instagram, twitter, linkedin")
    profile_name: str = Field(..., min_length=1, max_length=100)
    profile_url: Optional[str] = Field(None, max_length=500)
    profile_handle: Optional[str] = Field(None, max_length=100, description="@username")

    @validator('platform')
    def validate_platform(cls, v):
        allowed = ['facebook', 'instagram', 'twitter', 'linkedin']
        if v.lower() not in allowed:
            raise ValueError(f'Platform must be one of: {", ".join(allowed)}')
        return v.lower()


class SocialProfileResponse(BaseModel):
    """Response model for social profile"""
    id: uuid.UUID
    organization_id: uuid.UUID
    platform: str
    profile_name: str
    profile_url: Optional[str]
    profile_handle: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PostGenerateRequest(BaseModel):
    """Request body for generating a social media post"""
    topic: str = Field(..., min_length=3, max_length=200, description="Post topic or theme")
    platform: str = Field(..., description="Target platform: facebook, instagram, twitter, linkedin")
    tone: str = Field(default="professional", description="professional, friendly, inspirational, educational")
    include_hashtags: bool = Field(default=True)
    include_call_to_action: bool = Field(default=True)
    language: str = Field(default="en", description="en, ar")

    # Optional context
    target_audience: Optional[str] = Field(None, max_length=100)
    occasion: Optional[str] = Field(None, max_length=100, description="Ramadan, Eid, Jummah, etc.")

    @validator('platform')
    def validate_platform(cls, v):
        allowed = ['facebook', 'instagram', 'twitter', 'linkedin']
        if v.lower() not in allowed:
            raise ValueError(f'Platform must be one of: {", ".join(allowed)}')
        return v.lower()

    @validator('tone')
    def validate_tone(cls, v):
        allowed = ['professional', 'friendly', 'inspirational', 'educational']
        if v.lower() not in allowed:
            raise ValueError(f'Tone must be one of: {", ".join(allowed)}')
        return v.lower()


class PostUpdateRequest(BaseModel):
    """Request body for updating a post"""
    content: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_for: Optional[datetime] = None


class PostResponse(BaseModel):
    """Response model for social media post"""
    id: uuid.UUID
    organization_id: uuid.UUID
    platform: str
    topic: str
    tone: str
    content: str
    hashtags: List[str]
    word_count: int

    # Metadata
    language: str
    target_audience: Optional[str]
    occasion: Optional[str]

    # Scheduling
    scheduled_for: Optional[datetime]
    is_posted: bool
    posted_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialStatsResponse(BaseModel):
    """Statistics for social media usage"""
    total_posts_generated: int
    posts_this_month: int
    monthly_limit: int
    remaining_posts: int
    posts_by_platform: dict
    posts_by_tone: dict
    most_used_topics: List[dict]


class TemplateResponse(BaseModel):
    """Response model for post template"""
    id: str
    name: str
    description: str
    category: str
    platform: str
    example_content: str
    hashtags: List[str]


# ============================================================================
# SOCIAL PROFILE ROUTES
# ============================================================================

@router.post("/profiles", response_model=SocialProfileResponse, status_code=201)
async def create_social_profile(
    request: SocialProfileCreate,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("social_studio")),
    db: Session = Depends(get_db)
):
    """
    Create or update a social media profile for my organization.
    """
    # Check if profile already exists for this platform
    existing = db.query(SocialProfile).filter(
        and_(
            SocialProfile.organization_id == organization.id,
            SocialProfile.platform == request.platform
        )
    ).first()

    if existing:
        # Update existing
        existing.profile_name = request.profile_name
        existing.profile_url = request.profile_url
        existing.profile_handle = request.profile_handle
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    # Create new
    profile = SocialProfile(
        id=uuid.uuid4(),
        organization_id=organization.id,
        platform=request.platform,
        profile_name=request.profile_name,
        profile_url=request.profile_url,
        profile_handle=request.profile_handle,
        is_active=True
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get("/profiles", response_model=List[SocialProfileResponse])
async def get_my_social_profiles(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get all social media profiles for my organization.
    """
    profiles = db.query(SocialProfile).filter(
        SocialProfile.organization_id == organization.id
    ).order_by(SocialProfile.created_at).all()

    return profiles


@router.delete("/profiles/{profile_id}", status_code=204)
async def delete_social_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a social media profile.
    """
    profile = db.query(SocialProfile).filter(
        and_(
            SocialProfile.id == profile_id,
            SocialProfile.organization_id == organization.id
        )
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()

    return None


# ============================================================================
# POST GENERATION ROUTES
# ============================================================================

@router.post("/generate", response_model=PostResponse, status_code=201)
async def generate_social_post(
    request: PostGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("social_studio")),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered social media post.

    Plan limits:
    - Basic: Not available
    - Pro: 50 posts/month
    - Enterprise: Unlimited
    """
    # Check monthly usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_count = db.query(func.count(SocialPost.id)).filter(
        and_(
            SocialPost.organization_id == organization.id,
            SocialPost.created_at >= current_month_start
        )
    ).scalar()

    # Check usage limit
    check_usage_limit(organization.plan, "social_studio", monthly_count)

    # Generate post content based on platform and topic
    content = _generate_post_content(
        platform=request.platform,
        topic=request.topic,
        tone=request.tone,
        organization_name=organization.name,
        target_audience=request.target_audience,
        occasion=request.occasion,
        language=request.language
    )

    # Generate hashtags
    hashtags = _generate_hashtags(
        topic=request.topic,
        platform=request.platform,
        occasion=request.occasion
    ) if request.include_hashtags else []

    # Add call to action if requested
    if request.include_call_to_action:
        cta = _generate_call_to_action(platform=request.platform, organization_name=organization.name)
        content = f"{content}\n\n{cta}"

    # Create post record
    new_post = SocialPost(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        platform=request.platform,
        topic=request.topic,
        tone=request.tone,
        content=content,
        hashtags=hashtags,
        word_count=len(content.split()),
        language=request.language,
        target_audience=request.target_audience,
        occasion=request.occasion,
        is_posted=False
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="social_studio",
        usage_type="post_generated",
        metadata={
            "post_id": str(new_post.id),
            "platform": request.platform,
            "topic": request.topic
        }
    )
    db.add(usage)
    db.commit()

    return PostResponse(
        id=new_post.id,
        organization_id=new_post.organization_id,
        platform=new_post.platform,
        topic=new_post.topic,
        tone=new_post.tone,
        content=new_post.content,
        hashtags=new_post.hashtags or [],
        word_count=new_post.word_count,
        language=new_post.language,
        target_audience=new_post.target_audience,
        occasion=new_post.occasion,
        scheduled_for=new_post.scheduled_for,
        is_posted=new_post.is_posted,
        posted_at=new_post.posted_at,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at
    )


@router.get("/posts", response_model=List[PostResponse])
async def get_my_posts(
    platform: Optional[str] = Query(None),
    occasion: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get all generated posts for my organization.
    """
    query = db.query(SocialPost).filter(
        SocialPost.organization_id == organization.id
    )

    if platform:
        query = query.filter(SocialPost.platform == platform.lower())
    if occasion:
        query = query.filter(SocialPost.occasion.ilike(f"%{occasion}%"))

    query = query.order_by(SocialPost.created_at.desc())
    posts = query.offset(skip).limit(limit).all()

    return [
        PostResponse(
            id=post.id,
            organization_id=post.organization_id,
            platform=post.platform,
            topic=post.topic,
            tone=post.tone,
            content=post.content,
            hashtags=post.hashtags or [],
            word_count=post.word_count,
            language=post.language,
            target_audience=post.target_audience,
            occasion=post.occasion,
            scheduled_for=post.scheduled_for,
            is_posted=post.is_posted,
            posted_at=post.posted_at,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_details(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific post.
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.organization_id == organization.id
        )
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostResponse(
        id=post.id,
        organization_id=post.organization_id,
        platform=post.platform,
        topic=post.topic,
        tone=post.tone,
        content=post.content,
        hashtags=post.hashtags or [],
        word_count=post.word_count,
        language=post.language,
        target_audience=post.target_audience,
        occasion=post.occasion,
        scheduled_for=post.scheduled_for,
        is_posted=post.is_posted,
        posted_at=post.posted_at,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.patch("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    request: PostUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update a generated post.
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.organization_id == organization.id
        )
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update fields
    if request.content:
        post.content = request.content
        post.word_count = len(request.content.split())
    if request.hashtags is not None:
        post.hashtags = request.hashtags
    if request.scheduled_for is not None:
        post.scheduled_for = request.scheduled_for

    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        organization_id=post.organization_id,
        platform=post.platform,
        topic=post.topic,
        tone=post.tone,
        content=post.content,
        hashtags=post.hashtags or [],
        word_count=post.word_count,
        language=post.language,
        target_audience=post.target_audience,
        occasion=post.occasion,
        scheduled_for=post.scheduled_for,
        is_posted=post.is_posted,
        posted_at=post.posted_at,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a generated post.
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.organization_id == organization.id
        )
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return None


@router.post("/posts/{post_id}/regenerate", response_model=PostResponse)
async def regenerate_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Regenerate a post with the same parameters but new content.
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.organization_id == organization.id
        )
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Generate new content
    new_content = _generate_post_content(
        platform=post.platform,
        topic=post.topic,
        tone=post.tone,
        organization_name=organization.name,
        target_audience=post.target_audience,
        occasion=post.occasion,
        language=post.language
    )

    # Update post
    post.content = new_content
    post.word_count = len(new_content.split())
    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        organization_id=post.organization_id,
        platform=post.platform,
        topic=post.topic,
        tone=post.tone,
        content=post.content,
        hashtags=post.hashtags or [],
        word_count=post.word_count,
        language=post.language,
        target_audience=post.target_audience,
        occasion=post.occasion,
        scheduled_for=post.scheduled_for,
        is_posted=post.is_posted,
        posted_at=post.posted_at,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


# ============================================================================
# TEMPLATES
# ============================================================================

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available post templates.
    """
    templates = _get_builtin_templates()

    # Filter by platform
    if platform:
        templates = [t for t in templates if t["platform"] == platform.lower()]

    # Filter by category
    if category:
        templates = [t for t in templates if t["category"] == category.lower()]

    return [
        TemplateResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            category=t["category"],
            platform=t["platform"],
            example_content=t["example_content"],
            hashtags=t["hashtags"]
        )
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template_details(
    template_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific template.
    """
    templates = _get_builtin_templates()
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return TemplateResponse(
        id=template["id"],
        name=template["name"],
        description=template["description"],
        category=template["category"],
        platform=template["platform"],
        example_content=template["example_content"],
        hashtags=template["hashtags"]
    )


@router.post("/templates/{template_id}/use", response_model=PostResponse, status_code=201)
async def use_template(
    template_id: str,
    custom_text: Optional[str] = Query(None, description="Custom text to personalize template"),
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("social_studio")),
    db: Session = Depends(get_db)
):
    """
    Generate a post using a template.
    """
    templates = _get_builtin_templates()
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check monthly usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_count = db.query(func.count(SocialPost.id)).filter(
        and_(
            SocialPost.organization_id == organization.id,
            SocialPost.created_at >= current_month_start
        )
    ).scalar()

    check_usage_limit(organization.plan, "social_studio", monthly_count)

    # Customize template content
    content = template["example_content"].replace("[MASJID_NAME]", organization.name)
    if custom_text:
        content = f"{content}\n\n{custom_text}"

    # Create post
    new_post = SocialPost(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        platform=template["platform"],
        topic=template["name"],
        tone="professional",
        content=content,
        hashtags=template["hashtags"],
        word_count=len(content.split()),
        language="en",
        is_posted=False
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="social_studio",
        usage_type="template_used",
        metadata={"template_id": template_id, "template_name": template["name"]}
    )
    db.add(usage)
    db.commit()

    return PostResponse(
        id=new_post.id,
        organization_id=new_post.organization_id,
        platform=new_post.platform,
        topic=new_post.topic,
        tone=new_post.tone,
        content=new_post.content,
        hashtags=new_post.hashtags or [],
        word_count=new_post.word_count,
        language=new_post.language,
        target_audience=new_post.target_audience,
        occasion=new_post.occasion,
        scheduled_for=new_post.scheduled_for,
        is_posted=new_post.is_posted,
        posted_at=new_post.posted_at,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at
    )


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats", response_model=SocialStatsResponse)
async def get_social_stats(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get social media usage statistics for my organization.
    """
    from app.core.permissions import get_feature_limit

    # Total posts
    total = db.query(func.count(SocialPost.id)).filter(
        SocialPost.organization_id == organization.id
    ).scalar()

    # Posts this month
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = db.query(func.count(SocialPost.id)).filter(
        and_(
            SocialPost.organization_id == organization.id,
            SocialPost.created_at >= current_month_start
        )
    ).scalar()

    # Monthly limit
    monthly_limit = get_feature_limit(organization.plan, "social_studio")
    remaining = max(0, monthly_limit - this_month) if monthly_limit != -1 else -1

    # Posts by platform
    by_platform = db.query(
        SocialPost.platform,
        func.count(SocialPost.id).label("count")
    ).filter(
        SocialPost.organization_id == organization.id
    ).group_by(SocialPost.platform).all()

    # Posts by tone
    by_tone = db.query(
        SocialPost.tone,
        func.count(SocialPost.id).label("count")
    ).filter(
        SocialPost.organization_id == organization.id
    ).group_by(SocialPost.tone).all()

    # Most used topics
    topics = db.query(
        SocialPost.topic,
        func.count(SocialPost.id).label("count")
    ).filter(
        SocialPost.organization_id == organization.id
    ).group_by(SocialPost.topic).order_by(func.count(SocialPost.id).desc()).limit(5).all()

    return SocialStatsResponse(
        total_posts_generated=total,
        posts_this_month=this_month,
        monthly_limit=monthly_limit,
        remaining_posts=remaining,
        posts_by_platform={p: c for p, c in by_platform},
        posts_by_tone={t: c for t, c in by_tone},
        most_used_topics=[{"topic": t, "count": c} for t, c in topics]
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_post_content(
    platform: str,
    topic: str,
    tone: str,
    organization_name: str,
    target_audience: Optional[str] = None,
    occasion: Optional[str] = None,
    language: str = "en"
) -> str:
    """
    Generate AI-powered social media post content.
    This is a simplified version - in production, use OpenAI/Claude API.
    """
    # Platform-specific character limits
    limits = {
        "twitter": 280,
        "instagram": 2200,
        "facebook": 5000,
        "linkedin": 3000
    }

    # Generate content based on parameters
    if occasion:
        intro = f"As we approach {occasion}, "
    else:
        intro = ""

    if tone == "inspirational":
        content = f"{intro}Alhamdulillah, let's reflect on {topic}. At {organization_name}, we believe in the power of community and faith. {topic.capitalize()} reminds us of our purpose and connection to Allah SWT."
    elif tone == "educational":
        content = f"{intro}Did you know? {topic.capitalize()} is an important aspect of our faith. Join us at {organization_name} to learn more about {topic} and deepen your understanding of Islam."
    elif tone == "friendly":
        content = f"{intro}Assalamu Alaikum! We're excited to share with you about {topic}. Come join us at {organization_name} - your community masjid where everyone is family!"
    else:  # professional
        content = f"{intro}{organization_name} invites you to explore {topic}. We offer comprehensive programs and resources to strengthen your faith and knowledge."

    if target_audience:
        content += f" Perfect for {target_audience}."

    return content[:limits.get(platform, 2000)]


def _generate_hashtags(topic: str, platform: str, occasion: Optional[str] = None) -> List[str]:
    """
    Generate relevant hashtags for the post.
    """
    base_tags = ["#Islam", "#Muslim", "#Masjid", "#Community"]

    # Topic-specific tags
    topic_tags = [f"#{topic.replace(' ', '')}"]

    # Occasion-specific tags
    occasion_tags = []
    if occasion:
        occasion_tags = [f"#{occasion.replace(' ', '')}"]
        if occasion.lower() == "ramadan":
            occasion_tags.extend(["#Ramadan2024", "#BlessedMonth"])
        elif occasion.lower() == "eid":
            occasion_tags.extend(["#EidMubarak", "#EidAlFitr"])
        elif occasion.lower() == "jummah":
            occasion_tags.extend(["#JummahMubarak", "#FridayPrayer"])

    # Platform-specific count
    if platform == "twitter":
        return (base_tags + topic_tags + occasion_tags)[:3]
    elif platform == "instagram":
        return (base_tags + topic_tags + occasion_tags)[:10]
    else:
        return (base_tags + topic_tags + occasion_tags)[:5]


def _generate_call_to_action(platform: str, organization_name: str) -> str:
    """
    Generate call to action for the post.
    """
    ctas = [
        f"Visit {organization_name} today!",
        "Join our community programs.",
        "Share with your family and friends!",
        "Follow us for more Islamic content.",
        "Contact us to learn more."
    ]

    import random
    return random.choice(ctas)


def _get_builtin_templates() -> List[dict]:
    """
    Get list of built-in post templates.
    """
    return [
        {
            "id": "jummah-reminder",
            "name": "Jummah Reminder",
            "description": "Weekly Friday prayer reminder",
            "category": "prayer",
            "platform": "instagram",
            "example_content": "Jummah Mubarak! 🕌\n\nJoin us at [MASJID_NAME] for Jummah prayer this Friday.\n\nKhutbah starts at 1:00 PM\nPrayer at 1:30 PM\n\nMay Allah accept your prayers and grant you ease.",
            "hashtags": ["#JummahMubarak", "#FridayPrayer", "#Islam", "#Muslim", "#Masjid"]
        },
        {
            "id": "ramadan-iftar",
            "name": "Ramadan Iftar Invitation",
            "description": "Invite community to iftar",
            "category": "event",
            "platform": "facebook",
            "example_content": "🌙 Ramadan Kareem!\n\n[MASJID_NAME] invites you to join us for community Iftar this evening.\n\nIftar Time: Maghrib\nLocation: Main Prayer Hall\n\nBring your family and friends. Everyone is welcome!\n\nMay Allah accept your fasting and prayers.",
            "hashtags": ["#Ramadan", "#Iftar", "#Community", "#Islam", "#Masjid"]
        },
        {
            "id": "fundraiser",
            "name": "Fundraiser Announcement",
            "description": "Announce fundraising campaign",
            "category": "fundraising",
            "platform": "linkedin",
            "example_content": "Support Your Community Masjid\n\n[MASJID_NAME] is launching a fundraising campaign to expand our facilities and serve more community members.\n\nYour donations will help us:\n✅ Expand prayer facilities\n✅ Enhance educational programs\n✅ Support community services\n\nDonate today and earn continuous rewards. Every contribution makes a difference.",
            "hashtags": ["#Sadaqah", "#Charity", "#CommunitySupport", "#Islam", "#Masjid"]
        },
        {
            "id": "quran-class",
            "name": "Quran Class Announcement",
            "description": "Promote Quran learning programs",
            "category": "education",
            "platform": "instagram",
            "example_content": "📖 Learn the Quran with us!\n\n[MASJID_NAME] is offering Quran classes for all ages.\n\n🎯 Tajweed & Recitation\n🎯 Memorization (Hifz)\n🎯 Arabic Language\n\nEnrollment is now open. Limited seats available!\n\nContact us to register your family today.",
            "hashtags": ["#QuranClass", "#IslamicEducation", "#LearnQuran", "#Masjid", "#Community"]
        },
        {
            "id": "eid-wishes",
            "name": "Eid Mubarak Wishes",
            "description": "Eid greetings to community",
            "category": "occasion",
            "platform": "facebook",
            "example_content": "🌙 Eid Mubarak! 🌙\n\nFrom all of us at [MASJID_NAME], we wish you and your family a blessed Eid filled with joy, peace, and prosperity.\n\nEid Prayer Details:\nTime: 8:00 AM & 9:30 AM\nLocation: Main Prayer Hall\n\nTaqabbal Allahu minna wa minkum!\nMay Allah accept from us and from you!",
            "hashtags": ["#EidMubarak", "#EidAlFitr", "#Islam", "#Muslim", "#Celebration"]
        }
    ]


# Note: In production, integrate with OpenAI/Claude API for true AI generation
# Example:
# def _generate_post_content(...):
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{
#             "role": "system",
#             "content": "You are a social media expert for Islamic organizations..."
#         }]
#     )
#     return response.choices[0].message.content

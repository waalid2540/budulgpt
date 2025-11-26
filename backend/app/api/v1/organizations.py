"""
Global Waqaf Tech - Organization Management API
CRUD operations for organizations, settings, and plan management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models_multitenant import Organization, User
from app.core.deps import (
    get_current_user,
    get_current_organization,
    get_super_admin,
    get_org_admin_or_super,
    get_pagination_params,
)
from app.core.permissions import Plan, is_plan_upgrade


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class OrganizationCreate(BaseModel):
    """Create new organization (super admin only)"""
    name: str
    slug: Optional[str] = None
    type: str = "masjid"  # masjid, organization, school, business, other
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    plan: str = "basic"

    @validator('plan')
    def validate_plan(cls, v):
        if v not in Plan.all_plans():
            raise ValueError(f"Invalid plan. Must be one of: {', '.join(Plan.all_plans())}")
        return v


class OrganizationUpdate(BaseModel):
    """Update organization details"""
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    mission_statement: Optional[str] = None
    founding_year: Optional[int] = None


class SocialLinksUpdate(BaseModel):
    """Update social media links"""
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    linkedin: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Organization details response"""
    id: str
    name: str
    slug: str
    type: str
    logo_url: Optional[str]
    primary_color: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    website_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    description: Optional[str]
    plan: str
    subscription_status: str
    subscription_expires: Optional[datetime]
    is_active: bool
    is_verified: bool
    created_at: datetime
    user_count: Optional[int] = None

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """List of organizations with pagination"""
    organizations: List[OrganizationResponse]
    total: int
    skip: int
    limit: int


class PlanUpdateRequest(BaseModel):
    """Update organization plan (super admin only)"""
    plan: str

    @validator('plan')
    def validate_plan(cls, v):
        if v not in Plan.all_plans():
            raise ValueError(f"Invalid plan. Must be one of: {', '.join(Plan.all_plans())}")
        return v


# ============================================================================
# ORGANIZATION CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: OrganizationCreate,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new organization (super admin only)

    - Creates organization with specified plan
    - Generates unique slug
    """
    # Generate slug if not provided
    if request.slug:
        slug = request.slug
    else:
        base_slug = request.name.lower().replace(" ", "-").replace("_", "-")
        slug = base_slug
        counter = 1

        while db.query(Organization).filter(Organization.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

    # Check slug uniqueness
    if db.query(Organization).filter(Organization.slug == slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with slug '{slug}' already exists"
        )

    # Create organization
    organization = Organization(
        id=uuid.uuid4(),
        name=request.name,
        slug=slug,
        type=request.type,
        email=request.email,
        phone=request.phone,
        city=request.city,
        state=request.state,
        country=request.country,
        plan=request.plan,
        subscription_status="active",
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        type=organization.type,
        logo_url=organization.logo_url,
        primary_color=organization.primary_color,
        city=organization.city,
        state=organization.state,
        country=organization.country,
        website_url=organization.website_url,
        email=organization.email,
        phone=organization.phone,
        description=organization.description,
        plan=organization.plan,
        subscription_status=organization.subscription_status,
        subscription_expires=organization.subscription_expires,
        is_active=organization.is_active,
        is_verified=organization.is_verified,
        created_at=organization.created_at,
    )


@router.get("/", response_model=OrganizationListResponse)
async def list_organizations(
    current_user: User = Depends(get_super_admin),
    pagination: dict = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search by name, email, or city"),
    plan: Optional[str] = Query(None, description="Filter by plan"),
    country: Optional[str] = Query(None, description="Filter by country"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    List all organizations (super admin only)

    - Supports pagination, search, and filtering
    - Returns organization count per org
    """
    query = db.query(Organization)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Organization.name.ilike(search_term)) |
            (Organization.email.ilike(search_term)) |
            (Organization.city.ilike(search_term))
        )

    if plan:
        query = query.filter(Organization.plan == plan)

    if country:
        query = query.filter(Organization.country == country)

    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    organizations = query.order_by(Organization.created_at.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()

    # Get user counts for each organization
    org_ids = [org.id for org in organizations]
    user_counts = db.query(
        User.organization_id,
        func.count(User.id).label('count')
    ).filter(User.organization_id.in_(org_ids)).group_by(User.organization_id).all()

    user_count_map = {str(org_id): count for org_id, count in user_counts}

    # Build response
    org_responses = []
    for org in organizations:
        org_responses.append(OrganizationResponse(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            type=org.type,
            logo_url=org.logo_url,
            primary_color=org.primary_color,
            city=org.city,
            state=org.state,
            country=org.country,
            website_url=org.website_url,
            email=org.email,
            phone=org.phone,
            description=org.description,
            plan=org.plan,
            subscription_status=org.subscription_status,
            subscription_expires=org.subscription_expires,
            is_active=org.is_active,
            is_verified=org.is_verified,
            created_at=org.created_at,
            user_count=user_count_map.get(str(org.id), 0)
        ))

    return OrganizationListResponse(
        organizations=org_responses,
        total=total,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get current user's organization details
    """
    # Get user count
    user_count = db.query(func.count(User.id)).filter(
        User.organization_id == organization.id
    ).scalar()

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        type=organization.type,
        logo_url=organization.logo_url,
        primary_color=organization.primary_color,
        city=organization.city,
        state=organization.state,
        country=organization.country,
        website_url=organization.website_url,
        email=organization.email,
        phone=organization.phone,
        description=organization.description,
        plan=organization.plan,
        subscription_status=organization.subscription_status,
        subscription_expires=organization.subscription_expires,
        is_active=organization.is_active,
        is_verified=organization.is_verified,
        created_at=organization.created_at,
        user_count=user_count
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get organization by ID (super admin only)
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get user count
    user_count = db.query(func.count(User.id)).filter(
        User.organization_id == organization.id
    ).scalar()

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        type=organization.type,
        logo_url=organization.logo_url,
        primary_color=organization.primary_color,
        city=organization.city,
        state=organization.state,
        country=organization.country,
        website_url=organization.website_url,
        email=organization.email,
        phone=organization.phone,
        description=organization.description,
        plan=organization.plan,
        subscription_status=organization.subscription_status,
        subscription_expires=organization.subscription_expires,
        is_active=organization.is_active,
        is_verified=organization.is_verified,
        created_at=organization.created_at,
        user_count=user_count
    )


@router.patch("/me", response_model=OrganizationResponse)
async def update_my_organization(
    request: OrganizationUpdate,
    current_user: User = Depends(get_org_admin_or_super),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update current organization details (org admin or super admin)
    """
    # Update fields if provided
    update_data = request.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(organization)

    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        type=organization.type,
        logo_url=organization.logo_url,
        primary_color=organization.primary_color,
        city=organization.city,
        state=organization.state,
        country=organization.country,
        website_url=organization.website_url,
        email=organization.email,
        phone=organization.phone,
        description=organization.description,
        plan=organization.plan,
        subscription_status=organization.subscription_status,
        subscription_expires=organization.subscription_expires,
        is_active=organization.is_active,
        is_verified=organization.is_verified,
        created_at=organization.created_at,
    )


@router.patch("/me/social-links")
async def update_social_links(
    request: SocialLinksUpdate,
    current_user: User = Depends(get_org_admin_or_super),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update organization social media links
    """
    # Get existing social links or create new dict
    social_links = organization.social_links or {}

    # Update with new values
    update_data = request.dict(exclude_unset=True)
    social_links.update(update_data)

    organization.social_links = social_links
    organization.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "Social links updated successfully",
        "social_links": social_links
    }


@router.patch("/{organization_id}/plan")
async def update_organization_plan(
    organization_id: uuid.UUID,
    request: PlanUpdateRequest,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update organization plan (super admin only)
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    old_plan = organization.plan
    organization.plan = request.plan
    organization.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": f"Plan updated from {old_plan} to {request.plan}",
        "organization_id": str(organization.id),
        "old_plan": old_plan,
        "new_plan": request.plan,
        "is_upgrade": is_plan_upgrade(old_plan, request.plan)
    }


@router.patch("/{organization_id}/activate")
async def activate_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Activate organization (super admin only)
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    organization.is_active = True
    organization.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "Organization activated successfully"
    }


@router.patch("/{organization_id}/deactivate")
async def deactivate_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate organization (super admin only)
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    organization.is_active = False
    organization.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "Organization deactivated successfully"
    }


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete organization and all associated data (super admin only)

    WARNING: This will cascade delete all users, generations, and data!
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get counts before deletion
    user_count = db.query(func.count(User.id)).filter(
        User.organization_id == organization.id
    ).scalar()

    org_name = organization.name

    # Delete organization (cascade will handle related records)
    db.delete(organization)
    db.commit()

    return {
        "success": True,
        "message": f"Organization '{org_name}' deleted successfully",
        "deleted_users": user_count,
    }


# ============================================================================
# STATISTICS & ANALYTICS
# ============================================================================

@router.get("/me/stats")
async def get_organization_stats(
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get statistics for current organization
    """
    from app.db.models_multitenant import (
        DuaGeneration, StoryGeneration, SavedGrant,
        MarketplaceListing, SocialPost, Enrollment
    )

    # Count users
    user_count = db.query(func.count(User.id)).filter(
        User.organization_id == organization.id
    ).scalar()

    # Count generations
    dua_count = db.query(func.count(DuaGeneration.id)).filter(
        DuaGeneration.organization_id == organization.id
    ).scalar()

    story_count = db.query(func.count(StoryGeneration.id)).filter(
        StoryGeneration.organization_id == organization.id
    ).scalar()

    # Count saved grants
    grant_count = db.query(func.count(SavedGrant.id)).filter(
        SavedGrant.organization_id == organization.id
    ).scalar()

    # Count marketplace listings
    listing_count = db.query(func.count(MarketplaceListing.id)).filter(
        MarketplaceListing.organization_id == organization.id
    ).scalar()

    # Count social posts
    social_post_count = db.query(func.count(SocialPost.id)).filter(
        SocialPost.organization_id == organization.id
    ).scalar()

    # Count enrollments
    enrollment_count = db.query(func.count(Enrollment.id)).filter(
        Enrollment.organization_id == organization.id
    ).scalar()

    return {
        "organization_id": str(organization.id),
        "organization_name": organization.name,
        "plan": organization.plan,
        "subscription_status": organization.subscription_status,
        "stats": {
            "users": user_count,
            "duas_generated": dua_count,
            "stories_generated": story_count,
            "saved_grants": grant_count,
            "marketplace_listings": listing_count,
            "social_posts": social_post_count,
            "course_enrollments": enrollment_count,
        }
    }

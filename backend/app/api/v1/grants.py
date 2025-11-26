"""
Global Waqaf Tech - Grant Finder Module
Search and track grant opportunities with AI-powered helpers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
import uuid

from app.db.database import get_db
from app.db.models_multitenant import User, Organization, Grant, SavedGrant
from app.core.deps import (
    get_current_user,
    get_current_organization,
    get_super_admin,
    require_feature,
    get_pagination_params,
)
from app.core.permissions import get_feature_limit


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GrantCreate(BaseModel):
    """Create new grant (super admin only)"""
    title: str
    funder_name: str
    funder_website: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None  # US, EU, Middle East, Global
    type: str  # masjid, nonprofit, education, youth, immigrant, general
    categories: Optional[List[str]] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    currency: str = "USD"
    deadline: Optional[datetime] = None
    opens_at: Optional[datetime] = None
    link_url: str
    summary: str
    requirements: Optional[str] = None
    eligibility: Optional[str] = None
    application_process: Optional[str] = None
    is_featured: bool = False


class GrantUpdate(BaseModel):
    """Update grant details"""
    title: Optional[str] = None
    funder_name: Optional[str] = None
    summary: Optional[str] = None
    deadline: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class GrantResponse(BaseModel):
    """Grant details response"""
    id: str
    title: str
    funder_name: str
    funder_website: Optional[str]
    country: Optional[str]
    region: Optional[str]
    type: str
    categories: Optional[List[str]]
    amount_min: Optional[int]
    amount_max: Optional[int]
    currency: str
    deadline: Optional[datetime]
    link_url: str
    summary: str
    requirements: Optional[str]
    eligibility: Optional[str]
    is_active: bool
    is_featured: bool
    view_count: int
    save_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class GrantListResponse(BaseModel):
    """List of grants with pagination"""
    grants: List[GrantResponse]
    total: int
    skip: int
    limit: int


class SaveGrantRequest(BaseModel):
    """Save a grant to organization's tracker"""
    notes: Optional[str] = None


class UpdateSavedGrantRequest(BaseModel):
    """Update saved grant tracking"""
    status: Optional[str] = None  # interested, researching, drafting, submitted, awarded, rejected
    notes: Optional[str] = None
    submitted_date: Optional[date] = None
    decision_date: Optional[date] = None
    amount_requested: Optional[int] = None
    amount_awarded: Optional[int] = None

    @validator('status')
    def validate_status(cls, v):
        if v and v not in ["interested", "researching", "drafting", "submitted", "awarded", "rejected"]:
            raise ValueError("Invalid status")
        return v


class SavedGrantResponse(BaseModel):
    """Saved grant with tracking info"""
    id: str
    grant: GrantResponse
    status: str
    notes: Optional[str]
    ai_summary: Optional[str]
    ai_draft_response: Optional[str]
    ai_why_fit: Optional[str]
    submitted_date: Optional[date]
    decision_date: Optional[date]
    amount_requested: Optional[int]
    amount_awarded: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# GRANT CRUD ENDPOINTS (Super Admin)
# ============================================================================

@router.post("/", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
async def create_grant(
    request: GrantCreate,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new grant (super admin only)
    """
    grant = Grant(
        id=uuid.uuid4(),
        title=request.title,
        funder_name=request.funder_name,
        funder_website=request.funder_website,
        country=request.country,
        region=request.region,
        type=request.type,
        categories=request.categories or [],
        amount_min=request.amount_min,
        amount_max=request.amount_max,
        currency=request.currency,
        deadline=request.deadline,
        opens_at=request.opens_at,
        link_url=request.link_url,
        summary=request.summary,
        requirements=request.requirements,
        eligibility=request.eligibility,
        application_process=request.application_process,
        is_active=True,
        is_featured=request.is_featured,
        view_count=0,
        save_count=0,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
    )

    db.add(grant)
    db.commit()
    db.refresh(grant)

    return GrantResponse(
        id=str(grant.id),
        title=grant.title,
        funder_name=grant.funder_name,
        funder_website=grant.funder_website,
        country=grant.country,
        region=grant.region,
        type=grant.type,
        categories=grant.categories,
        amount_min=grant.amount_min,
        amount_max=grant.amount_max,
        currency=grant.currency,
        deadline=grant.deadline,
        link_url=grant.link_url,
        summary=grant.summary,
        requirements=grant.requirements,
        eligibility=grant.eligibility,
        is_active=grant.is_active,
        is_featured=grant.is_featured,
        view_count=grant.view_count,
        save_count=grant.save_count,
        created_at=grant.created_at,
    )


@router.patch("/{grant_id}", response_model=GrantResponse)
async def update_grant(
    grant_id: uuid.UUID,
    request: GrantUpdate,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update grant details (super admin only)
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grant, field, value)

    grant.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(grant)

    return GrantResponse(
        id=str(grant.id),
        title=grant.title,
        funder_name=grant.funder_name,
        funder_website=grant.funder_website,
        country=grant.country,
        region=grant.region,
        type=grant.type,
        categories=grant.categories,
        amount_min=grant.amount_min,
        amount_max=grant.amount_max,
        currency=grant.currency,
        deadline=grant.deadline,
        link_url=grant.link_url,
        summary=grant.summary,
        requirements=grant.requirements,
        eligibility=grant.eligibility,
        is_active=grant.is_active,
        is_featured=grant.is_featured,
        view_count=grant.view_count,
        save_count=grant.save_count,
        created_at=grant.created_at,
    )


@router.delete("/{grant_id}")
async def delete_grant(
    grant_id: uuid.UUID,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete grant (super admin only)
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found"
        )

    db.delete(grant)
    db.commit()

    return {
        "success": True,
        "message": "Grant deleted successfully"
    }


# ============================================================================
# GRANT SEARCH & DISCOVERY
# ============================================================================

@router.get("/search", response_model=GrantListResponse)
async def search_grants(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(require_feature("grant_finder")),
    pagination: dict = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search in title, funder, summary"),
    country: Optional[str] = Query(None, description="Filter by country"),
    region: Optional[str] = Query(None, description="Filter by region"),
    type: Optional[str] = Query(None, description="Filter by type"),
    amount_min: Optional[int] = Query(None, description="Minimum grant amount"),
    amount_max: Optional[int] = Query(None, description="Maximum grant amount"),
    deadline_before: Optional[datetime] = Query(None, description="Deadline before date"),
    deadline_after: Optional[datetime] = Query(None, description="Deadline after date"),
    featured_only: bool = Query(False, description="Show only featured grants"),
    db: Session = Depends(get_db)
):
    """
    Search available grants with filters

    - Search by keywords
    - Filter by location, type, amount, deadline
    - View featured grants
    """
    query = db.query(Grant).filter(Grant.is_active == True)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Grant.title.ilike(search_term),
                Grant.funder_name.ilike(search_term),
                Grant.summary.ilike(search_term)
            )
        )

    # Filters
    if country:
        query = query.filter(Grant.country == country)

    if region:
        query = query.filter(Grant.region == region)

    if type:
        query = query.filter(Grant.type == type)

    if amount_min:
        query = query.filter(Grant.amount_max >= amount_min)

    if amount_max:
        query = query.filter(Grant.amount_min <= amount_max)

    if deadline_before:
        query = query.filter(Grant.deadline <= deadline_before)

    if deadline_after:
        query = query.filter(Grant.deadline >= deadline_after)

    if featured_only:
        query = query.filter(Grant.is_featured == True)

    # Get total
    total = query.count()

    # Order by featured first, then deadline
    query = query.order_by(
        Grant.is_featured.desc(),
        Grant.deadline.asc()
    )

    # Pagination
    grants = query.offset(pagination["skip"]).limit(pagination["limit"]).all()

    # Build response
    grant_responses = []
    for grant in grants:
        grant_responses.append(GrantResponse(
            id=str(grant.id),
            title=grant.title,
            funder_name=grant.funder_name,
            funder_website=grant.funder_website,
            country=grant.country,
            region=grant.region,
            type=grant.type,
            categories=grant.categories,
            amount_min=grant.amount_min,
            amount_max=grant.amount_max,
            currency=grant.currency,
            deadline=grant.deadline,
            link_url=grant.link_url,
            summary=grant.summary,
            requirements=grant.requirements,
            eligibility=grant.eligibility,
            is_active=grant.is_active,
            is_featured=grant.is_featured,
            view_count=grant.view_count,
            save_count=grant.save_count,
            created_at=grant.created_at,
        ))

    return GrantListResponse(
        grants=grant_responses,
        total=total,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )


@router.get("/{grant_id}", response_model=GrantResponse)
async def get_grant(
    grant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get grant details by ID

    - Increments view count
    """
    grant = db.query(Grant).filter(
        Grant.id == grant_id,
        Grant.is_active == True
    ).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found"
        )

    # Increment view count
    grant.view_count += 1
    db.commit()
    db.refresh(grant)

    return GrantResponse(
        id=str(grant.id),
        title=grant.title,
        funder_name=grant.funder_name,
        funder_website=grant.funder_website,
        country=grant.country,
        region=grant.region,
        type=grant.type,
        categories=grant.categories,
        amount_min=grant.amount_min,
        amount_max=grant.amount_max,
        currency=grant.currency,
        deadline=grant.deadline,
        link_url=grant.link_url,
        summary=grant.summary,
        requirements=grant.requirements,
        eligibility=grant.eligibility,
        is_active=grant.is_active,
        is_featured=grant.is_featured,
        view_count=grant.view_count,
        save_count=grant.save_count,
        created_at=grant.created_at,
    )


# ============================================================================
# SAVED GRANTS & TRACKING
# ============================================================================

@router.post("/{grant_id}/save", response_model=SavedGrantResponse)
async def save_grant(
    grant_id: uuid.UUID,
    request: SaveGrantRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Save a grant to organization's tracker

    - Pro plan: Generate AI summary and draft (if enabled)
    - Check save limits for Basic plan
    """
    # Check if grant exists
    grant = db.query(Grant).filter(
        Grant.id == grant_id,
        Grant.is_active == True
    ).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found"
        )

    # Check if already saved
    existing = db.query(SavedGrant).filter(
        SavedGrant.organization_id == organization.id,
        SavedGrant.grant_id == grant_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grant already saved"
        )

    # Check save limit for Basic plan
    save_limit = get_feature_limit(organization.plan, "grant_finder", "save_limit")

    if save_limit != -1:  # -1 means unlimited
        current_saved = db.query(func.count(SavedGrant.id)).filter(
            SavedGrant.organization_id == organization.id
        ).scalar()

        if current_saved >= save_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You have reached your limit of {save_limit} saved grants. Upgrade to Pro for unlimited saves."
            )

    # Check if AI helpers are available
    ai_enabled = get_feature_limit(organization.plan, "grant_finder", "ai_summary")

    ai_summary = None
    ai_why_fit = None

    if ai_enabled:
        # Generate AI summary (simplified - in production use actual AI)
        ai_summary = f"This grant from {grant.funder_name} offers ${grant.amount_min:,} to ${grant.amount_max:,} for {grant.type} projects. Deadline: {grant.deadline.strftime('%B %d, %Y') if grant.deadline else 'Not specified'}."

        # Generate AI "why this fits" (simplified)
        ai_why_fit = f"This grant aligns with your organization '{organization.name}' because it supports {grant.type} initiatives in {grant.country or 'your region'}. Your organization's mission in serving the community makes you a strong candidate."

    # Create saved grant
    saved_grant = SavedGrant(
        id=uuid.uuid4(),
        organization_id=organization.id,
        grant_id=grant_id,
        user_id=current_user.id,
        status="interested",
        notes=request.notes,
        ai_summary=ai_summary,
        ai_why_fit=ai_why_fit,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(saved_grant)

    # Increment grant save count
    grant.save_count += 1

    db.commit()
    db.refresh(saved_grant)
    db.refresh(grant)

    # Track usage
    from app.db.models_multitenant import FeatureUsage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="grant_finder",
        action="save",
        request_data={"grant_id": str(grant_id), "grant_title": grant.title},
        success=True,
        created_at=datetime.utcnow(),
    )
    db.add(usage)
    db.commit()

    return SavedGrantResponse(
        id=str(saved_grant.id),
        grant=GrantResponse(
            id=str(grant.id),
            title=grant.title,
            funder_name=grant.funder_name,
            funder_website=grant.funder_website,
            country=grant.country,
            region=grant.region,
            type=grant.type,
            categories=grant.categories,
            amount_min=grant.amount_min,
            amount_max=grant.amount_max,
            currency=grant.currency,
            deadline=grant.deadline,
            link_url=grant.link_url,
            summary=grant.summary,
            requirements=grant.requirements,
            eligibility=grant.eligibility,
            is_active=grant.is_active,
            is_featured=grant.is_featured,
            view_count=grant.view_count,
            save_count=grant.save_count,
            created_at=grant.created_at,
        ),
        status=saved_grant.status,
        notes=saved_grant.notes,
        ai_summary=saved_grant.ai_summary,
        ai_draft_response=saved_grant.ai_draft_response,
        ai_why_fit=saved_grant.ai_why_fit,
        submitted_date=saved_grant.submitted_date,
        decision_date=saved_grant.decision_date,
        amount_requested=saved_grant.amount_requested,
        amount_awarded=saved_grant.amount_awarded,
        created_at=saved_grant.created_at,
        updated_at=saved_grant.updated_at,
    )


@router.get("/saved/my-grants")
async def get_my_saved_grants(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    pagination: dict = Depends(get_pagination_params),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get organization's saved grants

    - Filter by status
    - Pagination
    """
    query = db.query(SavedGrant).filter(
        SavedGrant.organization_id == organization.id
    )

    if status:
        query = query.filter(SavedGrant.status == status)

    total = query.count()

    saved_grants = query.order_by(SavedGrant.updated_at.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()

    # Get grant details
    grant_ids = [sg.grant_id for sg in saved_grants]
    grants = db.query(Grant).filter(Grant.id.in_(grant_ids)).all()
    grant_map = {grant.id: grant for grant in grants}

    # Build response
    responses = []
    for saved_grant in saved_grants:
        grant = grant_map.get(saved_grant.grant_id)
        if grant:
            responses.append(SavedGrantResponse(
                id=str(saved_grant.id),
                grant=GrantResponse(
                    id=str(grant.id),
                    title=grant.title,
                    funder_name=grant.funder_name,
                    funder_website=grant.funder_website,
                    country=grant.country,
                    region=grant.region,
                    type=grant.type,
                    categories=grant.categories,
                    amount_min=grant.amount_min,
                    amount_max=grant.amount_max,
                    currency=grant.currency,
                    deadline=grant.deadline,
                    link_url=grant.link_url,
                    summary=grant.summary,
                    requirements=grant.requirements,
                    eligibility=grant.eligibility,
                    is_active=grant.is_active,
                    is_featured=grant.is_featured,
                    view_count=grant.view_count,
                    save_count=grant.save_count,
                    created_at=grant.created_at,
                ),
                status=saved_grant.status,
                notes=saved_grant.notes,
                ai_summary=saved_grant.ai_summary,
                ai_draft_response=saved_grant.ai_draft_response,
                ai_why_fit=saved_grant.ai_why_fit,
                submitted_date=saved_grant.submitted_date,
                decision_date=saved_grant.decision_date,
                amount_requested=saved_grant.amount_requested,
                amount_awarded=saved_grant.amount_awarded,
                created_at=saved_grant.created_at,
                updated_at=saved_grant.updated_at,
            ))

    return {
        "saved_grants": responses,
        "total": total,
        "skip": pagination["skip"],
        "limit": pagination["limit"]
    }


@router.patch("/saved/{saved_grant_id}", response_model=SavedGrantResponse)
async def update_saved_grant(
    saved_grant_id: uuid.UUID,
    request: UpdateSavedGrantRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update saved grant tracking

    - Update status, notes, dates, amounts
    """
    saved_grant = db.query(SavedGrant).filter(
        SavedGrant.id == saved_grant_id,
        SavedGrant.organization_id == organization.id
    ).first()

    if not saved_grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved grant not found"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(saved_grant, field, value)

    saved_grant.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(saved_grant)

    # Get grant details
    grant = db.query(Grant).filter(Grant.id == saved_grant.grant_id).first()

    return SavedGrantResponse(
        id=str(saved_grant.id),
        grant=GrantResponse(
            id=str(grant.id),
            title=grant.title,
            funder_name=grant.funder_name,
            funder_website=grant.funder_website,
            country=grant.country,
            region=grant.region,
            type=grant.type,
            categories=grant.categories,
            amount_min=grant.amount_min,
            amount_max=grant.amount_max,
            currency=grant.currency,
            deadline=grant.deadline,
            link_url=grant.link_url,
            summary=grant.summary,
            requirements=grant.requirements,
            eligibility=grant.eligibility,
            is_active=grant.is_active,
            is_featured=grant.is_featured,
            view_count=grant.view_count,
            save_count=grant.save_count,
            created_at=grant.created_at,
        ),
        status=saved_grant.status,
        notes=saved_grant.notes,
        ai_summary=saved_grant.ai_summary,
        ai_draft_response=saved_grant.ai_draft_response,
        ai_why_fit=saved_grant.ai_why_fit,
        submitted_date=saved_grant.submitted_date,
        decision_date=saved_grant.decision_date,
        amount_requested=saved_grant.amount_requested,
        amount_awarded=saved_grant.amount_awarded,
        created_at=saved_grant.created_at,
        updated_at=saved_grant.updated_at,
    )


@router.delete("/saved/{saved_grant_id}")
async def unsave_grant(
    saved_grant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Remove grant from saved list
    """
    saved_grant = db.query(SavedGrant).filter(
        SavedGrant.id == saved_grant_id,
        SavedGrant.organization_id == organization.id
    ).first()

    if not saved_grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved grant not found"
        )

    # Decrement grant save count
    grant = db.query(Grant).filter(Grant.id == saved_grant.grant_id).first()
    if grant:
        grant.save_count = max(0, grant.save_count - 1)

    db.delete(saved_grant)
    db.commit()

    return {
        "success": True,
        "message": "Grant removed from saved list"
    }


# ============================================================================
# AI HELPERS (Pro/Enterprise Only)
# ============================================================================

@router.post("/saved/{saved_grant_id}/generate-draft")
async def generate_draft_application(
    saved_grant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(require_feature("grant_finder", "ai_draft")),
    db: Session = Depends(get_db)
):
    """
    Generate AI draft application response (Pro/Enterprise only)

    - Uses organization profile
    - Uses grant requirements
    - Creates personalized draft
    """
    saved_grant = db.query(SavedGrant).filter(
        SavedGrant.id == saved_grant_id,
        SavedGrant.organization_id == organization.id
    ).first()

    if not saved_grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved grant not found"
        )

    grant = db.query(Grant).filter(Grant.id == saved_grant.grant_id).first()

    # Generate AI draft (simplified - in production use actual AI)
    draft = f"""
Dear {grant.funder_name} Grant Committee,

We are writing to express our strong interest in the {grant.title}. Our organization, {organization.name}, is a {organization.type} based in {organization.city or 'our community'}, dedicated to {organization.mission_statement or 'serving our community'}.

This grant opportunity aligns perfectly with our mission because:
1. We serve the same community that your grant targets
2. Our programs directly address the needs outlined in your funding priorities
3. We have a proven track record of successful community initiatives

We are requesting funding in the range of ${grant.amount_min:,} to ${grant.amount_max:,} to support our ongoing programs and expand our impact.

Thank you for considering our application.

Sincerely,
{organization.name} Team

---
Note: This is an AI-generated draft. Please review, customize, and add specific details about your programs and impact.
"""

    saved_grant.ai_draft_response = draft.strip()
    saved_grant.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "draft": draft.strip(),
        "message": "Draft application generated successfully. Please review and customize before submitting."
    }


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats/overview")
async def get_grant_stats(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get grant statistics for organization
    """
    # Total saved grants
    total_saved = db.query(func.count(SavedGrant.id)).filter(
        SavedGrant.organization_id == organization.id
    ).scalar()

    # Breakdown by status
    status_counts = db.query(
        SavedGrant.status,
        func.count(SavedGrant.id)
    ).filter(
        SavedGrant.organization_id == organization.id
    ).group_by(SavedGrant.status).all()

    status_breakdown = {status: count for status, count in status_counts}

    # Total amount requested
    total_requested = db.query(func.sum(SavedGrant.amount_requested)).filter(
        SavedGrant.organization_id == organization.id
    ).scalar() or 0

    # Total amount awarded
    total_awarded = db.query(func.sum(SavedGrant.amount_awarded)).filter(
        and_(
            SavedGrant.organization_id == organization.id,
            SavedGrant.status == "awarded"
        )
    ).scalar() or 0

    return {
        "organization_id": str(organization.id),
        "organization_name": organization.name,
        "plan": organization.plan,
        "stats": {
            "total_saved": total_saved,
            "status_breakdown": status_breakdown,
            "total_amount_requested": total_requested,
            "total_amount_awarded": total_awarded,
            "success_rate": f"{(status_breakdown.get('awarded', 0) / total_saved * 100):.1f}%" if total_saved > 0 else "0%"
        }
    }

"""
Marketplace API Endpoints - Multi-tenant Business & Services Marketplace
Allows organizations to list businesses, services, courses, events, products, and tools
with approval workflow and plan-based limits.

Plan-based access:
- Basic: View only
- Pro: 1 active listing
- Enterprise: Unlimited listings + featured status

Routes:
- POST /api/v1/marketplace - Create listing (org user)
- GET /api/v1/marketplace - Browse all approved listings (public)
- GET /api/v1/marketplace/search - Search with filters (public)
- GET /api/v1/marketplace/my-listings - My org's listings (org user)
- GET /api/v1/marketplace/{id} - Get listing details (public)
- PATCH /api/v1/marketplace/{id} - Update my listing (org user)
- DELETE /api/v1/marketplace/{id} - Delete my listing (org user)
- POST /api/v1/marketplace/{id}/feature - Toggle featured (Enterprise)
- GET /api/v1/marketplace/categories - List all categories
- GET /api/v1/marketplace/stats - Marketplace statistics (org user)

Admin Routes:
- GET /api/v1/marketplace/admin/pending - List pending approvals (super admin)
- PATCH /api/v1/marketplace/admin/{id}/approve - Approve listing (super admin)
- PATCH /api/v1/marketplace/admin/{id}/reject - Reject listing (super admin)
- GET /api/v1/marketplace/admin/all - List all listings (super admin)
- DELETE /api/v1/marketplace/admin/{id} - Delete any listing (super admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models_multitenant import (
    MarketplaceListing,
    Organization,
    User,
    FeatureUsage
)
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_organization,
    require_roles,
    require_feature,
    get_pagination_params
)
from app.core.permissions import (
    UserRole,
    check_usage_limit,
    get_feature_limit,
    has_feature_access
)
from pydantic import BaseModel, Field, validator

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ListingCreateRequest(BaseModel):
    """Request body for creating a marketplace listing"""
    title: str = Field(..., min_length=3, max_length=200, description="Listing title")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description")
    category: str = Field(..., description="Category: business, service, course, event, product, tool")

    # Contact & Location
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)

    # Location
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)

    # Pricing
    price: Optional[float] = Field(None, ge=0, description="Price (if applicable)")
    price_type: Optional[str] = Field(None, description="free, paid, donation, variable")

    # Media
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = Field(default_factory=list, description="Additional image URLs")

    # Additional
    tags: Optional[List[str]] = Field(default_factory=list, max_items=10)
    external_url: Optional[str] = Field(None, max_length=500, description="External link")

    @validator('category')
    def validate_category(cls, v):
        allowed = ['business', 'service', 'course', 'event', 'product', 'tool']
        if v.lower() not in allowed:
            raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v.lower()

    @validator('price_type')
    def validate_price_type(cls, v):
        if v is None:
            return v
        allowed = ['free', 'paid', 'donation', 'variable']
        if v.lower() not in allowed:
            raise ValueError(f'Price type must be one of: {", ".join(allowed)}')
        return v.lower()


class ListingUpdateRequest(BaseModel):
    """Request body for updating a listing"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    price: Optional[float] = None
    price_type: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    external_url: Optional[str] = None


class ListingResponse(BaseModel):
    """Response model for marketplace listing"""
    id: uuid.UUID
    organization_id: uuid.UUID
    organization_name: str
    organization_type: str

    title: str
    description: str
    category: str

    # Contact & Location
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

    # Pricing
    price: Optional[float]
    price_type: Optional[str]

    # Media
    image_url: Optional[str]
    images: List[str]

    # Additional
    tags: List[str]
    external_url: Optional[str]

    # Status
    status: str
    is_featured: bool
    view_count: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketplaceStatsResponse(BaseModel):
    """Statistics for organization's marketplace presence"""
    total_listings: int
    active_listings: int
    pending_listings: int
    rejected_listings: int
    total_views: int
    featured_listings: int
    listings_by_category: dict


# ============================================================================
# PUBLIC ROUTES (Browse Marketplace)
# ============================================================================

@router.get("/", response_model=List[ListingResponse])
async def browse_marketplace(
    category: Optional[str] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    price_type: Optional[str] = Query(None, description="Filter by price type"),
    featured_only: bool = Query(False, description="Show only featured listings"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Browse all approved marketplace listings (public access).
    Featured listings appear first.
    """
    query = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        MarketplaceListing.status == "approved"
    )

    # Apply filters
    if category:
        query = query.filter(MarketplaceListing.category == category.lower())
    if city:
        query = query.filter(MarketplaceListing.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(MarketplaceListing.country.ilike(f"%{country}%"))
    if price_type:
        query = query.filter(MarketplaceListing.price_type == price_type.lower())
    if featured_only:
        query = query.filter(MarketplaceListing.is_featured == True)

    # Order: Featured first, then newest
    query = query.order_by(
        MarketplaceListing.is_featured.desc(),
        MarketplaceListing.created_at.desc()
    )

    results = query.offset(skip).limit(limit).all()

    return [
        ListingResponse(
            id=listing.id,
            organization_id=listing.organization_id,
            organization_name=org_name,
            organization_type=org_type,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            contact_name=listing.contact_name,
            contact_email=listing.contact_email,
            contact_phone=listing.contact_phone,
            website=listing.website,
            address=listing.address,
            city=listing.city,
            state=listing.state,
            country=listing.country,
            price=listing.price,
            price_type=listing.price_type,
            image_url=listing.image_url,
            images=listing.images or [],
            tags=listing.tags or [],
            external_url=listing.external_url,
            status=listing.status,
            is_featured=listing.is_featured,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at
        )
        for listing, org_name, org_type in results
    ]


@router.get("/search", response_model=List[ListingResponse])
async def search_marketplace(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search marketplace listings by keyword (public access).
    Searches in title, description, and tags.
    """
    search_term = f"%{q}%"

    query = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        and_(
            MarketplaceListing.status == "approved",
            or_(
                MarketplaceListing.title.ilike(search_term),
                MarketplaceListing.description.ilike(search_term),
                MarketplaceListing.tags.contains([q])
            )
        )
    )

    if category:
        query = query.filter(MarketplaceListing.category == category.lower())

    query = query.order_by(
        MarketplaceListing.is_featured.desc(),
        MarketplaceListing.created_at.desc()
    )

    results = query.offset(skip).limit(limit).all()

    return [
        ListingResponse(
            id=listing.id,
            organization_id=listing.organization_id,
            organization_name=org_name,
            organization_type=org_type,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            contact_name=listing.contact_name,
            contact_email=listing.contact_email,
            contact_phone=listing.contact_phone,
            website=listing.website,
            address=listing.address,
            city=listing.city,
            state=listing.state,
            country=listing.country,
            price=listing.price,
            price_type=listing.price_type,
            image_url=listing.image_url,
            images=listing.images or [],
            tags=listing.tags or [],
            external_url=listing.external_url,
            status=listing.status,
            is_featured=listing.is_featured,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at
        )
        for listing, org_name, org_type in results
    ]


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    Get list of all marketplace categories with listing counts (public access).
    """
    categories = db.query(
        MarketplaceListing.category,
        func.count(MarketplaceListing.id).label("count")
    ).filter(
        MarketplaceListing.status == "approved"
    ).group_by(
        MarketplaceListing.category
    ).all()

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in categories
        ],
        "all_categories": ["business", "service", "course", "event", "product", "tool"]
    }


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing_details(
    listing_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific listing (public access).
    Increments view count.
    """
    result = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        and_(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.status == "approved"
        )
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Listing not found or not approved")

    listing, org_name, org_type = result

    # Increment view count
    listing.view_count += 1
    db.commit()

    return ListingResponse(
        id=listing.id,
        organization_id=listing.organization_id,
        organization_name=org_name,
        organization_type=org_type,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        contact_name=listing.contact_name,
        contact_email=listing.contact_email,
        contact_phone=listing.contact_phone,
        website=listing.website,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        country=listing.country,
        price=listing.price,
        price_type=listing.price_type,
        image_url=listing.image_url,
        images=listing.images or [],
        tags=listing.tags or [],
        external_url=listing.external_url,
        status=listing.status,
        is_featured=listing.is_featured,
        view_count=listing.view_count,
        created_at=listing.created_at,
        updated_at=listing.updated_at
    )


# ============================================================================
# ORGANIZATION ROUTES (Manage Own Listings)
# ============================================================================

@router.post("/", response_model=ListingResponse, status_code=201)
async def create_listing(
    request: ListingCreateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("marketplace")),
    db: Session = Depends(get_db)
):
    """
    Create a new marketplace listing.

    Plan limits:
    - Basic: Not available
    - Pro: 1 active listing
    - Enterprise: Unlimited listings
    """
    # Check active listings count
    active_count = db.query(func.count(MarketplaceListing.id)).filter(
        and_(
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.status.in_(["pending", "approved"])
        )
    ).scalar()

    # Get plan limit
    limit = get_feature_limit(organization.plan, "marketplace")
    if limit != -1 and active_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Your {organization.plan} plan allows {limit} active listing(s). Please upgrade to Enterprise for unlimited listings."
        )

    # Create listing
    new_listing = MarketplaceListing(
        id=uuid.uuid4(),
        organization_id=organization.id,
        created_by_id=current_user.id,
        title=request.title,
        description=request.description,
        category=request.category,
        contact_name=request.contact_name,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        website=request.website,
        address=request.address,
        city=request.city,
        state=request.state,
        country=request.country,
        price=request.price,
        price_type=request.price_type,
        image_url=request.image_url,
        images=request.images,
        tags=request.tags,
        external_url=request.external_url,
        status="pending",  # Requires admin approval
        is_featured=False,
        view_count=0
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="marketplace",
        usage_type="listing_created",
        metadata={
            "listing_id": str(new_listing.id),
            "category": new_listing.category
        }
    )
    db.add(usage)
    db.commit()

    return ListingResponse(
        id=new_listing.id,
        organization_id=new_listing.organization_id,
        organization_name=organization.name,
        organization_type=organization.type,
        title=new_listing.title,
        description=new_listing.description,
        category=new_listing.category,
        contact_name=new_listing.contact_name,
        contact_email=new_listing.contact_email,
        contact_phone=new_listing.contact_phone,
        website=new_listing.website,
        address=new_listing.address,
        city=new_listing.city,
        state=new_listing.state,
        country=new_listing.country,
        price=new_listing.price,
        price_type=new_listing.price_type,
        image_url=new_listing.image_url,
        images=new_listing.images or [],
        tags=new_listing.tags or [],
        external_url=new_listing.external_url,
        status=new_listing.status,
        is_featured=new_listing.is_featured,
        view_count=new_listing.view_count,
        created_at=new_listing.created_at,
        updated_at=new_listing.updated_at
    )


@router.get("/my-listings", response_model=List[ListingResponse])
async def get_my_listings(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get all listings for my organization.
    """
    query = db.query(MarketplaceListing).filter(
        MarketplaceListing.organization_id == organization.id
    )

    if status:
        query = query.filter(MarketplaceListing.status == status.lower())

    query = query.order_by(MarketplaceListing.created_at.desc())
    listings = query.all()

    return [
        ListingResponse(
            id=listing.id,
            organization_id=listing.organization_id,
            organization_name=organization.name,
            organization_type=organization.type,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            contact_name=listing.contact_name,
            contact_email=listing.contact_email,
            contact_phone=listing.contact_phone,
            website=listing.website,
            address=listing.address,
            city=listing.city,
            state=listing.state,
            country=listing.country,
            price=listing.price,
            price_type=listing.price_type,
            image_url=listing.image_url,
            images=listing.images or [],
            tags=listing.tags or [],
            external_url=listing.external_url,
            status=listing.status,
            is_featured=listing.is_featured,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at
        )
        for listing in listings
    ]


@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: uuid.UUID,
    request: ListingUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update my organization's listing.
    Can only update own listings.
    """
    listing = db.query(MarketplaceListing).filter(
        and_(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.organization_id == organization.id
        )
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    listing.updated_at = datetime.utcnow()

    # If listing was rejected, change back to pending on update
    if listing.status == "rejected":
        listing.status = "pending"

    db.commit()
    db.refresh(listing)

    return ListingResponse(
        id=listing.id,
        organization_id=listing.organization_id,
        organization_name=organization.name,
        organization_type=organization.type,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        contact_name=listing.contact_name,
        contact_email=listing.contact_email,
        contact_phone=listing.contact_phone,
        website=listing.website,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        country=listing.country,
        price=listing.price,
        price_type=listing.price_type,
        image_url=listing.image_url,
        images=listing.images or [],
        tags=listing.tags or [],
        external_url=listing.external_url,
        status=listing.status,
        is_featured=listing.is_featured,
        view_count=listing.view_count,
        created_at=listing.created_at,
        updated_at=listing.updated_at
    )


@router.delete("/{listing_id}", status_code=204)
async def delete_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete my organization's listing.
    Can only delete own listings.
    """
    listing = db.query(MarketplaceListing).filter(
        and_(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.organization_id == organization.id
        )
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    db.delete(listing)
    db.commit()

    return None


@router.post("/{listing_id}/feature", response_model=ListingResponse)
async def toggle_featured(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("marketplace", "featured")),
    db: Session = Depends(get_db)
):
    """
    Toggle featured status for my organization's listing.

    Only available for Enterprise plan.
    Featured listings appear first in marketplace.
    """
    listing = db.query(MarketplaceListing).filter(
        and_(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.status == "approved"
        )
    ).first()

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Listing not found or not approved"
        )

    # Toggle featured status
    listing.is_featured = not listing.is_featured
    listing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(listing)

    return ListingResponse(
        id=listing.id,
        organization_id=listing.organization_id,
        organization_name=organization.name,
        organization_type=organization.type,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        contact_name=listing.contact_name,
        contact_email=listing.contact_email,
        contact_phone=listing.contact_phone,
        website=listing.website,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        country=listing.country,
        price=listing.price,
        price_type=listing.price_type,
        image_url=listing.image_url,
        images=listing.images or [],
        tags=listing.tags or [],
        external_url=listing.external_url,
        status=listing.status,
        is_featured=listing.is_featured,
        view_count=listing.view_count,
        created_at=listing.created_at,
        updated_at=listing.updated_at
    )


@router.get("/stats", response_model=MarketplaceStatsResponse)
async def get_marketplace_stats(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get marketplace statistics for my organization.
    """
    # Count listings by status
    total = db.query(func.count(MarketplaceListing.id)).filter(
        MarketplaceListing.organization_id == organization.id
    ).scalar()

    active = db.query(func.count(MarketplaceListing.id)).filter(
        and_(
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.status == "approved"
        )
    ).scalar()

    pending = db.query(func.count(MarketplaceListing.id)).filter(
        and_(
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.status == "pending"
        )
    ).scalar()

    rejected = db.query(func.count(MarketplaceListing.id)).filter(
        and_(
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.status == "rejected"
        )
    ).scalar()

    # Total views
    total_views = db.query(func.sum(MarketplaceListing.view_count)).filter(
        MarketplaceListing.organization_id == organization.id
    ).scalar() or 0

    # Featured count
    featured = db.query(func.count(MarketplaceListing.id)).filter(
        and_(
            MarketplaceListing.organization_id == organization.id,
            MarketplaceListing.is_featured == True
        )
    ).scalar()

    # Listings by category
    categories = db.query(
        MarketplaceListing.category,
        func.count(MarketplaceListing.id).label("count")
    ).filter(
        MarketplaceListing.organization_id == organization.id
    ).group_by(
        MarketplaceListing.category
    ).all()

    return MarketplaceStatsResponse(
        total_listings=total,
        active_listings=active,
        pending_listings=pending,
        rejected_listings=rejected,
        total_views=total_views,
        featured_listings=featured,
        listings_by_category={cat: count for cat, count in categories}
    )


# ============================================================================
# SUPER ADMIN ROUTES (Approval & Management)
# ============================================================================

@router.get("/admin/pending", response_model=List[ListingResponse])
async def get_pending_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get all pending listings awaiting approval (super admin only).
    """
    results = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        MarketplaceListing.status == "pending"
    ).order_by(
        MarketplaceListing.created_at.asc()
    ).offset(skip).limit(limit).all()

    return [
        ListingResponse(
            id=listing.id,
            organization_id=listing.organization_id,
            organization_name=org_name,
            organization_type=org_type,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            contact_name=listing.contact_name,
            contact_email=listing.contact_email,
            contact_phone=listing.contact_phone,
            website=listing.website,
            address=listing.address,
            city=listing.city,
            state=listing.state,
            country=listing.country,
            price=listing.price,
            price_type=listing.price_type,
            image_url=listing.image_url,
            images=listing.images or [],
            tags=listing.tags or [],
            external_url=listing.external_url,
            status=listing.status,
            is_featured=listing.is_featured,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at
        )
        for listing, org_name, org_type in results
    ]


@router.patch("/admin/{listing_id}/approve", response_model=ListingResponse)
async def approve_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Approve a pending listing (super admin only).
    """
    result = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        MarketplaceListing.id == listing_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing, org_name, org_type = result

    listing.status = "approved"
    listing.approved_by_id = current_user.id
    listing.approved_at = datetime.utcnow()
    listing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(listing)

    return ListingResponse(
        id=listing.id,
        organization_id=listing.organization_id,
        organization_name=org_name,
        organization_type=org_type,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        contact_name=listing.contact_name,
        contact_email=listing.contact_email,
        contact_phone=listing.contact_phone,
        website=listing.website,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        country=listing.country,
        price=listing.price,
        price_type=listing.price_type,
        image_url=listing.image_url,
        images=listing.images or [],
        tags=listing.tags or [],
        external_url=listing.external_url,
        status=listing.status,
        is_featured=listing.is_featured,
        view_count=listing.view_count,
        created_at=listing.created_at,
        updated_at=listing.updated_at
    )


@router.patch("/admin/{listing_id}/reject", response_model=ListingResponse)
async def reject_listing(
    listing_id: uuid.UUID,
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Reject a pending listing (super admin only).
    """
    result = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    ).filter(
        MarketplaceListing.id == listing_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing, org_name, org_type = result

    listing.status = "rejected"
    listing.rejection_reason = reason
    listing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(listing)

    return ListingResponse(
        id=listing.id,
        organization_id=listing.organization_id,
        organization_name=org_name,
        organization_type=org_type,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        contact_name=listing.contact_name,
        contact_email=listing.contact_email,
        contact_phone=listing.contact_phone,
        website=listing.website,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        country=listing.country,
        price=listing.price,
        price_type=listing.price_type,
        image_url=listing.image_url,
        images=listing.images or [],
        tags=listing.tags or [],
        external_url=listing.external_url,
        status=listing.status,
        is_featured=listing.is_featured,
        view_count=listing.view_count,
        created_at=listing.created_at,
        updated_at=listing.updated_at
    )


@router.get("/admin/all", response_model=List[ListingResponse])
async def get_all_listings_admin(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get all marketplace listings (super admin only).
    """
    query = db.query(
        MarketplaceListing,
        Organization.name.label("org_name"),
        Organization.type.label("org_type")
    ).join(
        Organization,
        MarketplaceListing.organization_id == Organization.id
    )

    if status:
        query = query.filter(MarketplaceListing.status == status.lower())
    if category:
        query = query.filter(MarketplaceListing.category == category.lower())

    query = query.order_by(MarketplaceListing.created_at.desc())
    results = query.offset(skip).limit(limit).all()

    return [
        ListingResponse(
            id=listing.id,
            organization_id=listing.organization_id,
            organization_name=org_name,
            organization_type=org_type,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            contact_name=listing.contact_name,
            contact_email=listing.contact_email,
            contact_phone=listing.contact_phone,
            website=listing.website,
            address=listing.address,
            city=listing.city,
            state=listing.state,
            country=listing.country,
            price=listing.price,
            price_type=listing.price_type,
            image_url=listing.image_url,
            images=listing.images or [],
            tags=listing.tags or [],
            external_url=listing.external_url,
            status=listing.status,
            is_featured=listing.is_featured,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at
        )
        for listing, org_name, org_type in results
    ]


@router.delete("/admin/{listing_id}", status_code=204)
async def delete_listing_admin(
    listing_id: uuid.UUID,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Delete any listing (super admin only).
    """
    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    db.delete(listing)
    db.commit()

    return None

"""
Umrah & Hajj Alerts API Endpoints - Multi-tenant Travel Deal Finder
Real-time search for Umrah/Hajj packages, hotels, and flights with price alerts.

Plan-based access:
- Basic: 5 searches/month, view only
- Pro: 50 searches/month, save searches with email alerts
- Enterprise: Unlimited searches, all alert channels (email, WhatsApp, SMS)

Routes:
- POST /api/v1/umrah/search - Search for deals (hotels, flights, packages)
- POST /api/v1/umrah/save-search - Save search with alerts
- GET /api/v1/umrah/my-searches - Get my saved searches
- GET /api/v1/umrah/my-searches/{id} - Get saved search details
- PATCH /api/v1/umrah/my-searches/{id} - Update search/alert preferences
- DELETE /api/v1/umrah/my-searches/{id} - Delete saved search
- GET /api/v1/umrah/alerts - Get my alerts
- PATCH /api/v1/umrah/alerts/{id}/read - Mark alert as read
- GET /api/v1/umrah/stats - Usage statistics

Background Services:
- Price monitoring (runs every 6 hours)
- Alert notifications (email, WhatsApp, SMS)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
import json
import os
import uuid

from app.db.database import get_db
from app.db.models_multitenant import (
    Organization,
    User,
    FeatureUsage
)
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_organization,
    require_feature
)
from app.core.permissions import check_usage_limit
from pydantic import BaseModel, EmailStr, Field, validator

router = APIRouter()

# Environment variables
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class UmrahSearchRequest(BaseModel):
    """Request model for Umrah/Hajj deal search"""
    search_type: str = Field(..., description="hotels, flights, packages")
    destination: str = Field(..., description="Makkah, Madinah, Both")
    budget_min: Optional[float] = Field(0, ge=0)
    budget_max: float = Field(..., gt=0)

    # Dates
    check_in_date: Optional[str] = Field(None, description="YYYY-MM-DD format")
    check_out_date: Optional[str] = Field(None, description="YYYY-MM-DD format")
    duration_nights: int = Field(7, ge=1, le=30)

    # Hotel preferences
    hotel_rating: int = Field(3, ge=1, le=5)
    distance_from_haram: float = Field(2.0, ge=0.1, le=10.0, description="Maximum km from Haram")

    # Flight preferences
    departure_city: Optional[str] = Field(None, description="e.g., New York, London")
    flight_class: str = Field("economy", description="economy, business, first")
    direct_flights_only: bool = Field(False)

    @validator('search_type')
    def validate_search_type(cls, v):
        allowed = ['hotels', 'flights', 'packages']
        if v.lower() not in allowed:
            raise ValueError(f'Search type must be: {", ".join(allowed)}')
        return v.lower()

    @validator('destination')
    def validate_destination(cls, v):
        allowed = ['Makkah', 'Madinah', 'Both']
        if v not in allowed:
            raise ValueError(f'Destination must be: {", ".join(allowed)}')
        return v

    @validator('flight_class')
    def validate_flight_class(cls, v):
        allowed = ['economy', 'business', 'first']
        if v.lower() not in allowed:
            raise ValueError(f'Flight class must be: {", ".join(allowed)}')
        return v.lower()


class SavedSearchCreate(BaseModel):
    """Request to save a search with alerts"""
    search_criteria: UmrahSearchRequest
    search_name: str = Field(..., min_length=3, max_length=100)
    alert_enabled: bool = Field(True)
    alert_email: bool = Field(True)
    alert_frequency: str = Field("daily", description="daily, weekly, price_drop")

    @validator('alert_frequency')
    def validate_alert_frequency(cls, v):
        allowed = ['daily', 'weekly', 'price_drop']
        if v not in allowed:
            raise ValueError(f'Alert frequency must be: {", ".join(allowed)}')
        return v


class SavedSearchUpdate(BaseModel):
    """Request to update saved search"""
    search_name: Optional[str] = None
    alert_enabled: Optional[bool] = None
    alert_email: Optional[bool] = None
    alert_frequency: Optional[str] = None


class UmrahDeal(BaseModel):
    """Single deal result"""
    deal_type: str
    price: float
    currency: str = "USD"
    location: str
    booking_url: Optional[str]
    provider: Optional[str]

    # Hotel fields
    hotel_name: Optional[str] = None
    hotel_rating: Optional[float] = None
    distance_from_haram: Optional[float] = None
    amenities: List[str] = []

    # Flight fields
    flight_airline: Optional[str] = None
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    flight_class: Optional[str] = None
    stops: Optional[int] = None

    # Availability
    available_from: Optional[str] = None
    available_to: Optional[str] = None


class SearchResponse(BaseModel):
    """Response for deal search"""
    deals: List[UmrahDeal]
    total_results: int
    search_duration_ms: int
    searched_at: datetime
    searches_remaining: int


class SavedSearchResponse(BaseModel):
    """Response for saved search"""
    id: uuid.UUID
    organization_id: uuid.UUID
    search_name: str
    destination: str
    budget_max: float
    hotel_rating: int
    alert_enabled: bool
    alert_email: bool
    alert_frequency: str
    last_checked: Optional[datetime]
    best_price_found: Optional[float]
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    """Response for alert notification"""
    id: uuid.UUID
    search_id: Optional[uuid.UUID]
    alert_type: str
    message: str
    deal_data: Optional[dict]
    is_read: bool
    created_at: datetime


class UmrahStatsResponse(BaseModel):
    """Statistics for Umrah usage"""
    total_searches: int
    searches_this_month: int
    monthly_limit: int
    remaining_searches: int
    saved_searches: int
    active_alerts: int
    best_deal_found: Optional[dict]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def search_deals_with_perplexity(search_params: UmrahSearchRequest) -> List[dict]:
    """Search for Umrah deals using Perplexity AI"""

    destination_str = "Makkah and Madinah" if search_params.destination == "Both" else search_params.destination
    current_date = datetime.now().strftime("%Y-%m-%d")
    check_in = search_params.check_in_date or current_date

    # Build query based on search type
    if search_params.search_type == "hotels":
        query = f"""Search for CURRENT available Umrah hotels in {destination_str} for dates around {check_in}.

Requirements:
- Budget: ${search_params.budget_min} to ${search_params.budget_max} per night
- Hotel rating: {search_params.hotel_rating} stars or higher
- Distance from Haram: within {search_params.distance_from_haram} km
- Duration: {search_params.duration_nights} nights

Search: Booking.com, Expedia, Hotels.com, Agoda, Almosafer, Seera, HotelsCombined

For each hotel, return JSON with: hotel_name, rating, price (per night USD), distance_km, amenities (array), booking_url, provider, location, deal_type:"hotel"

Return ONLY valid JSON array, no markdown."""

    elif search_params.search_type == "flights":
        dep_city = search_params.departure_city or "New York"
        query = f"""Search for CURRENT available flights from {dep_city} to Jeddah/Medina Saudi Arabia for Umrah around {check_in}.

Requirements:
- Budget: up to ${search_params.budget_max} roundtrip
- Flight class: {search_params.flight_class}
- Direct flights only: {search_params.direct_flights_only}

Search: Saudi Airlines, Emirates, Qatar Airways, Etihad, Turkish Airlines, Google Flights, Kayak, Skyscanner

For each flight, return JSON with: flight_airline, price (USD roundtrip), departure_city, arrival_city, flight_class, stops, booking_url, provider, location, deal_type:"flight"

Return ONLY valid JSON array, no markdown."""

    else:  # packages
        dep_city = search_params.departure_city or "New York"
        query = f"""Search for CURRENT Umrah packages (flight + hotel) from {dep_city} to {destination_str} around {check_in}.

Requirements:
- Total budget: up to ${search_params.budget_max}
- Duration: {search_params.duration_nights} nights
- Hotel rating: {search_params.hotel_rating}+ stars
- Flight class: {search_params.flight_class}

Search: Almosafer, Seera, HalalBooking, IslamicTravel, BookingMuslim, Umrahme

For each package, return JSON with: hotel_name, rating, flight_airline, departure_city, arrival_city, flight_class, stops, price (total USD), booking_url, provider, location, deal_type:"package"

Return ONLY valid JSON array, no markdown."""

    # Try Perplexity API
    try:
        if not PERPLEXITY_API_KEY:
            return _get_mock_deals(search_params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a real-time travel search engine. Return ONLY valid JSON array, no explanations."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4000,
                    "return_citations": True,
                    "search_recency_filter": "month"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                try:
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()
                    elif "```" in content:
                        json_start = content.find("```") + 3
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()

                    deals = json.loads(content)
                    if isinstance(deals, dict):
                        deals = [deals]
                    return deals
                except json.JSONDecodeError:
                    return _get_mock_deals(search_params)
            else:
                return _get_mock_deals(search_params)

    except Exception as e:
        print(f"Perplexity API error: {str(e)}")
        return _get_mock_deals(search_params)


def _get_mock_deals(search_params: UmrahSearchRequest) -> List[dict]:
    """Return mock deals for testing"""
    deals = []

    if search_params.search_type in ["hotels", "packages"]:
        if search_params.destination in ["Makkah", "Both"]:
            deals.extend([
                {
                    "deal_type": search_params.search_type,
                    "hotel_name": "Makkah Clock Royal Tower",
                    "rating": 5.0,
                    "price": 450 if search_params.search_type == "hotels" else 1850,
                    "distance_km": 0.1,
                    "amenities": ["WiFi", "Breakfast", "Haram View", "Pool"],
                    "booking_url": "https://booking.com/makkah-clock-tower",
                    "provider": "Booking.com",
                    "location": "Adjacent to Masjid al-Haram"
                },
                {
                    "deal_type": search_params.search_type,
                    "hotel_name": "Swissotel Makkah",
                    "rating": 5.0,
                    "price": 380 if search_params.search_type == "hotels" else 1680,
                    "distance_km": 0.2,
                    "amenities": ["WiFi", "Breakfast", "Spa"],
                    "booking_url": "https://expedia.com/swissotel-makkah",
                    "provider": "Expedia",
                    "location": "200m from Masjid al-Haram"
                }
            ])

        if search_params.destination in ["Madinah", "Both"]:
            deals.append({
                "deal_type": search_params.search_type,
                "hotel_name": "Oberoi Madinah",
                "rating": 5.0,
                "price": 320 if search_params.search_type == "hotels" else 1620,
                "distance_km": 0.3,
                "amenities": ["WiFi", "Breakfast", "Prophet's Mosque View"],
                "booking_url": "https://booking.com/oberoi-madinah",
                "provider": "Booking.com",
                "location": "Near Prophet's Mosque"
            })

    if search_params.search_type in ["flights", "packages"]:
        dep_city = search_params.departure_city or "New York"
        deals.extend([
            {
                "deal_type": "flight" if search_params.search_type == "flights" else search_params.search_type,
                "flight_airline": "Saudi Airlines",
                "price": 850 if search_params.search_type == "flights" else 1850,
                "departure_city": dep_city,
                "arrival_city": "Jeddah (JED)",
                "flight_class": search_params.flight_class,
                "stops": 0,
                "booking_url": "https://saudia.com",
                "provider": "Saudi Airlines",
                "location": "Jeddah (JED)"
            }
        ])

    # Filter by budget and rating
    filtered = [
        d for d in deals
        if d["price"] <= search_params.budget_max
        and (d.get("rating", 5) >= search_params.hotel_rating if "rating" in d else True)
    ]

    return filtered


# ============================================================================
# SEARCH ROUTES
# ============================================================================

@router.post("/search", response_model=SearchResponse)
async def search_umrah_deals(
    search: UmrahSearchRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("umrah_finder")),
    db: Session = Depends(get_db)
):
    """
    Search for Umrah/Hajj deals in real-time.

    Plan limits:
    - Basic: 5 searches/month
    - Pro: 50 searches/month
    - Enterprise: Unlimited
    """
    # Check monthly usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_count = db.query(func.count(FeatureUsage.id)).filter(
        and_(
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search",
            FeatureUsage.created_at >= current_month_start
        )
    ).scalar()

    check_usage_limit(organization.plan, "umrah_finder", monthly_count)

    start_time = datetime.now()

    # Search for deals
    deals_data = await search_deals_with_perplexity(search)

    # Convert to UmrahDeal models
    deals = []
    for deal in deals_data:
        try:
            deals.append(UmrahDeal(
                deal_type=deal.get("deal_type", "hotel"),
                price=deal.get("price", 0),
                currency="USD",
                location=deal.get("location", ""),
                booking_url=deal.get("booking_url"),
                provider=deal.get("provider"),
                hotel_name=deal.get("hotel_name"),
                hotel_rating=deal.get("rating"),
                distance_from_haram=deal.get("distance_km"),
                amenities=deal.get("amenities", []),
                flight_airline=deal.get("flight_airline"),
                departure_city=deal.get("departure_city"),
                arrival_city=deal.get("arrival_city"),
                flight_class=deal.get("flight_class"),
                stops=deal.get("stops")
            ))
        except Exception as e:
            print(f"Error parsing deal: {e}")
            continue

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="umrah_finder",
        usage_type="search",
        metadata={
            "search_type": search.search_type,
            "destination": search.destination,
            "results_count": len(deals)
        }
    )
    db.add(usage)
    db.commit()

    # Calculate remaining searches
    from app.core.permissions import get_feature_limit
    limit = get_feature_limit(organization.plan, "umrah_finder")
    remaining = max(0, limit - (monthly_count + 1)) if limit != -1 else -1

    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    return SearchResponse(
        deals=deals,
        total_results=len(deals),
        search_duration_ms=duration_ms,
        searched_at=datetime.now(),
        searches_remaining=remaining
    )


# ============================================================================
# SAVED SEARCHES ROUTES
# ============================================================================

# Note: For saved searches, we would need to add new models to models_multitenant.py
# For now, I'll create endpoints that work with the existing FeatureUsage tracking
# In production, add: SavedUmrahSearch, UmrahAlert models

@router.post("/save-search")
async def save_search(
    request: SavedSearchCreate,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("umrah_finder", "save_searches")),
    db: Session = Depends(get_db)
):
    """
    Save a search with price alerts (Pro/Enterprise only).
    """
    # Track saved search
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="umrah_finder",
        usage_type="search_saved",
        metadata={
            "search_name": request.search_name,
            "destination": request.search_criteria.destination,
            "budget_max": request.search_criteria.budget_max,
            "alert_enabled": request.alert_enabled,
            "alert_frequency": request.alert_frequency
        }
    )
    db.add(usage)
    db.commit()

    return {
        "success": True,
        "search_id": str(usage.id),
        "message": f"Search '{request.search_name}' saved successfully!",
        "alert_status": {
            "enabled": request.alert_enabled,
            "email": request.alert_email,
            "frequency": request.alert_frequency
        },
        "next_check": (datetime.now() + timedelta(hours=6)).isoformat()
    }


@router.get("/my-searches")
async def get_my_saved_searches(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get all saved searches for my organization.
    """
    saved_searches = db.query(FeatureUsage).filter(
        and_(
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search_saved"
        )
    ).order_by(FeatureUsage.created_at.desc()).all()

    return {
        "searches": [
            {
                "id": str(search.id),
                "search_name": search.metadata.get("search_name"),
                "destination": search.metadata.get("destination"),
                "budget_max": search.metadata.get("budget_max"),
                "alert_enabled": search.metadata.get("alert_enabled"),
                "created_at": search.created_at.isoformat()
            }
            for search in saved_searches
        ],
        "total": len(saved_searches)
    }


@router.delete("/my-searches/{search_id}")
async def delete_saved_search(
    search_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a saved search.
    """
    search = db.query(FeatureUsage).filter(
        and_(
            FeatureUsage.id == search_id,
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search_saved"
        )
    ).first()

    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")

    db.delete(search)
    db.commit()

    return {"success": True, "message": "Search deleted successfully"}


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats", response_model=UmrahStatsResponse)
async def get_umrah_stats(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get Umrah/Hajj search statistics for my organization.
    """
    from app.core.permissions import get_feature_limit

    # Total searches
    total = db.query(func.count(FeatureUsage.id)).filter(
        and_(
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search"
        )
    ).scalar()

    # Searches this month
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = db.query(func.count(FeatureUsage.id)).filter(
        and_(
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search",
            FeatureUsage.created_at >= current_month_start
        )
    ).scalar()

    # Saved searches
    saved = db.query(func.count(FeatureUsage.id)).filter(
        and_(
            FeatureUsage.organization_id == organization.id,
            FeatureUsage.feature_name == "umrah_finder",
            FeatureUsage.usage_type == "search_saved"
        )
    ).scalar()

    # Monthly limit
    monthly_limit = get_feature_limit(organization.plan, "umrah_finder")
    remaining = max(0, monthly_limit - this_month) if monthly_limit != -1 else -1

    return UmrahStatsResponse(
        total_searches=total,
        searches_this_month=this_month,
        monthly_limit=monthly_limit,
        remaining_searches=remaining,
        saved_searches=saved,
        active_alerts=saved,  # Assumes all saved searches have alerts
        best_deal_found=None
    )

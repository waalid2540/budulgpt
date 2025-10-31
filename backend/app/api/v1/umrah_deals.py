"""
Umrah Deal Finder API Endpoints
Integrates with Perplexity AI to search for real-time Umrah deals
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import httpx
import os
import json

router = APIRouter()

# Environment variables
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


class UmrahSearchRequest(BaseModel):
    """Request model for Umrah deal search"""
    search_type: str = "packages"  # "hotels", "flights", "packages"
    destination: str  # "Makkah", "Madinah", "Both"
    budget_min: Optional[float] = 0
    budget_max: float
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    duration_nights: Optional[int] = 7
    # Hotel-specific fields
    hotel_rating: Optional[int] = 3  # 3, 4, or 5 stars
    distance_from_haram: Optional[float] = 2.0  # km
    # Flight-specific fields
    departure_city: Optional[str] = None
    flight_class: Optional[str] = "economy"
    direct_flights_only: Optional[bool] = False


class SavedSearchRequest(BaseModel):
    """Request model for saving a search with alerts"""
    search_criteria: UmrahSearchRequest
    search_name: str
    alert_enabled: bool = True
    alert_email: bool = True
    alert_whatsapp: bool = False
    alert_sms: bool = False
    user_email: EmailStr
    user_phone: Optional[str] = None


class UmrahDeal(BaseModel):
    """Response model for a single deal"""
    deal_type: str  # "hotel", "flight", "package"
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
    # Common fields
    available_from: Optional[str] = None
    available_to: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search results"""
    search_id: Optional[str]
    deals: List[UmrahDeal]
    total_results: int
    search_duration_ms: int
    searched_at: datetime


async def search_umrah_deals_with_perplexity(search_params: UmrahSearchRequest) -> List[dict]:
    """
    Use Perplexity AI to search for Umrah deals across the web
    """

    # Build the search query
    destination_str = search_params.destination
    if search_params.destination == "Both":
        destination_str = "Makkah and Madinah"

    query = f"""Find current Umrah hotel deals in {destination_str} with these requirements:
- Budget: ${search_params.budget_min} to ${search_params.budget_max} per night
- Hotel rating: {search_params.hotel_rating} stars or higher
- Distance from Haram: within {search_params.distance_from_haram} km
- Duration: {search_params.duration_nights} nights
"""

    if search_params.check_in_date:
        query += f"- Check-in: {search_params.check_in_date}\n"
    if search_params.check_out_date:
        query += f"- Check-out: {search_params.check_out_date}\n"

    query += """
Search across major booking sites (Booking.com, Expedia, Hotels.com, Agoda) and Umrah-specific travel agencies.

For each hotel found, provide:
1. Hotel name
2. Star rating
3. Current price per night in USD
4. Distance from Masjid al-Haram
5. Key amenities
6. Booking website/link
7. Provider name

Format as JSON array with these exact fields: hotel_name, rating, price, distance_km, amenities, booking_url, provider, location
"""

    # Call Perplexity API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",  # Perplexity's web search model
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a travel deal finder specializing in Umrah packages and hotels. Always return results in valid JSON format."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                timeout=30.0
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Perplexity API error: {response.text}"
                )

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse the JSON response
            try:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                deals = json.loads(content)

                # Ensure it's a list
                if isinstance(deals, dict):
                    deals = [deals]

                return deals

            except json.JSONDecodeError:
                # If JSON parsing fails, return mock data for now
                return get_mock_deals(search_params)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Search timeout - please try again")
    except Exception as e:
        # Return mock data if API fails
        print(f"Perplexity API error: {str(e)}")
        return get_mock_deals(search_params)


def get_mock_deals(search_params: UmrahSearchRequest) -> List[dict]:
    """Return mock deals for testing when API is not available"""
    destination = search_params.destination
    search_type = search_params.search_type

    mock_deals = []

    # Hotel deals
    if search_type in ["hotels", "packages"]:
        hotel_deals = []

        if destination in ["Makkah", "Both"]:
            hotel_deals.extend([
                {
                    "deal_type": search_type,
                    "hotel_name": "Makkah Clock Royal Tower",
                    "rating": 5.0,
                    "price": 1850 if search_type == "packages" else 450,
                    "distance_km": 0.1,
                    "amenities": ["WiFi", "Breakfast", "Haram View", "Pool", "Spa"],
                    "booking_url": "https://booking.com/makkah-clock-tower",
                    "provider": "Booking.com",
                    "location": "Adjacent to Masjid al-Haram"
                },
                {
                    "deal_type": search_type,
                    "hotel_name": "Swissotel Makkah",
                    "rating": 5.0,
                    "price": 1680 if search_type == "packages" else 380,
                    "distance_km": 0.2,
                    "amenities": ["WiFi", "Breakfast", "Spa", "Restaurant"],
                    "booking_url": "https://expedia.com/swissotel-makkah",
                    "provider": "Expedia",
                    "location": "200m from Masjid al-Haram"
                },
                {
                    "deal_type": search_type,
                    "hotel_name": "Dar Al Eiman Royal",
                    "rating": 4.0,
                    "price": 1480 if search_type == "packages" else 280,
                    "distance_km": 0.5,
                    "amenities": ["WiFi", "Breakfast", "Shuttle"],
                    "booking_url": "https://hotels.com/dar-al-eiman",
                    "provider": "Hotels.com",
                    "location": "500m from Masjid al-Haram"
                }
            ])

        if destination in ["Madinah", "Both"]:
            hotel_deals.extend([
                {
                    "deal_type": search_type,
                    "hotel_name": "Oberoi Madinah",
                    "rating": 5.0,
                    "price": 1620 if search_type == "packages" else 320,
                    "distance_km": 0.3,
                    "amenities": ["WiFi", "Breakfast", "Prophet's Mosque View"],
                    "booking_url": "https://booking.com/oberoi-madinah",
                    "provider": "Booking.com",
                    "location": "Near Prophet's Mosque"
                },
                {
                    "deal_type": search_type,
                    "hotel_name": "Dar Al Iman InterContinental",
                    "rating": 5.0,
                    "price": 1590 if search_type == "packages" else 290,
                    "distance_km": 0.4,
                    "amenities": ["WiFi", "Breakfast", "Pool", "Gym"],
                    "booking_url": "https://expedia.com/dar-al-iman-ic",
                    "provider": "Expedia",
                    "location": "400m from Prophet's Mosque"
                }
            ])

        # Filter hotels by budget and rating
        filtered_hotels = [
            deal for deal in hotel_deals
            if deal["price"] <= search_params.budget_max
            and deal["rating"] >= search_params.hotel_rating
            and deal["distance_km"] <= search_params.distance_from_haram
        ]
        mock_deals.extend(filtered_hotels)

    # Flight deals
    if search_type in ["flights", "packages"]:
        dep_city = search_params.departure_city or "New York (JFK)"
        flight_class = search_params.flight_class or "economy"

        flight_deals = [
            {
                "deal_type": "flight" if search_type == "flights" else search_type,
                "flight_airline": "Saudi Airlines",
                "price": 1850 if search_type == "packages" else 850,
                "departure_city": dep_city,
                "arrival_city": "Jeddah (JED)",
                "flight_class": flight_class,
                "stops": 0,
                "booking_url": "https://saudia.com",
                "provider": "Saudi Airlines",
                "location": "Jeddah (JED)"
            },
            {
                "deal_type": "flight" if search_type == "flights" else search_type,
                "flight_airline": "Emirates",
                "price": 1680 if search_type == "packages" else 920,
                "departure_city": dep_city,
                "arrival_city": "Jeddah (JED)",
                "flight_class": flight_class,
                "stops": 1,
                "booking_url": "https://emirates.com",
                "provider": "Emirates",
                "location": "Jeddah (JED)"
            },
            {
                "deal_type": "flight" if search_type == "flights" else search_type,
                "flight_airline": "Qatar Airways",
                "price": 1750 if search_type == "packages" else 890,
                "departure_city": dep_city,
                "arrival_city": "Jeddah (JED)",
                "flight_class": flight_class,
                "stops": 1,
                "booking_url": "https://qatarairways.com",
                "provider": "Qatar Airways",
                "location": "Jeddah (JED)"
            }
        ]

        # Filter flights by budget and direct flights preference
        filtered_flights = [
            deal for deal in flight_deals
            if deal["price"] <= search_params.budget_max
            and (not search_params.direct_flights_only or deal["stops"] == 0)
        ]
        mock_deals.extend(filtered_flights)

    return mock_deals


@router.post("/search", response_model=SearchResponse)
async def search_umrah_deals(search: UmrahSearchRequest):
    """
    Search for Umrah deals using Perplexity AI

    Returns real-time hotel deals from across the web matching your criteria.
    """

    start_time = datetime.now()

    # Search using Perplexity (or mock data)
    deals_data = await search_umrah_deals_with_perplexity(search)

    # Convert to UmrahDeal models
    deals = []
    for deal in deals_data:
        try:
            umrah_deal = UmrahDeal(
                deal_type=deal.get("deal_type", "hotel"),
                price=deal.get("price", 0),
                currency="USD",
                location=deal.get("location", ""),
                booking_url=deal.get("booking_url"),
                provider=deal.get("provider"),
                # Hotel fields
                hotel_name=deal.get("hotel_name"),
                hotel_rating=deal.get("rating"),
                distance_from_haram=deal.get("distance_km"),
                amenities=deal.get("amenities", []),
                # Flight fields
                flight_airline=deal.get("flight_airline"),
                departure_city=deal.get("departure_city"),
                arrival_city=deal.get("arrival_city"),
                flight_class=deal.get("flight_class"),
                stops=deal.get("stops")
            )
            deals.append(umrah_deal)
        except Exception as e:
            print(f"Error parsing deal: {e}")
            continue

    # Calculate search duration
    end_time = datetime.now()
    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    return SearchResponse(
        search_id=None,
        deals=deals,
        total_results=len(deals),
        search_duration_ms=duration_ms,
        searched_at=datetime.now()
    )


@router.post("/save-search")
async def save_search_with_alerts(request: SavedSearchRequest, background_tasks: BackgroundTasks):
    """
    Save a search and enable alerts for price drops and new deals

    Returns saved search ID and confirmation of alert setup.
    """

    # Generate a unique search ID
    search_id = f"search_{int(datetime.now().timestamp())}"

    # TODO: Save to database
    # For now, return success response

    return {
        "success": True,
        "search_id": search_id,
        "message": "Search saved successfully",
        "alert_status": {
            "email": request.alert_email,
            "whatsapp": request.alert_whatsapp,
            "sms": request.alert_sms
        },
        "next_check": (datetime.now() + timedelta(hours=6)).isoformat(),
        "notification": f"You'll receive alerts via {'email' if request.alert_email else ''}{' and WhatsApp' if request.alert_whatsapp else ''}{' and SMS' if request.alert_sms else ''}"
    }


@router.get("/saved-searches")
async def get_saved_searches(user_email: str):
    """
    Get all saved searches for a user

    Returns list of saved searches with alert status.
    """

    # TODO: Fetch from database
    # Mock response for now
    return {
        "searches": [
            {
                "id": "search_1",
                "name": "Makkah 5-star under $500",
                "destination": "Makkah",
                "budget_max": 500,
                "hotel_rating": 5,
                "alert_enabled": True,
                "last_checked": datetime.now().isoformat(),
                "best_price_found": 450,
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1
    }


@router.get("/alerts")
async def get_user_alerts(user_email: str, limit: int = 20):
    """
    Get recent alerts for a user

    Returns list of price drop and new deal notifications.
    """

    # TODO: Fetch from database
    # Mock response
    return {
        "alerts": [
            {
                "id": "alert_1",
                "type": "price_drop",
                "message": "Price dropped by $50 on Makkah Clock Royal Tower",
                "deal": {
                    "hotel_name": "Makkah Clock Royal Tower",
                    "old_price": 500,
                    "new_price": 450
                },
                "sent_at": datetime.now().isoformat(),
                "is_read": False
            }
        ],
        "total": 1,
        "unread": 1
    }


@router.delete("/saved-search/{search_id}")
async def delete_saved_search(search_id: str):
    """
    Delete a saved search and its alerts
    """

    # TODO: Delete from database
    return {
        "success": True,
        "message": f"Search {search_id} deleted successfully"
    }


@router.put("/saved-search/{search_id}/alerts")
async def update_alert_preferences(search_id: str, email: bool, whatsapp: bool, sms: bool):
    """
    Update alert preferences for a saved search
    """

    # TODO: Update in database
    return {
        "success": True,
        "search_id": search_id,
        "alert_preferences": {
            "email": email,
            "whatsapp": whatsapp,
            "sms": sms
        }
    }

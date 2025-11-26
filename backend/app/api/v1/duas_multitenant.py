"""
Global Waqaf Tech - Du'a & Dhikr Studio API
Multi-tenant Islamic supplications generator with AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models_multitenant import User, Organization, DuaGeneration
from app.core.deps import (
    get_current_user,
    get_current_organization,
    require_feature,
    get_pagination_params,
)
from app.core.permissions import get_feature_limit, check_usage_limit


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DuaGenerateRequest(BaseModel):
    """Request to generate a du'a"""
    topic: str  # e.g., "morning", "evening", "travel", "health", "success"
    situation: Optional[str] = None  # Additional context
    language: str = "en"
    level: str = "adults"  # kids, adults
    include_arabic: bool = True
    include_transliteration: bool = True


class DuaResponse(BaseModel):
    """Du'a response with all details"""
    id: str
    topic: str
    situation: Optional[str]
    arabic_text: Optional[str]
    transliteration: Optional[str]
    translation: str
    explanation: Optional[str]
    source_reference: Optional[str]
    benefits: Optional[List[str]]
    is_saved: bool
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DuaListResponse(BaseModel):
    """List of duas with pagination"""
    duas: List[DuaResponse]
    total: int
    skip: int
    limit: int


class DuaUpdateRequest(BaseModel):
    """Update du'a flags"""
    is_saved: Optional[bool] = None
    is_favorite: Optional[bool] = None


# ============================================================================
# DU'A DATABASE (In production, this would be from database or API)
# ============================================================================

DUAS_DATABASE = {
    "morning": {
        "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ",
        "transliteration": "Asbahna wa asbahal-mulku lillah, walhamdu lillah",
        "translation": "We have entered morning and the dominion has entered the morning belonging to Allah, and all praise is for Allah",
        "explanation": "This du'a acknowledges Allah's sovereignty and expresses gratitude for entering a new day",
        "source": "Sahih Muslim",
        "benefits": [
            "Protection throughout the day",
            "Remembrance of Allah's sovereignty",
            "Starting the day with gratitude"
        ]
    },
    "evening": {
        "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ",
        "transliteration": "Amsayna wa amsal-mulku lillah, walhamdu lillah",
        "translation": "We have entered evening and the dominion has entered the evening belonging to Allah, and all praise is for Allah",
        "explanation": "Similar to the morning du'a, this acknowledges Allah's dominion over the evening",
        "source": "Sahih Muslim",
        "benefits": [
            "Protection throughout the night",
            "Remembrance of Allah's sovereignty",
            "Ending the day with gratitude"
        ]
    },
    "travel": {
        "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ",
        "transliteration": "Subhanal-ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin",
        "translation": "Glory be to Him who has subjected this to us, and we could never have it by our own efforts",
        "explanation": "A du'a for safe travel, acknowledging that all ability comes from Allah",
        "source": "Quran 43:13-14",
        "benefits": [
            "Safe travel",
            "Protection from accidents",
            "Gratitude for Allah's blessings"
        ]
    },
    "health": {
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ",
        "transliteration": "Allahumma inni as'alukal-'afiyata fid-dunya wal-akhirah",
        "translation": "O Allah, I ask You for well-being in this world and the Hereafter",
        "explanation": "A comprehensive du'a seeking health and well-being in both worlds",
        "source": "Sunan Abi Dawud",
        "benefits": [
            "Seeking health and wellness",
            "Protection from illness",
            "Well-being in both worlds"
        ]
    },
    "success": {
        "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
        "transliteration": "Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan wa qina 'adhaban-nar",
        "translation": "Our Lord, give us in this world good and in the Hereafter good and protect us from the punishment of the Fire",
        "explanation": "The most comprehensive du'a from the Quran, asking for success in both worlds",
        "source": "Quran 2:201",
        "benefits": [
            "Success in both worlds",
            "Protection from Hellfire",
            "Comprehensive du'a for all needs"
        ]
    },
    "gratitude": {
        "arabic": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "transliteration": "Alhamdu lillahi rabbil-'alamin",
        "translation": "All praise is due to Allah, Lord of all the worlds",
        "explanation": "The fundamental expression of gratitude to Allah",
        "source": "Quran 1:2",
        "benefits": [
            "Expressing gratitude",
            "Acknowledging Allah's lordship",
            "Increases blessings"
        ]
    },
    "forgiveness": {
        "arabic": "اللَّهُمَّ اغْفِرْ لِي ذَنْبِي كُلَّهُ، دِقَّهُ وَجِلَّهُ، وَأَوَّلَهُ وَآخِرَهُ، وَعَلَانِيَتَهُ وَسِرَّهُ",
        "transliteration": "Allahumma-ghfir li dhanbi kullahu, diqqahu wa jillahu, wa awwalahu wa akhirahu, wa 'alaniyatahu wa sirrahu",
        "translation": "O Allah, forgive all my sins, the small and the great, the first and the last, the open and the secret",
        "explanation": "A comprehensive du'a seeking Allah's forgiveness for all types of sins",
        "source": "Sahih Muslim",
        "benefits": [
            "Seeking complete forgiveness",
            "Acknowledging all types of sins",
            "Humility before Allah"
        ]
    },
    "guidance": {
        "arabic": "اللَّهُمَّ اهْدِنِي وَسَدِّدْنِي",
        "transliteration": "Allahumma-hdini wa saddidni",
        "translation": "O Allah, guide me and make me upright",
        "explanation": "A simple yet powerful du'a seeking Allah's guidance and steadfastness",
        "source": "Sahih Muslim",
        "benefits": [
            "Seeking divine guidance",
            "Asking for uprightness",
            "Staying on the straight path"
        ]
    }
}


# ============================================================================
# DU'A GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=DuaResponse)
async def generate_dua(
    request: DuaGenerateRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(require_feature("dua_studio")),
    db: Session = Depends(get_db)
):
    """
    Generate a du'a based on topic

    - Checks plan limits
    - Generates du'a with Arabic, transliteration, and translation
    - Tracks usage for the organization
    """
    # Check monthly usage limit
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_count = db.query(func.count(DuaGeneration.id)).filter(
        and_(
            DuaGeneration.organization_id == organization.id,
            DuaGeneration.created_at >= current_month_start
        )
    ).scalar()

    check_usage_limit(organization.plan, "dua_studio", monthly_count)

    # Get du'a from database
    topic_lower = request.topic.lower()

    if topic_lower not in DUAS_DATABASE:
        # In production, use AI to generate custom du'a
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Du'a for topic '{request.topic}' not found. Available topics: {', '.join(DUAS_DATABASE.keys())}"
        )

    dua_data = DUAS_DATABASE[topic_lower]

    # Create du'a generation record
    dua_generation = DuaGeneration(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        topic=request.topic,
        situation=request.situation,
        language=request.language,
        level=request.level,
        arabic_text=dua_data["arabic"] if request.include_arabic else None,
        transliteration=dua_data["transliteration"] if request.include_transliteration else None,
        translation=dua_data["translation"],
        explanation=dua_data.get("explanation"),
        source_reference=dua_data.get("source"),
        benefits=dua_data.get("benefits", []),
        is_saved=False,
        is_favorite=False,
        created_at=datetime.utcnow(),
    )

    db.add(dua_generation)
    db.commit()
    db.refresh(dua_generation)

    # Track usage
    from app.db.models_multitenant import FeatureUsage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="dua_studio",
        action="generate",
        request_data={"topic": request.topic, "language": request.language},
        success=True,
        created_at=datetime.utcnow(),
    )
    db.add(usage)
    db.commit()

    return DuaResponse(
        id=str(dua_generation.id),
        topic=dua_generation.topic,
        situation=dua_generation.situation,
        arabic_text=dua_generation.arabic_text,
        transliteration=dua_generation.transliteration,
        translation=dua_generation.translation,
        explanation=dua_generation.explanation,
        source_reference=dua_generation.source_reference,
        benefits=dua_generation.benefits,
        is_saved=dua_generation.is_saved,
        is_favorite=dua_generation.is_favorite,
        created_at=dua_generation.created_at,
    )


@router.get("/topics")
async def get_dua_topics(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available du'a topics
    """
    return {
        "topics": list(DUAS_DATABASE.keys()),
        "total": len(DUAS_DATABASE),
        "categories": {
            "daily": ["morning", "evening"],
            "travel": ["travel"],
            "health": ["health"],
            "spiritual": ["success", "gratitude", "forgiveness", "guidance"]
        }
    }


@router.get("/", response_model=DuaListResponse)
async def list_my_duas(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    pagination: dict = Depends(get_pagination_params),
    saved_only: bool = Query(False, description="Show only saved duas"),
    favorites_only: bool = Query(False, description="Show only favorite duas"),
    db: Session = Depends(get_db)
):
    """
    List organization's generated duas

    - Supports filtering by saved/favorites
    - Pagination
    """
    query = db.query(DuaGeneration).filter(
        DuaGeneration.organization_id == organization.id
    )

    if saved_only:
        query = query.filter(DuaGeneration.is_saved == True)

    if favorites_only:
        query = query.filter(DuaGeneration.is_favorite == True)

    # Get total count
    total = query.count()

    # Apply pagination
    duas = query.order_by(DuaGeneration.created_at.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()

    # Build response
    dua_responses = []
    for dua in duas:
        dua_responses.append(DuaResponse(
            id=str(dua.id),
            topic=dua.topic,
            situation=dua.situation,
            arabic_text=dua.arabic_text,
            transliteration=dua.transliteration,
            translation=dua.translation,
            explanation=dua.explanation,
            source_reference=dua.source_reference,
            benefits=dua.benefits,
            is_saved=dua.is_saved,
            is_favorite=dua.is_favorite,
            created_at=dua.created_at,
        ))

    return DuaListResponse(
        duas=dua_responses,
        total=total,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )


@router.get("/{dua_id}", response_model=DuaResponse)
async def get_dua(
    dua_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get specific du'a by ID

    - Organization members can only access their org's duas
    """
    dua = db.query(DuaGeneration).filter(
        DuaGeneration.id == dua_id,
        DuaGeneration.organization_id == organization.id
    ).first()

    if not dua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Du'a not found"
        )

    return DuaResponse(
        id=str(dua.id),
        topic=dua.topic,
        situation=dua.situation,
        arabic_text=dua.arabic_text,
        transliteration=dua.transliteration,
        translation=dua.translation,
        explanation=dua.explanation,
        source_reference=dua.source_reference,
        benefits=dua.benefits,
        is_saved=dua.is_saved,
        is_favorite=dua.is_favorite,
        created_at=dua.created_at,
    )


@router.patch("/{dua_id}", response_model=DuaResponse)
async def update_dua(
    dua_id: uuid.UUID,
    request: DuaUpdateRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update du'a (save/favorite flags)
    """
    dua = db.query(DuaGeneration).filter(
        DuaGeneration.id == dua_id,
        DuaGeneration.organization_id == organization.id
    ).first()

    if not dua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Du'a not found"
        )

    # Update fields
    if request.is_saved is not None:
        dua.is_saved = request.is_saved

    if request.is_favorite is not None:
        dua.is_favorite = request.is_favorite

    db.commit()
    db.refresh(dua)

    return DuaResponse(
        id=str(dua.id),
        topic=dua.topic,
        situation=dua.situation,
        arabic_text=dua.arabic_text,
        transliteration=dua.transliteration,
        translation=dua.translation,
        explanation=dua.explanation,
        source_reference=dua.source_reference,
        benefits=dua.benefits,
        is_saved=dua.is_saved,
        is_favorite=dua.is_favorite,
        created_at=dua.created_at,
    )


@router.delete("/{dua_id}")
async def delete_dua(
    dua_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a du'a
    """
    dua = db.query(DuaGeneration).filter(
        DuaGeneration.id == dua_id,
        DuaGeneration.organization_id == organization.id
    ).first()

    if not dua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Du'a not found"
        )

    db.delete(dua)
    db.commit()

    return {
        "success": True,
        "message": "Du'a deleted successfully"
    }


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats/usage")
async def get_dua_usage_stats(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get du'a usage statistics for organization
    """
    # Total duas generated
    total_duas = db.query(func.count(DuaGeneration.id)).filter(
        DuaGeneration.organization_id == organization.id
    ).scalar()

    # Current month usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_usage = db.query(func.count(DuaGeneration.id)).filter(
        and_(
            DuaGeneration.organization_id == organization.id,
            DuaGeneration.created_at >= current_month_start
        )
    ).scalar()

    # Get limit for current plan
    monthly_limit = get_feature_limit(organization.plan, "dua_studio", "limit")

    # Saved duas count
    saved_count = db.query(func.count(DuaGeneration.id)).filter(
        and_(
            DuaGeneration.organization_id == organization.id,
            DuaGeneration.is_saved == True
        )
    ).scalar()

    # Favorite duas count
    favorite_count = db.query(func.count(DuaGeneration.id)).filter(
        and_(
            DuaGeneration.organization_id == organization.id,
            DuaGeneration.is_favorite == True
        )
    ).scalar()

    return {
        "organization_id": str(organization.id),
        "organization_name": organization.name,
        "plan": organization.plan,
        "usage": {
            "total_all_time": total_duas,
            "current_month": monthly_usage,
            "monthly_limit": monthly_limit,
            "limit_remaining": monthly_limit - monthly_usage if monthly_limit != -1 else "unlimited",
            "saved_duas": saved_count,
            "favorite_duas": favorite_count,
        }
    }

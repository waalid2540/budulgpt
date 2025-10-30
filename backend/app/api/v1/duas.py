"""
Du'ā Generator API Endpoint for MadinaGPT
Generates Islamic duas (supplications) with Arabic text, transliteration, and meanings
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()


class DuaRequest(BaseModel):
    """Request model for dua generation"""
    purpose: str  # e.g., "morning", "evening", "travel", "health", "success"
    language: str = "en"  # Language for translation
    include_arabic: bool = True
    include_transliteration: bool = True


class DuaResponse(BaseModel):
    """Response model for generated dua"""
    dua_id: str
    arabic_text: Optional[str]
    transliteration: Optional[str]
    english_translation: str
    occasion: str
    source: Optional[str]  # e.g., "Quran 2:201", "Sahih Bukhari 123"
    benefits: List[str]
    generated_at: datetime


# Sample duas database (in production, this would be from a real database)
DUAS_DATABASE = {
    "morning": {
        "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ",
        "transliteration": "Asbahna wa asbahal-mulku lillah, walhamdu lillah",
        "translation": "We have entered morning and the dominion has entered the morning belonging to Allah, and all praise is for Allah",
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
        "source": "Quran 2:201",
        "benefits": [
            "Success in both worlds",
            "Protection from Hellfire",
            "Comprehensive dua for all needs"
        ]
    }
}


@router.post("/generate", response_model=DuaResponse)
async def generate_dua(request: DuaRequest):
    """
    Generate a dua based on the specified purpose

    - **purpose**: The occasion or purpose of the dua (morning, evening, travel, health, success)
    - **language**: Language for translation (currently supports 'en')
    - **include_arabic**: Whether to include Arabic text
    - **include_transliteration**: Whether to include transliteration
    """

    purpose_lower = request.purpose.lower()

    # Check if dua exists in database
    if purpose_lower not in DUAS_DATABASE:
        raise HTTPException(
            status_code=404,
            detail=f"Dua for purpose '{request.purpose}' not found. Available purposes: {', '.join(DUAS_DATABASE.keys())}"
        )

    dua_data = DUAS_DATABASE[purpose_lower]

    # Generate dua response
    response = DuaResponse(
        dua_id=f"dua_{purpose_lower}_{int(datetime.now().timestamp())}",
        arabic_text=dua_data["arabic"] if request.include_arabic else None,
        transliteration=dua_data["transliteration"] if request.include_transliteration else None,
        english_translation=dua_data["translation"],
        occasion=purpose_lower.capitalize(),
        source=dua_data.get("source"),
        benefits=dua_data.get("benefits", []),
        generated_at=datetime.now()
    )

    return response


@router.get("/purposes")
async def get_dua_purposes():
    """
    Get a list of available dua purposes
    """
    return {
        "purposes": list(DUAS_DATABASE.keys()),
        "total": len(DUAS_DATABASE)
    }


@router.get("/random", response_model=DuaResponse)
async def get_random_dua():
    """
    Get a random dua from the database
    """
    import random

    purpose = random.choice(list(DUAS_DATABASE.keys()))
    dua_data = DUAS_DATABASE[purpose]

    response = DuaResponse(
        dua_id=f"dua_{purpose}_{int(datetime.now().timestamp())}",
        arabic_text=dua_data["arabic"],
        transliteration=dua_data["transliteration"],
        english_translation=dua_data["translation"],
        occasion=purpose.capitalize(),
        source=dua_data.get("source"),
        benefits=dua_data.get("benefits", []),
        generated_at=datetime.now()
    )

    return response

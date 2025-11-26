"""
Global Waqaf Tech - Kids Story Studio API
Multi-tenant Islamic story generator for children with AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models_multitenant import User, Organization, StoryGeneration
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

class StoryGenerateRequest(BaseModel):
    """Request to generate a story"""
    theme: str  # honesty, kindness, gratitude, salah, etc.
    age_range: str = "5-8"  # 3-5, 5-8, 9-12
    style: str = "short"  # short, medium, long
    language: str = "en"
    custom_prompt: Optional[str] = None


class StoryResponse(BaseModel):
    """Story response with all details"""
    id: str
    title: str
    content: str
    theme: str
    age_range: str
    moral_lesson: str
    islamic_teaching: str
    discussion_questions: List[str]
    related_verses: List[str]
    is_saved: bool
    is_favorite: bool
    read_count: int
    rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class StoryListResponse(BaseModel):
    """List of stories with pagination"""
    stories: List[StoryResponse]
    total: int
    skip: int
    limit: int


class StoryUpdateRequest(BaseModel):
    """Update story flags"""
    is_saved: Optional[bool] = None
    is_favorite: Optional[bool] = None
    rating: Optional[int] = None  # 1-5


# ============================================================================
# STORY DATABASE
# ============================================================================

STORIES_DATABASE = {
    "honesty": {
        "title": "The Truthful Merchant of Madinah",
        "content": """Once upon a time in the beautiful city of Madinah, there lived a young merchant named Bilal. Bilal sold dates and honey in the marketplace, and he was known for his kindness and bright smile.

One busy day, a traveler came to his stall and bought a large bag of dates. The traveler was in a hurry to catch his caravan, so he quickly paid and rushed away. After he left, Bilal noticed he had accidentally given the man old dates instead of the fresh ones he had paid for!

Even though the traveler was far away and would never know about the mistake, Bilal's heart felt heavy. He remembered what Prophet Muhammad (peace be upon him) taught: "Truthfulness leads to righteousness, and righteousness leads to Paradise."

Bilal immediately closed his stall and ran through the marketplace, past the city gates, until he found the traveler preparing to leave. Out of breath, Bilal explained his mistake and gave him the fresh dates, taking back the old ones.

The traveler was amazed! "You could have kept quiet, and I would never have known," he said.

Bilal smiled and replied, "But Allah would have known, and that is what matters most."

The traveler was so impressed by Bilal's honesty that he told everyone in the marketplace about the truthful merchant. Soon, people from all over came to buy from Bilal because they knew they could trust him.

Bilal's business grew, and he became successful. But more importantly, he had pleased Allah by being honest, and that made him the happiest of all!""",
        "moral": "Always tell the truth, even when no one is watching. Allah sees everything, and honesty brings blessings in this life and the next.",
        "teaching": "The Prophet Muhammad (peace be upon him) said: 'Truthfulness leads to righteousness, and righteousness leads to Paradise.' Being honest, even when it's difficult, is one of the most important qualities of a Muslim.",
        "questions": [
            "Why did Bilal run after the traveler even though the traveler didn't know about the mistake?",
            "How did being honest help Bilal's business in the end?",
            "Can you think of a time when you told the truth even though it was hard?"
        ],
        "verses": [
            "Quran 9:119 - 'O you who have believed, fear Allah and be with those who are true.'",
            "Hadith - 'Truthfulness leads to righteousness, and righteousness leads to Paradise.'"
        ]
    },
    "kindness": {
        "title": "Aisha and the Kind Neighbor",
        "content": """In a peaceful village, there lived a young girl named Aisha who loved helping others. She lived next door to Umm Hassan, an elderly woman who lived alone and sometimes found it hard to do everyday tasks.

Every Friday after Jumu'ah prayer, Aisha would visit Umm Hassan. Sometimes she would help clean the house, sometimes she would read Quran to her, and sometimes they would just sit and talk. Aisha's mother had taught her that being kind to neighbors is one of the best deeds in Islam.

One cold winter day, Umm Hassan fell ill with a fever. When Aisha heard the news, she immediately told her family. Her mother made warm soup, her father brought medicine, and Aisha brought warm blankets.

Every day, Aisha's family took turns checking on Umm Hassan, bringing her food, and making sure she was comfortable. They didn't do it because they expected anything in return – they did it because it was the right thing to do.

After two weeks, Umm Hassan felt better. When spring came, her garden bloomed with beautiful flowers. She called Aisha over and said, "These flowers are lovely, but they are nothing compared to the beautiful kindness you and your family showed me. You treated me like I was your own grandmother!"

Tears of happiness filled Umm Hassan's eyes. She made du'a for Aisha and her family, asking Allah to bless them always.

Aisha learned that small acts of kindness can make a big difference in someone's life, and that being good to neighbors is one of the things that pleases Allah the most.""",
        "moral": "Be kind to your neighbors and help those in need. Small acts of kindness can make a huge difference in someone's life.",
        "teaching": "The Prophet (peace be upon him) said: 'Whoever believes in Allah and the Last Day, let him be kind to his neighbor.' Taking care of neighbors, especially elderly ones, is a beautiful sunnah.",
        "questions": [
            "What are some things Aisha did to help Umm Hassan?",
            "Why is it important to be kind to our neighbors?",
            "What is one kind thing you can do for your neighbor this week?"
        ],
        "verses": [
            "Quran 4:36 - 'Worship Allah and associate nothing with Him, and to parents do good, and to relatives, orphans, the needy, the near neighbor, the neighbor farther away...'",
            "Hadith - 'The best of companions in the sight of Allah is the best to his companion, and the best of neighbors is the best to his neighbor.'"
        ]
    },
    "salah": {
        "title": "Omar's Special Meetings with Allah",
        "content": """Omar was a curious seven-year-old boy who loved asking questions. One day, he asked his father, "Baba, why do we pray five times every day?"

His father smiled and said, "Let me tell you a story that will help you understand."

"Imagine if you had a best friend who lived far away," his father began. "Would you like to talk to them every day?"

"Yes!" Omar said excitedly.

"Well, Allah is better than any friend, and salah is our special meeting with Him! Five times a day, we get to talk to Allah, thank Him, ask Him for help, and remember how much He loves us."

Omar's eyes widened with understanding. From that day on, he started looking at salah differently. Instead of thinking it was just something he had to do, he realized it was something special – his private meeting with Allah!

When he prayed Fajr in the morning, he would say, "Good morning, Allah! Thank you for this new day!"

At Dhuhr, he would think about all the good things that happened in the morning and thank Allah for them.

Asr prayer reminded him that the day was almost over, so he should do something good before it ends.

At Maghrib, he would ask Allah to forgive any mistakes he made that day.

And at Isha, before going to sleep, he would ask Allah to protect him through the night.

Omar's little sister noticed how happy he looked when he prayed. "Why are you smiling?" she asked.

"Because," Omar said, "I'm meeting with Allah, and that makes me the happiest person in the world!"

His sister smiled too, and from then on, they both loved their special meetings with Allah.""",
        "moral": "Salah is not just a duty – it's a special gift that lets us connect with Allah five times a day!",
        "teaching": "Prayer (salah) is the second pillar of Islam and our direct connection to Allah. The Prophet (peace be upon him) said that salah is 'the coolness of his eyes' – meaning it brought him peace and joy!",
        "questions": [
            "How many times do we pray each day? Can you name them?",
            "What does Omar compare salah to in the story?",
            "How do you feel when you pray? What do you like to thank Allah for?"
        ],
        "verses": [
            "Quran 29:45 - 'Indeed, prayer prohibits immorality and wrongdoing, and the remembrance of Allah is greater.'",
            "Hadith - 'The first thing that a person will be questioned about on the Day of Judgment is salah.'"
        ]
    },
    "gratitude": {
        "title": "The Grateful Farmer's Secret",
        "content": """In a small village, there were two farmers who lived next to each other. The first farmer, Omar, had a small farm with a few sheep, some chickens, and a small vegetable garden. The second farmer, Khalid, had a much larger farm with many animals and big fields of crops.

Every morning, Omar would wake up before Fajr prayer and say, "Alhamdulillah! All praise is for Allah!" He was grateful for everything he had, even though it was small.

Khalid, on the other hand, was never happy. Even though he had more than Omar, he always wanted more animals, bigger crops, and a larger house. He rarely said Alhamdulillah.

One year, there was very little rain. Many farmers lost their crops. Omar's small garden survived because he had always taken good care of it and planted strong seeds. He still said, "Alhamdulillah!"

Khalid's large farm suffered greatly because he had been careless. He became very sad and asked Omar, "How can you still be grateful when times are so hard?"

Omar smiled warmly and said, "My dear neighbor, I have my health, my family, my faith, and food to eat. I have a roof over my head and clothes on my back. Allah has given me more than I truly need! When we say Alhamdulillah and are grateful for what we have, we see how rich we really are."

Khalid thought about this deeply. That night, for the first time in years, he truly thanked Allah for all his blessings. He realized that gratitude wasn't about having everything – it was about appreciating everything you have.

From that day on, both farmers could be heard saying "Alhamdulillah!" and they both lived happily, not because they had everything, but because they were grateful for what Allah had given them.""",
        "moral": "Always be grateful for what you have. When we thank Allah by saying Alhamdulillah, we realize how truly blessed we are!",
        "teaching": "Allah says in the Quran: 'If you are grateful, I will surely increase you in favor' (14:7). The Prophet Muhammad (peace be upon him) taught us that gratitude is the key to happiness and more blessings.",
        "questions": [
            "What was the difference between Omar and Khalid at the beginning of the story?",
            "Why was Omar happy even when there was very little rain?",
            "What are three things you are grateful for today?"
        ],
        "verses": [
            "Quran 14:7 - 'If you are grateful, I will surely increase you in favor.'",
            "Hadith - 'He who does not thank people, does not thank Allah.'",
            "Sunnah - The Prophet (peace be upon him) would say Alhamdulillah for everything, in good times and in difficult times."
        ]
    }
}


# ============================================================================
# STORY GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    request: StoryGenerateRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(require_feature("story_studio")),
    db: Session = Depends(get_db)
):
    """
    Generate an Islamic kids story

    - Checks plan limits
    - Generates age-appropriate story with moral lessons
    - Tracks usage for the organization
    """
    # Check monthly usage limit
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_count = db.query(func.count(StoryGeneration.id)).filter(
        and_(
            StoryGeneration.organization_id == organization.id,
            StoryGeneration.created_at >= current_month_start
        )
    ).scalar()

    check_usage_limit(organization.plan, "story_studio", monthly_count)

    # Get story from database
    theme_lower = request.theme.lower()

    if theme_lower not in STORIES_DATABASE:
        # In production, use AI to generate custom story
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story for theme '{request.theme}' not found. Available themes: {', '.join(STORIES_DATABASE.keys())}"
        )

    story_data = STORIES_DATABASE[theme_lower]

    # Create story generation record
    story_generation = StoryGeneration(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        age_range=request.age_range,
        theme=request.theme,
        style=request.style,
        language=request.language,
        custom_prompt=request.custom_prompt,
        title=story_data["title"],
        content=story_data["content"],
        moral_lesson=story_data["moral"],
        islamic_teaching=story_data["teaching"],
        discussion_questions=story_data["questions"],
        related_verses=story_data["verses"],
        is_saved=False,
        is_favorite=False,
        read_count=0,
        created_at=datetime.utcnow(),
    )

    db.add(story_generation)
    db.commit()
    db.refresh(story_generation)

    # Track usage
    from app.db.models_multitenant import FeatureUsage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="story_studio",
        action="generate",
        request_data={"theme": request.theme, "age_range": request.age_range},
        success=True,
        created_at=datetime.utcnow(),
    )
    db.add(usage)
    db.commit()

    return StoryResponse(
        id=str(story_generation.id),
        title=story_generation.title,
        content=story_generation.content,
        theme=story_generation.theme,
        age_range=story_generation.age_range,
        moral_lesson=story_generation.moral_lesson,
        islamic_teaching=story_generation.islamic_teaching,
        discussion_questions=story_generation.discussion_questions,
        related_verses=story_generation.related_verses,
        is_saved=story_generation.is_saved,
        is_favorite=story_generation.is_favorite,
        read_count=story_generation.read_count,
        rating=story_generation.rating,
        created_at=story_generation.created_at,
    )


@router.get("/themes")
async def get_story_themes(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available story themes
    """
    return {
        "themes": list(STORIES_DATABASE.keys()),
        "total": len(STORIES_DATABASE),
        "age_ranges": ["3-5", "5-8", "9-12"],
        "styles": ["short", "medium", "long"],
        "categories": {
            "character": ["honesty", "kindness", "gratitude"],
            "worship": ["salah"],
            "more_coming": "Additional themes will be added regularly"
        }
    }


@router.get("/", response_model=StoryListResponse)
async def list_my_stories(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    pagination: dict = Depends(get_pagination_params),
    saved_only: bool = Query(False, description="Show only saved stories"),
    favorites_only: bool = Query(False, description="Show only favorite stories"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    db: Session = Depends(get_db)
):
    """
    List organization's generated stories

    - Supports filtering by saved/favorites/theme
    - Pagination
    """
    query = db.query(StoryGeneration).filter(
        StoryGeneration.organization_id == organization.id
    )

    if saved_only:
        query = query.filter(StoryGeneration.is_saved == True)

    if favorites_only:
        query = query.filter(StoryGeneration.is_favorite == True)

    if theme:
        query = query.filter(StoryGeneration.theme.ilike(f"%{theme}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    stories = query.order_by(StoryGeneration.created_at.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()

    # Build response
    story_responses = []
    for story in stories:
        story_responses.append(StoryResponse(
            id=str(story.id),
            title=story.title,
            content=story.content,
            theme=story.theme,
            age_range=story.age_range,
            moral_lesson=story.moral_lesson,
            islamic_teaching=story.islamic_teaching,
            discussion_questions=story.discussion_questions,
            related_verses=story.related_verses,
            is_saved=story.is_saved,
            is_favorite=story.is_favorite,
            read_count=story.read_count,
            rating=story.rating,
            created_at=story.created_at,
        ))

    return StoryListResponse(
        stories=story_responses,
        total=total,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get specific story by ID

    - Increments read count
    - Organization members can only access their org's stories
    """
    story = db.query(StoryGeneration).filter(
        StoryGeneration.id == story_id,
        StoryGeneration.organization_id == organization.id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )

    # Increment read count
    story.read_count += 1
    db.commit()
    db.refresh(story)

    return StoryResponse(
        id=str(story.id),
        title=story.title,
        content=story.content,
        theme=story.theme,
        age_range=story.age_range,
        moral_lesson=story.moral_lesson,
        islamic_teaching=story.islamic_teaching,
        discussion_questions=story.discussion_questions,
        related_verses=story.related_verses,
        is_saved=story.is_saved,
        is_favorite=story.is_favorite,
        read_count=story.read_count,
        rating=story.rating,
        created_at=story.created_at,
    )


@router.patch("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: uuid.UUID,
    request: StoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update story (save/favorite/rating flags)
    """
    story = db.query(StoryGeneration).filter(
        StoryGeneration.id == story_id,
        StoryGeneration.organization_id == organization.id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )

    # Update fields
    if request.is_saved is not None:
        story.is_saved = request.is_saved

    if request.is_favorite is not None:
        story.is_favorite = request.is_favorite

    if request.rating is not None:
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        story.rating = request.rating

    db.commit()
    db.refresh(story)

    return StoryResponse(
        id=str(story.id),
        title=story.title,
        content=story.content,
        theme=story.theme,
        age_range=story.age_range,
        moral_lesson=story.moral_lesson,
        islamic_teaching=story.islamic_teaching,
        discussion_questions=story.discussion_questions,
        related_verses=story.related_verses,
        is_saved=story.is_saved,
        is_favorite=story.is_favorite,
        read_count=story.read_count,
        rating=story.rating,
        created_at=story.created_at,
    )


@router.delete("/{story_id}")
async def delete_story(
    story_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a story
    """
    story = db.query(StoryGeneration).filter(
        StoryGeneration.id == story_id,
        StoryGeneration.organization_id == organization.id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )

    db.delete(story)
    db.commit()

    return {
        "success": True,
        "message": "Story deleted successfully"
    }


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats/usage")
async def get_story_usage_stats(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get story usage statistics for organization
    """
    # Total stories generated
    total_stories = db.query(func.count(StoryGeneration.id)).filter(
        StoryGeneration.organization_id == organization.id
    ).scalar()

    # Current month usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_usage = db.query(func.count(StoryGeneration.id)).filter(
        and_(
            StoryGeneration.organization_id == organization.id,
            StoryGeneration.created_at >= current_month_start
        )
    ).scalar()

    # Get limit for current plan
    monthly_limit = get_feature_limit(organization.plan, "story_studio", "limit")

    # Saved stories count
    saved_count = db.query(func.count(StoryGeneration.id)).filter(
        and_(
            StoryGeneration.organization_id == organization.id,
            StoryGeneration.is_saved == True
        )
    ).scalar()

    # Total reads
    total_reads = db.query(func.sum(StoryGeneration.read_count)).filter(
        StoryGeneration.organization_id == organization.id
    ).scalar() or 0

    return {
        "organization_id": str(organization.id),
        "organization_name": organization.name,
        "plan": organization.plan,
        "usage": {
            "total_all_time": total_stories,
            "current_month": monthly_usage,
            "monthly_limit": monthly_limit,
            "limit_remaining": monthly_limit - monthly_usage if monthly_limit != -1 else "unlimited",
            "saved_stories": saved_count,
            "total_reads": total_reads,
        }
    }

"""
Islamic Kids Story Generator API Endpoint for MadinaGPT
Generates age-appropriate Islamic stories with moral lessons
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()


class StoryRequest(BaseModel):
    """Request model for story generation"""
    theme: str  # e.g., "honesty", "kindness", "gratitude", "courage", "prayer"
    age_group: str = "5-8"  # "3-5", "5-8", "9-12"
    language: str = "en"
    length: str = "short"  # "short" (5-7 min), "medium" (10-15 min), "long" (20+ min)


class StoryResponse(BaseModel):
    """Response model for generated story"""
    story_id: str
    title: str
    content: str
    theme: str
    moral_lesson: str
    age_group: str
    islamic_teaching: str
    discussion_questions: List[str]
    related_verses: List[str]  # Quran verses or Hadith references
    generated_at: datetime


# Sample stories database (in production, this would use AI generation or real database)
STORIES_DATABASE = {
    "honesty": {
        "title": "The Truthful Merchant",
        "content": """Once upon a time in the beautiful city of Madinah, there lived a young merchant named Bilal. Bilal sold dates and honey in the marketplace.

One day, a traveler came to his stall and bought a large bag of dates. After the traveler left, Bilal noticed he had accidentally given the man old dates instead of the fresh ones he had paid for.

Even though the traveler was far away and would never know, Bilal immediately closed his stall and ran after him. He found the traveler at the city gates and gave him the fresh dates, returning the old ones.

The traveler was amazed by Bilal's honesty. He told everyone in the marketplace about the truthful merchant, and soon, people from all over came to buy from Bilal because they knew they could trust him.

Bilal always remembered the words of Prophet Muhammad (peace be upon him): "Truthfulness leads to righteousness, and righteousness leads to Paradise."""",
        "moral": "Always tell the truth, even when no one is watching. Allah sees everything, and honesty brings blessings.",
        "teaching": "The Prophet Muhammad (peace be upon him) taught us that honesty is one of the most important qualities of a Muslim.",
        "questions": [
            "Why did Bilal run after the traveler?",
            "How did being honest help Bilal's business?",
            "Can you think of a time when you were honest even though it was hard?"
        ],
        "verses": [
            "Quran 9:119 - 'O you who have believed, fear Allah and be with those who are true.'",
            "Hadith - 'Truthfulness leads to righteousness, and righteousness leads to Paradise.'"
        ]
    },
    "kindness": {
        "title": "The Kind Neighbor",
        "content": """In a small village, there lived a girl named Aisha who loved helping others. Her neighbor, an elderly woman named Umm Hassan, lived alone and found it hard to carry her groceries.

Every Friday after Jumu'ah prayer, Aisha would visit Umm Hassan and ask if she needed anything. Sometimes she would help clean, sometimes she would read Quran to her, and sometimes they would just talk.

One winter day, Umm Hassan fell ill. Aisha's family brought her soup, medicine, and warm blankets. They took turns caring for her until she recovered.

When spring came, Umm Hassan's garden bloomed with beautiful flowers. She told everyone, "These flowers are nothing compared to the beautiful kindness Aisha and her family showed me."

Aisha learned that being kind to neighbors is one of the best deeds in Islam, just as the Prophet Muhammad (peace be upon him) taught.""",
        "moral": "Be kind to your neighbors and help those in need. Small acts of kindness can make a big difference.",
        "teaching": "The Prophet (peace be upon him) said: 'The best of companions in the sight of Allah is the best to his companion, and the best of neighbors is the best to his neighbor.'",
        "questions": [
            "How did Aisha help Umm Hassan?",
            "Why is it important to be kind to neighbors?",
            "What nice thing can you do for your neighbor this week?"
        ],
        "verses": [
            "Quran 4:36 - 'Worship Allah and associate nothing with Him, and to parents do good, and to relatives, orphans, the needy, the near neighbor, the neighbor farther away...'",
            "Hadith - 'Whoever believes in Allah and the Last Day, let him be kind to his neighbor.'"
        ]
    },
    "gratitude": {
        "title": "The Grateful Farmer",
        "content": """There was a farmer named Omar who had a small farm with a few sheep, some chickens, and a vegetable garden. Every morning, he would wake up before Fajr prayer and thank Allah for his blessings.

His friend Khalid had a much larger farm with many animals and crops. But Khalid was never happy - he always wanted more.

One year, a drought came. Many farmers lost their crops. Omar's small garden survived because he had always taken good care of it and planted strong seeds. He still said "Alhamdulillah" (All praise is due to Allah).

Khalid's large farm suffered greatly because he had been careless. He became sad and asked Omar, "How can you still be grateful when times are hard?"

Omar smiled and said, "I have my health, my family, my faith, and enough food to eat. Allah has given me more than I need. Being grateful for what we have makes us see how rich we truly are."

Khalid learned an important lesson that day and started practicing gratitude like his friend Omar.""",
        "moral": "Always be grateful for what you have. Allah loves those who say Alhamdulillah in good times and bad times.",
        "teaching": "The Prophet Muhammad (peace be upon him) said: 'If you are grateful, I will surely increase you in favor.'",
        "questions": [
            "What was the difference between Omar and Khalid?",
            "Why was Omar happy even during the drought?",
            "What three things are you grateful for today?"
        ],
        "verses": [
            "Quran 14:7 - 'If you are grateful, I will surely increase you in favor.'",
            "Hadith - 'He who does not thank people, does not thank Allah.'"
        ]
    }
}


@router.post("/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """
    Generate an Islamic kids story based on the specified theme

    - **theme**: The moral theme of the story (honesty, kindness, gratitude, etc.)
    - **age_group**: Target age group (3-5, 5-8, 9-12)
    - **language**: Language for the story (currently supports 'en')
    - **length**: Story length (short, medium, long)
    """

    theme_lower = request.theme.lower()

    # Check if story theme exists in database
    if theme_lower not in STORIES_DATABASE:
        raise HTTPException(
            status_code=404,
            detail=f"Story for theme '{request.theme}' not found. Available themes: {', '.join(STORIES_DATABASE.keys())}"
        )

    story_data = STORIES_DATABASE[theme_lower]

    # Generate story response
    response = StoryResponse(
        story_id=f"story_{theme_lower}_{int(datetime.now().timestamp())}",
        title=story_data["title"],
        content=story_data["content"],
        theme=theme_lower.capitalize(),
        moral_lesson=story_data["moral"],
        age_group=request.age_group,
        islamic_teaching=story_data["teaching"],
        discussion_questions=story_data["questions"],
        related_verses=story_data["verses"],
        generated_at=datetime.now()
    )

    return response


@router.get("/themes")
async def get_story_themes():
    """
    Get a list of available story themes
    """
    return {
        "themes": list(STORIES_DATABASE.keys()),
        "total": len(STORIES_DATABASE),
        "age_groups": ["3-5", "5-8", "9-12"],
        "lengths": ["short", "medium", "long"]
    }


@router.get("/random", response_model=StoryResponse)
async def get_random_story(age_group: str = "5-8"):
    """
    Get a random Islamic kids story

    - **age_group**: Target age group (default: 5-8)
    """
    import random

    theme = random.choice(list(STORIES_DATABASE.keys()))
    story_data = STORIES_DATABASE[theme]

    response = StoryResponse(
        story_id=f"story_{theme}_{int(datetime.now().timestamp())}",
        title=story_data["title"],
        content=story_data["content"],
        theme=theme.capitalize(),
        moral_lesson=story_data["moral"],
        age_group=age_group,
        islamic_teaching=story_data["teaching"],
        discussion_questions=story_data["questions"],
        related_verses=story_data["verses"],
        generated_at=datetime.now()
    )

    return response

"""
Main API router for Budul AI v1
"""

from fastapi import APIRouter
from app.api.v1 import islamic_content, chat, islamic_chat, simple_chat

api_router = APIRouter()

# Include existing API route modules
api_router.include_router(islamic_content.router, prefix="/content", tags=["islamic-content"])
api_router.include_router(chat.router, prefix="/chat", tags=["budul-gpt"])
api_router.include_router(islamic_chat.router, prefix="/islamic-chat", tags=["islamic-ai"])
api_router.include_router(simple_chat.router, prefix="/budul-ai", tags=["budul-ai-trained"])
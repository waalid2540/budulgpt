"""
Budul GPT Chat API endpoints
Provides Islamic conversational AI with authentic citations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from uuid import uuid4
from datetime import datetime

from app.services.islamic_ai_service import IslamicAIService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the Islamic AI service
ai_service = IslamicAIService()

@router.post("/", summary="Chat with Budul AI")
async def chat(request: Dict[str, Any]):
    """
    Send a message to Budul AI and get an Islamic-informed response
    """
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response using the trained Islamic AI model
        response = await ai_service.generate_response(message)
        
        return {
            "id": str(uuid4()),
            "message": message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Budul AI chat is running"}
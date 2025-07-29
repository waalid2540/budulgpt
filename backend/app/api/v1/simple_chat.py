"""
Simple Chat API using your trained Budul AI model
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from ...services.budul_ai_service import budul_ai

# Router setup
router = APIRouter()

# Request/Response models
class SimpleChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SimpleChatResponse(BaseModel):
    response_id: str
    message: str
    session_id: str
    response_text: str
    confidence_score: float
    authenticity_score: float
    citations: list = []
    sources: list = []
    related_topics: list = []
    requires_scholar_review: bool = False
    content_warnings: list = []
    prayer_times: Optional[dict] = None
    qibla_direction: Optional[float] = None
    generated_at: str
    processing_time_ms: float

@router.post("/", response_model=SimpleChatResponse)
async def chat_with_budul_ai(request: SimpleChatRequest):
    """
    Chat with your trained Budul AI Islamic model
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate response using your trained model
        result = budul_ai.generate_response(request.message)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500, 
                detail=f"Budul AI Error: {result.get('error', 'Unknown error')}"
            )
        
        # Format response
        response = SimpleChatResponse(
            response_id=result.get("response_id", str(uuid.uuid4())),
            message=request.message,
            session_id=session_id,
            response_text=result.get("response", "No response generated"),
            confidence_score=result.get("confidence_score", 0.0),
            authenticity_score=result.get("authenticity_score", 0.0),
            citations=result.get("citations", []),
            sources=result.get("sources", []),
            related_topics=result.get("related_topics", []),
            requires_scholar_review=False,
            content_warnings=[],
            generated_at=datetime.utcnow().isoformat(),
            processing_time_ms=result.get("processing_time_ms", 1000.0)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/health")
async def budul_ai_health():
    """Check if Budul AI model is loaded and ready"""
    try:
        # Try to load model if not already loaded
        if not budul_ai.is_loaded:
            success = budul_ai.load_model()
            if not success:
                return {
                    "status": "unhealthy",
                    "service": "Budul AI - Your Trained Islamic Model",
                    "model_loaded": False,
                    "error": "Failed to load trained Islamic model"
                }
        
        return {
            "status": "healthy",
            "service": "Budul AI - Your Trained Islamic Model",
            "model_loaded": budul_ai.is_loaded,
            "model_path": budul_ai.model_path,
            "message": "🕌 Your trained Islamic AI model is ready to serve!"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "service": "Budul AI",
            "error": str(e)
        }

@router.post("/load-model")
async def load_budul_model():
    """Manually load the Budul AI model"""
    try:
        success = budul_ai.load_model()
        if success:
            return {
                "message": "✅ Budul AI model loaded successfully!",
                "model_path": budul_ai.model_path,
                "status": "loaded"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to load Budul AI model. Check if model files exist."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model loading error: {str(e)}")
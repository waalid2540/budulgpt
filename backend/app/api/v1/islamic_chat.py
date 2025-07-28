"""
Islamic GPT Chat API Endpoints
Advanced chat interface with WebSocket support for real-time conversations
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends, 
    HTTPException, BackgroundTasks, Query, Path
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

# Services
from ...services.islamic_gpt_service import (
    IslamicGPTService, ChatContext, IslamicResponse, 
    DifficultyLevel, IslamicTopic
)
from ...db.database import get_db
from ...core.auth import get_current_user_optional
from ...core.rate_limiting import rate_limit
from ...core.monitoring import track_api_call

# Monitoring
import structlog
from prometheus_client import Counter, Histogram

# Models
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    context: Optional[Dict] = Field(None, description="Additional context")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the five pillars of Islam?",
                "session_id": "12345",
                "context": {
                    "knowledge_level": "intermediate",
                    "madhab": "hanafi",
                    "language": "en"
                }
            }
        }

class ChatResponse(BaseModel):
    """Chat response model"""
    response_id: str
    message: str
    session_id: str
    response_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    authenticity_score: float = Field(..., ge=0.0, le=1.0)
    citations: List[Dict] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    requires_scholar_review: bool = False
    content_warnings: List[str] = Field(default_factory=list)
    prayer_times: Optional[Dict] = None
    qibla_direction: Optional[float] = None
    generated_at: datetime
    processing_time_ms: float
    
    class Config:
        schema_extra = {
            "example": {
                "response_id": "uuid4",
                "message": "What are the five pillars of Islam?",
                "session_id": "12345",
                "response_text": "The five pillars of Islam are...",
                "confidence_score": 0.95,
                "authenticity_score": 0.98,
                "citations": [
                    {
                        "type": "quran",
                        "reference": "Quran 2:177",
                        "text": "...",
                        "relevance": 0.9
                    }
                ],
                "sources": ["Quran 2:177", "Sahih Bukhari 8"],
                "related_topics": ["prayer", "charity", "pilgrimage"],
                "requires_scholar_review": False,
                "content_warnings": [],
                "generated_at": "2024-01-01T12:00:00Z",
                "processing_time_ms": 1250.5
            }
        }

class ConversationHistory(BaseModel):
    """Conversation history model"""
    session_id: str
    user_id: str
    messages: List[Dict]
    created_at: datetime
    last_activity: datetime
    total_messages: int
    
class UserPreferences(BaseModel):
    """User preferences for Islamic content"""
    knowledge_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    preferred_madhab: str = "general"
    preferred_language: str = "en"
    location: Optional[Dict] = None
    topics_of_interest: List[IslamicTopic] = Field(default_factory=list)
    notification_preferences: Dict = Field(default_factory=dict)
    
    @validator('preferred_madhab')
    def validate_madhab(cls, v):
        valid_madhabs = ['hanafi', 'maliki', 'shafii', 'hanbali', 'jafari', 'general']
        if v.lower() not in valid_madhabs:
            raise ValueError(f'Invalid madhab. Must be one of: {valid_madhabs}')
        return v.lower()

class StreamingChatRequest(BaseModel):
    """Streaming chat request model"""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    context: Optional[Dict] = None
    stream: bool = True

# Router setup
router = APIRouter(prefix="/chat", tags=["Islamic Chat"])
logger = structlog.get_logger(__name__)

# Metrics
chat_requests_counter = Counter('islamic_chat_requests_total', 'Total chat requests', ['endpoint'])
response_time_histogram = Histogram('islamic_chat_response_time_seconds', 'Chat response time')
websocket_connections_gauge = Counter('islamic_chat_websocket_connections', 'Active WebSocket connections')

# Global service instance
islamic_gpt_service: Optional[IslamicGPTService] = None

async def get_islamic_gpt_service() -> IslamicGPTService:
    """Get or initialize Islamic GPT service"""
    global islamic_gpt_service
    
    if islamic_gpt_service is None:
        islamic_gpt_service = IslamicGPTService()
        await islamic_gpt_service.initialize()
    
    return islamic_gpt_service

# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        """Connect a new WebSocket"""
        await websocket.accept()
        connection_id = f"{user_id}:{session_id}"
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        websocket_connections_gauge.inc()
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, user_id: str, session_id: str):
        """Disconnect WebSocket"""
        connection_id = f"{user_id}:{session_id}"
        
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_sessions:
            if session_id in self.user_sessions[user_id]:
                self.user_sessions[user_id].remove(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        websocket_connections_gauge.dec()
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, user_id: str, session_id: str, message: dict):
        """Send message to specific WebSocket"""
        connection_id = f"{user_id}:{session_id}"
        
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(user_id, session_id)

manager = ConnectionManager()

@router.post("/", response_model=ChatResponse)
@rate_limit(calls=60, period=60)  # 60 calls per minute
@track_api_call
async def chat_with_islamic_ai(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_optional),
    service: IslamicGPTService = Depends(get_islamic_gpt_service),
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Chat with Islamic AI assistant
    
    Send a message to the Islamic AI and receive a comprehensive response
    with citations, authenticity scoring, and scholarly verification.
    """
    start_time = datetime.utcnow()
    chat_requests_counter.labels(endpoint='chat').inc()
    
    try:
        # Default user ID for anonymous users
        if not user_id:
            user_id = f"anonymous_{uuid4().hex[:8]}"
        
        # Generate Islamic response
        islamic_response = await service.chat(
            message=request.message,
            user_id=user_id,
            session_id=request.session_id,
            context=request.context
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Create API response
        api_response = ChatResponse(
            response_id=islamic_response.response_id,
            message=request.message,
            session_id=islamic_response.response_id,  # Use response_id as session if not provided
            response_text=islamic_response.response_text,
            confidence_score=islamic_response.confidence_score,
            authenticity_score=islamic_response.authenticity_score,
            citations=islamic_response.citations,
            sources=islamic_response.sources,
            related_topics=islamic_response.related_topics,
            requires_scholar_review=islamic_response.requires_scholar_review,
            content_warnings=islamic_response.content_warnings,
            prayer_times=islamic_response.prayer_times,
            qibla_direction=islamic_response.qibla_direction,
            generated_at=islamic_response.generated_at,
            processing_time_ms=processing_time
        )
        
        # Log interaction for analytics
        background_tasks.add_task(
            log_chat_interaction,
            user_id, request.message, islamic_response, processing_time
        )
        
        # Record metrics
        response_time_histogram.observe(processing_time / 1000)
        
        return api_response
        
    except Exception as e:
        logger.error(f"Error in Islamic chat: {e}")
        raise HTTPException(status_code=500, detail=f"Islamic chat error: {str(e)}")

@router.post("/stream")
@rate_limit(calls=30, period=60)  # 30 streaming calls per minute
async def stream_chat_with_islamic_ai(
    request: StreamingChatRequest,
    user_id: str = Depends(get_current_user_optional),
    service: IslamicGPTService = Depends(get_islamic_gpt_service)
):
    """
    Stream chat with Islamic AI for real-time responses
    
    Provides streaming responses for better user experience with long answers.
    """
    chat_requests_counter.labels(endpoint='stream').inc()
    
    if not user_id:
        user_id = f"anonymous_{uuid4().hex[:8]}"
    
    async def generate_stream():
        try:
            async for chunk in service.stream_chat(
                message=request.message,
                user_id=user_id,
                session_id=request.session_id,
                context=request.context
            ):
                # Format chunk as Server-Sent Event
                yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.websocket("/ws/{user_id}/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: str = Path(...),
    session_id: str = Path(...),
    service: IslamicGPTService = Depends(get_islamic_gpt_service)
):
    """
    WebSocket endpoint for real-time Islamic chat
    
    Provides persistent connection for continuous Islamic conversations.
    """
    await manager.connect(websocket, user_id, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract message
            message = message_data.get('message', '')
            context = message_data.get('context', {})
            
            if not message:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Empty message received'
                }))
                continue
            
            # Send typing indicator
            await websocket.send_text(json.dumps({
                'type': 'typing',
                'message': 'Budul AI is thinking...'
            }))
            
            try:
                # Get Islamic response
                islamic_response = await service.chat(
                    message=message,
                    user_id=user_id,
                    session_id=session_id,
                    context=context
                )
                
                # Send response
                response_data = {
                    'type': 'response',
                    'response_id': islamic_response.response_id,
                    'message': message,
                    'response_text': islamic_response.response_text,
                    'confidence_score': islamic_response.confidence_score,
                    'authenticity_score': islamic_response.authenticity_score,
                    'citations': islamic_response.citations,
                    'sources': islamic_response.sources,
                    'related_topics': islamic_response.related_topics,
                    'requires_scholar_review': islamic_response.requires_scholar_review,
                    'content_warnings': islamic_response.content_warnings,
                    'prayer_times': islamic_response.prayer_times,
                    'qibla_direction': islamic_response.qibla_direction,
                    'generated_at': islamic_response.generated_at.isoformat()
                }
                
                await websocket.send_text(json.dumps(response_data))
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': f'Error processing message: {str(e)}'
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(user_id, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(user_id, session_id)

@router.get("/history/{session_id}", response_model=ConversationHistory)
@rate_limit(calls=100, period=60)
async def get_conversation_history(
    session_id: str = Path(...),
    user_id: str = Depends(get_current_user_optional),
    limit: int = Query(20, ge=1, le=100),
    service: IslamicGPTService = Depends(get_islamic_gpt_service)
) -> ConversationHistory:
    """
    Get conversation history for a session
    
    Retrieve the chat history for analysis and context.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required for history access")
    
    try:
        # Get conversation context
        context_key = f"{user_id}:{session_id}"
        
        if context_key in service.active_conversations:
            context = service.active_conversations[context_key]
            
            return ConversationHistory(
                session_id=session_id,
                user_id=user_id,
                messages=context.conversation_history[-limit:],
                created_at=context.created_at,
                last_activity=context.last_activity,
                total_messages=len(context.conversation_history)
            )
        else:
            # Try to load from cache/database
            raise HTTPException(status_code=404, detail="Conversation not found")
            
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation history")

@router.post("/preferences")
@rate_limit(calls=10, period=60)
async def update_user_preferences(
    preferences: UserPreferences,
    user_id: str = Depends(get_current_user_optional),
    service: IslamicGPTService = Depends(get_islamic_gpt_service)
):
    """
    Update user preferences for Islamic content
    
    Customize the AI responses based on user's Islamic knowledge level,
    madhab preference, and other settings.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Update preferences in service
        # This would typically save to database
        logger.info(f"Updated preferences for user {user_id}: {preferences}")
        
        return {"message": "Preferences updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Error updating preferences")

@router.get("/topics", response_model=List[str])
async def get_islamic_topics():
    """
    Get available Islamic topics for conversation
    
    Returns list of Islamic topics that the AI can discuss.
    """
    return [topic.value for topic in IslamicTopic]

@router.get("/madhabs", response_model=List[str])
async def get_available_madhabs():
    """
    Get available Islamic schools of thought (madhabs)
    
    Returns list of supported madhabs for personalized responses.
    """
    return ["hanafi", "maliki", "shafii", "hanbali", "jafari", "general"]

@router.get("/health")
async def chat_health_check(
    service: IslamicGPTService = Depends(get_islamic_gpt_service)
):
    """
    Health check for Islamic chat service
    
    Returns service status and performance metrics.
    """
    try:
        # Basic health check
        active_connections = len(manager.active_connections)
        
        return {
            "status": "healthy",
            "service": "Islamic GPT Chat",
            "active_websocket_connections": active_connections,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Background tasks
async def log_chat_interaction(
    user_id: str,
    message: str,
    response: IslamicResponse,
    processing_time: float
):
    """Log chat interaction for analytics"""
    try:
        interaction_data = {
            "user_id": user_id,
            "message": message,
            "response_id": response.response_id,
            "authenticity_score": response.authenticity_score,
            "confidence_score": response.confidence_score,
            "processing_time_ms": processing_time,
            "requires_scholar_review": response.requires_scholar_review,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # This would save to analytics database
        logger.info(f"Chat interaction logged: {interaction_data}")
        
    except Exception as e:
        logger.error(f"Error logging chat interaction: {e}")

# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return HTTPException(status_code=400, detail=str(exc))

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")
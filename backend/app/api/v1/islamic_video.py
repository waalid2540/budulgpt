"""
Islamic Video Generation API
Comprehensive API for Islamic video creation with templates and customization
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import (
    APIRouter, BackgroundTasks, Depends, HTTPException, 
    UploadFile, File, Form, Query, Path
)
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

# Video generation services
from ...video_generation.islamic_video_generator import (
    IslamicVideoGenerator, VideoRequest, VideoGenerationConfig,
    VideoStyle, VideoFormat, AudioStyle
)
from ...core.auth import get_current_user_optional
from ...core.rate_limiting import rate_limit
from ...db.database import get_db

# Monitoring
import structlog
from prometheus_client import Counter, Histogram

# Models
class VideoGenerationRequest(BaseModel):
    """Video generation request model"""
    text_content: str = Field(..., min_length=10, max_length=5000, description="Content for video")
    title: Optional[str] = Field(None, max_length=200, description="Video title")
    duration_seconds: float = Field(30.0, ge=5.0, le=300.0, description="Video duration")
    style: VideoStyle = Field(VideoStyle.MODERN, description="Visual style")
    format: VideoFormat = Field(VideoFormat.LANDSCAPE, description="Video format")
    audio_style: AudioStyle = Field(AudioStyle.AMBIENT, description="Audio style")
    
    # Islamic customization
    include_arabic_text: bool = Field(True, description="Include Arabic text")
    include_english_text: bool = Field(True, description="Include English text")
    include_citations: bool = Field(True, description="Include Islamic citations")
    madhab_specific: bool = Field(False, description="Use specific madhab")
    preferred_madhab: str = Field("general", description="Preferred Islamic school")
    cultural_style: str = Field("general", description="Cultural style preference")
    
    # Technical settings
    resolution: str = Field("1080p", description="Video resolution")
    quality: str = Field("high", description="Video quality")
    include_subtitles: bool = Field(True, description="Include subtitles")
    
    class Config:
        schema_extra = {
            "example": {
                "text_content": "Explain the importance of the five daily prayers in Islam",
                "title": "The Five Daily Prayers",
                "duration_seconds": 60.0,
                "style": "modern",
                "format": "landscape",
                "audio_style": "ambient",
                "include_arabic_text": True,
                "include_english_text": True,
                "include_citations": True,
                "madhab_specific": False,
                "preferred_madhab": "general",
                "cultural_style": "general",
                "resolution": "1080p",
                "quality": "high",
                "include_subtitles": True
            }
        }

class VideoGenerationResponse(BaseModel):
    """Video generation response model"""
    request_id: str
    status: str  # queued, processing, completed, failed
    progress: int = 0
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    
class VideoTemplate(BaseModel):
    """Video template model"""
    template_id: str
    name: str
    description: str
    category: str
    preview_url: str
    duration_seconds: float
    style: VideoStyle
    format: VideoFormat
    islamic_topic: str
    difficulty_level: str
    
class VideoLibraryItem(BaseModel):
    """Video library item model"""
    video_id: str
    title: str
    description: str
    thumbnail_url: str
    video_url: str
    duration_seconds: float
    views: int
    created_at: datetime
    islamic_topic: str
    style: VideoStyle
    
# Router setup
router = APIRouter(prefix="/video", tags=["Islamic Video Generation"])
logger = structlog.get_logger(__name__)

# Metrics
video_requests_counter = Counter('islamic_video_api_requests_total', 'Total video API requests')
generation_queue_gauge = Counter('islamic_video_queue_size', 'Video generation queue size')

# Global service instance
video_generator: Optional[IslamicVideoGenerator] = None

async def get_video_generator() -> IslamicVideoGenerator:
    """Get or initialize video generator service"""
    global video_generator
    
    if video_generator is None:
        video_generator = IslamicVideoGenerator()
        await video_generator.initialize()
    
    return video_generator

@router.post("/generate", response_model=VideoGenerationResponse)
@rate_limit(calls=10, period=3600)  # 10 video generations per hour
async def generate_islamic_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_optional),
    generator: IslamicVideoGenerator = Depends(get_video_generator),
    db: AsyncSession = Depends(get_db)
) -> VideoGenerationResponse:
    """
    Generate Islamic video from text content
    
    Creates a professional Islamic video with Arabic calligraphy, geometric patterns,
    appropriate audio, and scholarly citations.
    """
    video_requests_counter.inc()
    
    try:
        # Default user ID for anonymous users
        if not user_id:
            user_id = f"anonymous_{uuid4().hex[:8]}"
        
        # Convert resolution string to tuple
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160)
        }
        resolution = resolution_map.get(request.resolution, (1920, 1080))
        
        # Create video generation config
        config = VideoGenerationConfig(
            resolution=resolution,
            duration_seconds=request.duration_seconds,
            format=request.format,
            style=request.style,
            include_arabic_text=request.include_arabic_text,
            include_english_text=request.include_english_text,
            include_citations=request.include_citations,
            audio_style=request.audio_style,
            madhab_specific=request.madhab_specific,
            preferred_madhab=request.preferred_madhab,
            cultural_style=request.cultural_style,
            quality=request.quality,
            include_subtitles=request.include_subtitles
        )
        
        # Create video request
        video_request = VideoRequest(
            text_content=request.text_content,
            title=request.title,
            config=config,
            user_id=user_id
        )
        
        # Start video generation in background
        background_tasks.add_task(
            generate_video_background,
            generator, video_request
        )
        
        # Return immediate response
        return VideoGenerationResponse(
            request_id=video_request.request_id,
            status="queued",
            progress=0,
            created_at=datetime.utcnow(),
            estimated_completion=datetime.utcnow().replace(
                minute=datetime.utcnow().minute + int(request.duration_seconds / 10)
            )
        )
        
    except Exception as e:
        logger.error(f"Error in video generation request: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation error: {str(e)}")

@router.get("/status/{request_id}", response_model=VideoGenerationResponse)
async def get_video_generation_status(
    request_id: str = Path(...),
    generator: IslamicVideoGenerator = Depends(get_video_generator)
) -> VideoGenerationResponse:
    """
    Get status of video generation request
    
    Check the progress and status of an ongoing video generation.
    """
    try:
        # Check if request is in active generations
        if request_id in generator.active_generations:
            generation_info = generator.active_generations[request_id]
            
            return VideoGenerationResponse(
                request_id=request_id,
                status=generation_info["status"],
                progress=generation_info["progress"],
                created_at=generation_info["started_at"],
                error_message=generation_info.get("error")
            )
        
        # Check Redis cache for completed generations
        cached_result = await generator.redis_client.get(f"video_result:{request_id}")
        if cached_result:
            result_data = json.loads(cached_result)
            return VideoGenerationResponse(**result_data)
        
        # Request not found
        raise HTTPException(status_code=404, detail="Video generation request not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking video status: {e}")
        raise HTTPException(status_code=500, detail="Error checking video status")

@router.get("/download/{request_id}")
async def download_generated_video(
    request_id: str = Path(...),
    generator: IslamicVideoGenerator = Depends(get_video_generator)
):
    """
    Download generated video file
    
    Download the completed Islamic video file.
    """
    try:
        # Check if video is completed
        cached_result = await generator.redis_client.get(f"video_result:{request_id}")
        if not cached_result:
            raise HTTPException(status_code=404, detail="Video not found or not completed")
        
        result_data = json.loads(cached_result)
        
        if result_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="Video generation not completed")
        
        video_path = result_data.get("video_path")
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Return video file
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"islamic_video_{request_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail="Error downloading video")

@router.get("/templates", response_model=List[VideoTemplate])
async def get_video_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    islamic_topic: Optional[str] = Query(None, description="Filter by Islamic topic"),
    style: Optional[VideoStyle] = Query(None, description="Filter by style"),
    limit: int = Query(20, ge=1, le=100, description="Number of templates to return")
) -> List[VideoTemplate]:
    """
    Get available Islamic video templates
    
    Browse pre-designed templates for different Islamic topics and styles.
    """
    try:
        # This would fetch from database in production
        templates = [
            VideoTemplate(
                template_id="prayer_importance",
                name="Importance of Prayer",
                description="Template explaining the significance of daily prayers in Islam",
                category="worship",
                preview_url="/static/templates/prayer_importance_preview.jpg",
                duration_seconds=60.0,
                style=VideoStyle.MODERN,
                format=VideoFormat.LANDSCAPE,
                islamic_topic="prayer",
                difficulty_level="beginner"
            ),
            VideoTemplate(
                template_id="quran_recitation",
                name="Quran Recitation",
                description="Beautiful Quran recitation with Arabic calligraphy",
                category="quran",
                preview_url="/static/templates/quran_recitation_preview.jpg",
                duration_seconds=120.0,
                style=VideoStyle.CALLIGRAPHY_FOCUS,
                format=VideoFormat.LANDSCAPE,
                islamic_topic="quran",
                difficulty_level="intermediate"
            ),
            VideoTemplate(
                template_id="islamic_architecture",
                name="Islamic Architecture",
                description="Showcase of beautiful Islamic architectural elements",
                category="culture",
                preview_url="/static/templates/architecture_preview.jpg",
                duration_seconds=90.0,
                style=VideoStyle.ARCHITECTURE,
                format=VideoFormat.LANDSCAPE,
                islamic_topic="history",
                difficulty_level="advanced"
            )
        ]
        
        # Apply filters
        if category:
            templates = [t for t in templates if t.category == category]
        if islamic_topic:
            templates = [t for t in templates if t.islamic_topic == islamic_topic]
        if style:
            templates = [t for t in templates if t.style == style]
        
        return templates[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail="Error fetching templates")

@router.post("/generate-from-template")
@rate_limit(calls=15, period=3600)  # 15 template-based generations per hour
async def generate_video_from_template(
    template_id: str = Form(...),
    custom_text: Optional[str] = Form(None),
    duration_override: Optional[float] = Form(None),
    background_tasks: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_optional),
    generator: IslamicVideoGenerator = Depends(get_video_generator)
) -> VideoGenerationResponse:
    """
    Generate video from Islamic template
    
    Use a pre-designed template with optional customizations.
    """
    try:
        # Load template configuration
        template_config = await load_template_config(template_id)
        if not template_config:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Apply customizations
        if custom_text:
            template_config["text_content"] = custom_text
        if duration_override:
            template_config["duration_seconds"] = duration_override
        
        # Create video request from template
        video_request = VideoRequest(
            text_content=template_config["text_content"],
            title=template_config.get("title"),
            config=VideoGenerationConfig(**template_config["config"]),
            user_id=user_id or f"anonymous_{uuid4().hex[:8]}"
        )
        
        # Start generation
        background_tasks.add_task(
            generate_video_background,
            generator, video_request
        )
        
        return VideoGenerationResponse(
            request_id=video_request.request_id,
            status="queued",
            progress=0,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating from template: {e}")
        raise HTTPException(status_code=500, detail="Error generating from template")

@router.get("/library", response_model=List[VideoLibraryItem])
async def get_video_library(
    islamic_topic: Optional[str] = Query(None),
    style: Optional[VideoStyle] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[VideoLibraryItem]:
    """
    Browse Islamic video library
    
    Discover existing Islamic videos for inspiration and reference.
    """
    try:
        # This would fetch from database in production
        library_items = []
        
        # Apply filters and pagination
        # Implementation would query actual database
        
        return library_items
        
    except Exception as e:
        logger.error(f"Error fetching video library: {e}")
        raise HTTPException(status_code=500, detail="Error fetching video library")

@router.delete("/cancel/{request_id}")
async def cancel_video_generation(
    request_id: str = Path(...),
    user_id: str = Depends(get_current_user_optional),
    generator: IslamicVideoGenerator = Depends(get_video_generator)
):
    """
    Cancel ongoing video generation
    
    Cancel a video generation request that is currently in progress.
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if request exists and belongs to user
        if request_id in generator.active_generations:
            generation_info = generator.active_generations[request_id]
            
            # Mark as cancelled
            generation_info["status"] = "cancelled"
            generation_info["cancelled_at"] = datetime.utcnow()
            
            return {"message": "Video generation cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Generation request not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling video generation: {e}")
        raise HTTPException(status_code=500, detail="Error cancelling generation")

@router.get("/analytics")
async def get_video_analytics(
    user_id: str = Depends(get_current_user_optional),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get video generation analytics
    
    View statistics about video generations and usage.
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # This would query analytics database
        analytics = {
            "total_videos_generated": 0,
            "total_watch_time_minutes": 0,
            "most_popular_topics": [],
            "generation_success_rate": 0.0,
            "average_generation_time_minutes": 0.0
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail="Error fetching analytics")

@router.get("/health")
async def video_service_health():
    """
    Health check for video generation service
    
    Check if the video generation service is operational.
    """
    try:
        return {
            "status": "healthy",
            "service": "Islamic Video Generation",
            "queue_size": 0,  # Would get actual queue size
            "active_generations": 0,  # Would get actual count
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Video service health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Background tasks
async def generate_video_background(
    generator: IslamicVideoGenerator,
    video_request: VideoRequest
):
    """Background task for video generation"""
    try:
        result = await generator.generate_video(video_request)
        
        # Cache result for retrieval
        await generator.redis_client.setex(
            f"video_result:{video_request.request_id}",
            86400,  # 24 hours
            json.dumps(result, default=str)
        )
        
        logger.info(f"Video generation completed: {video_request.request_id}")
        
    except Exception as e:
        logger.error(f"Background video generation failed: {e}")
        
        # Cache error result
        error_result = {
            "request_id": video_request.request_id,
            "status": "failed",
            "error_message": str(e)
        }
        
        await generator.redis_client.setex(
            f"video_result:{video_request.request_id}",
            86400,
            json.dumps(error_result)
        )

async def load_template_config(template_id: str) -> Optional[Dict]:
    """Load template configuration"""
    # This would load from database in production
    templates = {
        "prayer_importance": {
            "text_content": "Prayer is the cornerstone of Islamic worship...",
            "title": "The Importance of Prayer",
            "config": {
                "duration_seconds": 60.0,
                "style": "modern",
                "format": "landscape",
                "include_arabic_text": True,
                "audio_style": "ambient"
            }
        }
    }
    
    return templates.get(template_id)
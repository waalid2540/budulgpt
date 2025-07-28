"""
Islamic GPT Chat System - Comprehensive Islamic conversational AI
Multi-turn conversations with real-time citations and scholarly verification
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

# AI and ML libraries
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TextStreamer, GenerationConfig
)
from sentence_transformers import SentenceTransformer
import numpy as np

# Database and caching
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient

# Islamic processing
from ..processing.arabic_text_processor import IslamicTextProcessor
from ..db.islamic_schema import IslamicContent, IslamicSource
from ..core.islamic_ai_config import settings

# Monitoring and logging
import structlog
from prometheus_client import Counter, Histogram, Gauge
import opentelemetry as otel

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SCHOLAR = "scholar"

class IslamicTopic(str, Enum):
    AQEEDAH = "aqeedah"
    FIQH = "fiqh"
    SEERAH = "seerah"
    QURAN = "quran"
    HADITH = "hadith"
    AKHLAQ = "akhlaq"
    DAWA = "dawa"
    GENERAL = "general"

@dataclass
class ChatContext:
    """Maintains conversation context for Islamic discussions"""
    user_id: str
    session_id: str
    conversation_history: List[Dict] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)
    islamic_knowledge_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    preferred_madhab: str = "general"
    preferred_language: str = "en"
    location: Optional[Dict] = None
    conversation_topic: IslamicTopic = IslamicTopic.GENERAL
    scholar_mode: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

@dataclass
class IslamicResponse:
    """Structured response from Islamic AI"""
    response_text: str
    confidence_score: float
    authenticity_score: float
    citations: List[Dict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    madhab_specific: bool = False
    requires_scholar_review: bool = False
    content_warnings: List[str] = field(default_factory=list)
    prayer_times: Optional[Dict] = None
    qibla_direction: Optional[float] = None
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = field(default_factory=datetime.utcnow)

class IslamicGPTService:
    """
    Comprehensive Islamic GPT service with multi-turn conversations,
    real-time citations, and scholarly verification
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # AI Models
        self.islamic_model = None
        self.tokenizer = None
        self.embedding_model = None
        
        # Text processing
        self.islamic_processor = None
        
        # Database connections
        self.redis_client = None
        self.postgres_session = None
        self.mongodb_client = None
        
        # Active conversations
        self.active_conversations: Dict[str, ChatContext] = {}
        
        # Islamic knowledge bases
        self.quran_verses = {}
        self.hadith_collections = {}
        self.scholarly_opinions = {}
        self.fatwa_database = {}
        
        # Location services
        self.prayer_times_cache = {}
        self.qibla_cache = {}
        
        # Metrics
        self.setup_metrics()
        
        # Content safety
        self.content_filter = None
        self.controversy_detector = None
        
    def setup_metrics(self):
        """Setup monitoring metrics"""
        self.chat_requests_counter = Counter('islamic_gpt_requests_total', 'Total chat requests')
        self.response_time_histogram = Histogram('islamic_gpt_response_time_seconds', 'Response time')
        self.authenticity_gauge = Gauge('islamic_gpt_authenticity_score', 'Average authenticity score')
        self.active_conversations_gauge = Gauge('islamic_gpt_active_conversations', 'Active conversations')
        
    async def initialize(self):
        """Initialize the Islamic GPT service"""
        self.logger.info("Initializing Islamic GPT service")
        
        try:
            # Load AI models
            await self._load_models()
            
            # Setup database connections
            await self._setup_databases()
            
            # Initialize Islamic text processor
            await self._setup_text_processor()
            
            # Load Islamic knowledge bases
            await self._load_knowledge_bases()
            
            # Setup content safety
            await self._setup_content_safety()
            
            self.logger.info("Islamic GPT service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Islamic GPT service: {e}")
            raise
    
    async def _load_models(self):
        """Load Islamic AI models"""
        self.logger.info("Loading Islamic AI models")
        
        # Load main Islamic GPT model
        model_path = settings.islamic_gpt_model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.islamic_model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Load embedding model for semantic search
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        self.logger.info("Islamic AI models loaded successfully")
    
    async def _setup_databases(self):
        """Setup database connections"""
        # Redis for caching and session management
        self.redis_client = redis.from_url(settings.redis_url)
        
        # MongoDB for conversation history
        self.mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        
    async def _setup_text_processor(self):
        """Setup Islamic text processor"""
        from ..processing.arabic_text_processor import ArabicProcessingConfig
        config = ArabicProcessingConfig()
        self.islamic_processor = IslamicTextProcessor(config)
    
    async def _load_knowledge_bases(self):
        """Load Islamic knowledge bases"""
        self.logger.info("Loading Islamic knowledge bases")
        
        # This would load from your databases
        # For now, we'll set up the structure
        self.quran_verses = await self._load_quran_database()
        self.hadith_collections = await self._load_hadith_database()
        self.scholarly_opinions = await self._load_scholarly_database()
        self.fatwa_database = await self._load_fatwa_database()
    
    async def _setup_content_safety(self):
        """Setup content safety and filtering"""
        # Initialize content filters for inappropriate content
        # and controversy detection
        pass
    
    async def chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> IslamicResponse:
        """
        Main chat interface for Islamic conversations
        """
        start_time = time.time()
        self.chat_requests_counter.inc()
        
        try:
            # Get or create conversation context
            chat_context = await self._get_or_create_context(user_id, session_id, context)
            
            # Process the message
            processed_message = await self._process_message(message, chat_context)
            
            # Generate Islamic response
            response = await self._generate_islamic_response(processed_message, chat_context)
            
            # Update conversation history
            await self._update_conversation_history(chat_context, message, response)
            
            # Update metrics
            response_time = time.time() - start_time
            self.response_time_histogram.observe(response_time)
            self.authenticity_gauge.set(response.authenticity_score)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in Islamic chat: {e}")
            return await self._create_error_response(str(e))
    
    async def stream_chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat interface for real-time responses
        """
        try:
            # Get conversation context
            chat_context = await self._get_or_create_context(user_id, session_id, context)
            
            # Process message
            processed_message = await self._process_message(message, chat_context)
            
            # Generate streaming response
            async for chunk in self._generate_streaming_response(processed_message, chat_context):
                yield chunk
                
        except Exception as e:
            self.logger.error(f"Error in streaming chat: {e}")
            yield f"Error: {str(e)}"
    
    async def _get_or_create_context(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> ChatContext:
        """Get existing or create new conversation context"""
        
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if context exists in memory
        context_key = f"{user_id}:{session_id}"
        
        if context_key in self.active_conversations:
            chat_context = self.active_conversations[context_key]
            chat_context.last_activity = datetime.utcnow()
            return chat_context
        
        # Try to load from Redis
        cached_context = await self.redis_client.get(f"chat_context:{context_key}")
        if cached_context:
            context_data = json.loads(cached_context)
            chat_context = ChatContext(**context_data)
        else:
            # Create new context
            chat_context = ChatContext(
                user_id=user_id,
                session_id=session_id
            )
            
            # Load user preferences if provided
            if context:
                chat_context.user_preferences = context.get('preferences', {})
                chat_context.islamic_knowledge_level = DifficultyLevel(
                    context.get('knowledge_level', 'intermediate')
                )
                chat_context.preferred_madhab = context.get('madhab', 'general')
                chat_context.preferred_language = context.get('language', 'en')
                chat_context.location = context.get('location')
        
        # Store in memory and cache
        self.active_conversations[context_key] = chat_context
        await self._cache_context(chat_context)
        
        return chat_context
    
    async def _process_message(self, message: str, context: ChatContext) -> Dict:
        """Process incoming message with Islamic context"""
        
        # Detect language
        language = await self._detect_language(message)
        
        # Process Arabic text if applicable
        if language == 'ar':
            arabic_analysis = await self.islamic_processor.process_islamic_text(message)
        else:
            arabic_analysis = None
        
        # Extract Islamic intent
        intent = await self._extract_islamic_intent(message, context)
        
        # Detect controversial topics
        controversy_flags = await self._detect_controversial_content(message)
        
        # Check for prayer time requests
        prayer_time_request = await self._detect_prayer_time_request(message)
        
        # Check for Qibla direction requests
        qibla_request = await self._detect_qibla_request(message)
        
        return {
            'original_message': message,
            'language': language,
            'arabic_analysis': arabic_analysis,
            'islamic_intent': intent,
            'controversy_flags': controversy_flags,
            'prayer_time_request': prayer_time_request,
            'qibla_request': qibla_request,
            'context': context
        }
    
    async def _generate_islamic_response(
        self,
        processed_message: Dict,
        context: ChatContext
    ) -> IslamicResponse:
        """Generate comprehensive Islamic response"""
        
        message = processed_message['original_message']
        intent = processed_message['islamic_intent']
        
        # Handle special requests first
        if processed_message['prayer_time_request']:
            return await self._handle_prayer_time_request(processed_message, context)
        
        if processed_message['qibla_request']:
            return await self._handle_qibla_request(processed_message, context)
        
        # Build context for generation
        generation_context = await self._build_generation_context(processed_message, context)
        
        # Generate response using Islamic model
        response_text = await self._generate_text_response(generation_context)
        
        # Find relevant citations
        citations = await self._find_citations(message, response_text, intent)
        
        # Verify authenticity
        authenticity_score = await self._calculate_authenticity_score(response_text, citations)
        
        # Calculate confidence
        confidence_score = await self._calculate_confidence_score(response_text, intent)
        
        # Check if scholar review is needed
        requires_review = await self._requires_scholar_review(
            response_text, authenticity_score, processed_message['controversy_flags']
        )
        
        # Extract related topics
        related_topics = await self._extract_related_topics(response_text, intent)
        
        return IslamicResponse(
            response_text=response_text,
            confidence_score=confidence_score,
            authenticity_score=authenticity_score,
            citations=citations,
            sources=[citation['source'] for citation in citations],
            related_topics=related_topics,
            requires_scholar_review=requires_review,
            content_warnings=processed_message['controversy_flags']
        )
    
    async def _build_generation_context(self, processed_message: Dict, context: ChatContext) -> str:
        """Build context for response generation"""
        
        # Start with system prompt
        system_prompt = self._get_islamic_system_prompt(context)
        
        # Add conversation history
        conversation_history = self._format_conversation_history(context.conversation_history)
        
        # Add relevant Islamic knowledge
        relevant_knowledge = await self._retrieve_relevant_knowledge(
            processed_message['original_message'],
            processed_message['islamic_intent']
        )
        
        # Combine context
        full_context = f"{system_prompt}\n\n{conversation_history}\n\n{relevant_knowledge}\n\nHuman: {processed_message['original_message']}\n\nAssistant:"
        
        return full_context
    
    def _get_islamic_system_prompt(self, context: ChatContext) -> str:
        """Get Islamic system prompt based on user context"""
        
        base_prompt = """You are Budul AI, an Islamic artificial intelligence assistant trained on authentic Islamic sources. Your responses must be:

1. Islamically accurate and based on Quran and authentic Hadith
2. Respectful of all Islamic schools of thought (madhabs)
3. Culturally sensitive to global Muslim diversity
4. Backed by proper citations when making Islamic claims
5. Appropriate for the user's knowledge level

When discussing controversial topics, present balanced perspectives and recommend consulting qualified scholars."""

        # Customize based on user preferences
        if context.preferred_madhab != "general":
            base_prompt += f"\n\nThe user follows the {context.preferred_madhab} madhab. When relevant, provide perspective from this school of thought while acknowledging other valid opinions."
        
        if context.islamic_knowledge_level == DifficultyLevel.BEGINNER:
            base_prompt += "\n\nExplain Islamic concepts in simple terms and provide background context."
        elif context.islamic_knowledge_level == DifficultyLevel.ADVANCED:
            base_prompt += "\n\nProvide detailed scholarly analysis with references to classical texts."
        
        return base_prompt
    
    async def _generate_text_response(self, context: str) -> str:
        """Generate text response using Islamic model"""
        
        # Tokenize input
        inputs = self.tokenizer(
            context,
            return_tensors="pt",
            truncation=True,
            max_length=settings.max_context_length - 512  # Leave space for response
        )
        
        # Generation configuration
        generation_config = GenerationConfig(
            max_new_tokens=512,
            temperature=settings.temperature,
            top_p=settings.top_p,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3
        )
        
        # Generate response
        with torch.no_grad():
            outputs = self.islamic_model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                generation_config=generation_config
            )
        
        # Decode response
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        # Clean up response
        response = self._clean_generated_response(response)
        
        return response
    
    def _clean_generated_response(self, response: str) -> str:
        """Clean and format generated response"""
        
        # Remove common generation artifacts
        response = re.sub(r'\n+', '\n', response)
        response = response.strip()
        
        # Ensure proper Islamic etiquette
        if not response.startswith(('Bismillah', 'بسم الله', 'Assalamu alaikum')):
            if 'allah' in response.lower() or 'الله' in response:
                # Add appropriate Islamic greeting for religious content
                response = f"Bismillah (In the name of Allah),\n\n{response}"
        
        return response
    
    async def _find_citations(self, question: str, response: str, intent: Dict) -> List[Dict]:
        """Find relevant Islamic citations for the response"""
        
        citations = []
        
        # Search for Quran verses
        quran_citations = await self._search_quran_citations(question, response)
        citations.extend(quran_citations)
        
        # Search for Hadith
        hadith_citations = await self._search_hadith_citations(question, response)
        citations.extend(hadith_citations)
        
        # Search for scholarly opinions
        scholarly_citations = await self._search_scholarly_citations(question, response)
        citations.extend(scholarly_citations)
        
        # Rank citations by relevance
        ranked_citations = await self._rank_citations(citations, question, response)
        
        return ranked_citations[:5]  # Return top 5 citations
    
    async def _search_quran_citations(self, question: str, response: str) -> List[Dict]:
        """Search for relevant Quran verses"""
        # This would use your Quran database and semantic search
        # Placeholder implementation
        return []
    
    async def _search_hadith_citations(self, question: str, response: str) -> List[Dict]:
        """Search for relevant Hadith"""
        # This would use your Hadith database and semantic search
        # Placeholder implementation
        return []
    
    async def _search_scholarly_citations(self, question: str, response: str) -> List[Dict]:
        """Search for relevant scholarly opinions"""
        # This would use your scholarly works database
        # Placeholder implementation
        return []
    
    async def _rank_citations(self, citations: List[Dict], question: str, response: str) -> List[Dict]:
        """Rank citations by relevance"""
        # Use semantic similarity to rank citations
        # Placeholder implementation
        return citations
    
    async def _calculate_authenticity_score(self, response: str, citations: List[Dict]) -> float:
        """Calculate Islamic authenticity score"""
        
        base_score = 0.7  # Base score
        
        # Boost score for citations
        if citations:
            citation_boost = min(0.2, len(citations) * 0.05)
            base_score += citation_boost
        
        # Check for Islamic terminology usage
        islamic_terms = self._count_islamic_terms(response)
        if islamic_terms > 0:
            base_score += min(0.1, islamic_terms * 0.02)
        
        # Placeholder: In production, this would use ML models
        # trained on scholarly verification
        
        return min(1.0, base_score)
    
    def _count_islamic_terms(self, text: str) -> int:
        """Count Islamic terminology in text"""
        islamic_terms = [
            'Allah', 'الله', 'Prophet', 'Muhammad', 'محمد',
            'Quran', 'قرآن', 'Hadith', 'حديث', 'Sunnah',
            'Islam', 'إسلام', 'Muslim', 'مسلم'
        ]
        
        return sum(1 for term in islamic_terms if term.lower() in text.lower())
    
    async def _calculate_confidence_score(self, response: str, intent: Dict) -> float:
        """Calculate confidence in response accuracy"""
        # Placeholder: Would use model uncertainty estimation
        return 0.85
    
    async def _requires_scholar_review(
        self,
        response: str,
        authenticity_score: float,
        controversy_flags: List[str]
    ) -> bool:
        """Determine if response requires scholar review"""
        
        if authenticity_score < 0.8:
            return True
        
        if controversy_flags:
            return True
        
        # Check for complex fiqh topics
        complex_topics = ['divorce', 'inheritance', 'business', 'marriage']
        if any(topic in response.lower() for topic in complex_topics):
            return True
        
        return False
    
    # Additional methods for prayer times, Qibla direction, etc.
    async def _handle_prayer_time_request(self, processed_message: Dict, context: ChatContext) -> IslamicResponse:
        """Handle prayer time requests"""
        if not context.location:
            return IslamicResponse(
                response_text="To provide accurate prayer times, I need your location. Please share your city or coordinates.",
                confidence_score=1.0,
                authenticity_score=1.0
            )
        
        prayer_times = await self._get_prayer_times(context.location)
        
        response_text = self._format_prayer_times_response(prayer_times, context.location)
        
        return IslamicResponse(
            response_text=response_text,
            confidence_score=1.0,
            authenticity_score=1.0,
            prayer_times=prayer_times
        )
    
    async def _handle_qibla_request(self, processed_message: Dict, context: ChatContext) -> IslamicResponse:
        """Handle Qibla direction requests"""
        if not context.location:
            return IslamicResponse(
                response_text="To provide the Qibla direction, I need your location. Please share your city or coordinates.",
                confidence_score=1.0,
                authenticity_score=1.0
            )
        
        qibla_direction = await self._get_qibla_direction(context.location)
        
        response_text = f"The Qibla direction from your location is {qibla_direction:.1f}° from North."
        
        return IslamicResponse(
            response_text=response_text,
            confidence_score=1.0,
            authenticity_score=1.0,
            qibla_direction=qibla_direction
        )
    
    # Placeholder methods for external services
    async def _get_prayer_times(self, location: Dict) -> Dict:
        """Get prayer times for location"""
        # This would integrate with Islamic prayer time APIs
        return {
            "fajr": "05:30",
            "dhuhr": "12:15",
            "asr": "15:45",
            "maghrib": "18:20",
            "isha": "19:35"
        }
    
    async def _get_qibla_direction(self, location: Dict) -> float:
        """Calculate Qibla direction"""
        # This would calculate direction to Mecca from user location
        return 45.0  # Placeholder
    
    # Database loading methods (placeholders)
    async def _load_quran_database(self) -> Dict: return {}
    async def _load_hadith_database(self) -> Dict: return {}
    async def _load_scholarly_database(self) -> Dict: return {}
    async def _load_fatwa_database(self) -> Dict: return {}
    
    # Additional utility methods
    async def _detect_language(self, text: str) -> str: return 'en'
    async def _extract_islamic_intent(self, text: str, context: ChatContext) -> Dict: return {}
    async def _detect_controversial_content(self, text: str) -> List[str]: return []
    async def _detect_prayer_time_request(self, text: str) -> bool: return 'prayer' in text.lower()
    async def _detect_qibla_request(self, text: str) -> bool: return 'qibla' in text.lower()
    async def _retrieve_relevant_knowledge(self, question: str, intent: Dict) -> str: return ""
    async def _extract_related_topics(self, response: str, intent: Dict) -> List[str]: return []
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        formatted = ""
        for turn in history[-5:]:  # Last 5 turns
            formatted += f"Human: {turn['message']}\nAssistant: {turn['response']}\n\n"
        return formatted
    
    def _format_prayer_times_response(self, prayer_times: Dict, location: Dict) -> str:
        return f"Prayer times for today:\nFajr: {prayer_times['fajr']}\nDhuhr: {prayer_times['dhuhr']}\nAsr: {prayer_times['asr']}\nMaghrib: {prayer_times['maghrib']}\nIsha: {prayer_times['isha']}"
    
    async def _cache_context(self, context: ChatContext):
        """Cache conversation context"""
        context_data = {
            'user_id': context.user_id,
            'session_id': context.session_id,
            'user_preferences': context.user_preferences,
            'islamic_knowledge_level': context.islamic_knowledge_level.value,
            'preferred_madhab': context.preferred_madhab,
            'preferred_language': context.preferred_language,
            'location': context.location,
            'conversation_topic': context.conversation_topic.value,
            'last_activity': context.last_activity.isoformat()
        }
        
        context_key = f"chat_context:{context.user_id}:{context.session_id}"
        await self.redis_client.setex(context_key, 3600, json.dumps(context_data))
    
    async def _update_conversation_history(
        self,
        context: ChatContext,
        message: str,
        response: IslamicResponse
    ):
        """Update conversation history"""
        turn = {
            'message': message,
            'response': response.response_text,
            'timestamp': datetime.utcnow().isoformat(),
            'authenticity_score': response.authenticity_score,
            'citations': response.citations
        }
        
        context.conversation_history.append(turn)
        
        # Keep only last 20 turns
        if len(context.conversation_history) > 20:
            context.conversation_history = context.conversation_history[-20:]
        
        # Update cache
        await self._cache_context(context)
    
    async def _create_error_response(self, error_message: str) -> IslamicResponse:
        """Create error response"""
        return IslamicResponse(
            response_text=f"I apologize, but I encountered an error: {error_message}. Please try again.",
            confidence_score=0.0,
            authenticity_score=0.0,
            requires_scholar_review=True
        )
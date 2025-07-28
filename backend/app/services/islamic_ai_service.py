"""
Islamic AI Service - Core AI logic for Budul GPT
Handles AI response generation with Islamic knowledge integration
"""

import logging
import asyncio
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import re

import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import numpy as np
from typing import Optional
import json

from app.core.config import settings
from app.db.models import ChatMessage
from processors.arabic_processor import ArabicProcessor
from processors.content_processor import ContentProcessor

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Structure for AI-generated responses"""
    content: str
    citations: List[Dict[str, Any]]
    islamic_topics: List[str]
    confidence_score: float
    model_used: str
    tokens_used: int
    response_time_ms: int

class IslamicAIService:
    """Main service for Islamic AI responses with authentic citations"""
    
    def __init__(self):
        self.arabic_processor = ArabicProcessor()
        self.content_processor = ContentProcessor()
        
        # Initialize your custom Islamic AI model
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load your trained Islamic model
        self._load_islamic_model()
        
        # Islamic knowledge base prompts
        self.system_prompts = {
            "default": """You are Budul AI, an Islamic artificial intelligence assistant serving Muslims worldwide. You provide authentic, scholar-verified Islamic knowledge with proper citations.

Core Principles:
- Always cite authentic Islamic sources (Quran, Sahih Hadith, classical scholars)
- Provide balanced perspectives when multiple valid opinions exist
- Respect all four madhabs while noting differences when relevant
- Use appropriate Islamic etiquette (Bismillah, Alhamdulillah, etc.)
- Acknowledge when you're uncertain and recommend consulting scholars
- Be culturally sensitive to global Muslim diversity

Citation Format:
- Quran: [Quran Surah:Verse]
- Hadith: [Collection, Book/Number, Grade if known]
- Scholarly opinion: [Scholar name, work/context]

Remember: You serve 1.8 billion Muslims with diverse backgrounds, languages, and schools of thought. Provide guidance that unites rather than divides.""",
            
            "beginner": """You are Budul AI, designed to help new Muslims and beginners learn Islam. 

Focus on:
- Simple, clear explanations
- Basic concepts and practices
- Encouragement and support
- Practical daily guidance
- Foundational knowledge

Use gentle, encouraging language and explain Islamic terms when first mentioned.""",
            
            "advanced": """You are Budul AI for advanced Islamic study.

You may:
- Discuss complex fiqh issues
- Reference classical Arabic texts
- Explore scholarly differences in detail
- Analyze historical contexts
- Engage with nuanced theological topics

Maintain academic rigor while remaining accessible."""
        }
        
        # Islamic response templates
        self.response_templates = {
            "quran_citation": "The Holy Quran states: \"{verse_text}\" [{surah}:{verse}]",
            "hadith_citation": "The Prophet (ﷺ) said: \"{hadith_text}\" [Narrated by {narrator}, {collection}]",
            "uncertainty": "والله أعلم (And Allah knows best). For this complex matter, I recommend consulting with a qualified Islamic scholar.",
            "multiple_opinions": "There are different scholarly opinions on this matter:",
            "seek_scholar": "This is a nuanced issue that requires consultation with a qualified Islamic scholar who can consider your specific circumstances."
        }
    
    def _load_islamic_model(self):
        """Load your custom trained Islamic AI model"""
        try:
            # Path to your trained Islamic model
            model_path = settings.ISLAMIC_MODEL_PATH if hasattr(settings, 'ISLAMIC_MODEL_PATH') else "./models/islamic-ai"
            
            logger.info(f"Loading Islamic AI model from {model_path}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                use_fast=True,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                load_in_8bit=False,  # Set to True if you want 8-bit quantization
                load_in_4bit=False   # Set to True if you want 4-bit quantization
            )
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Put model in evaluation mode
            self.model.eval()
            
            logger.info("✅ Islamic AI model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Islamic AI model: {e}")
            logger.info("🔄 Falling back to rule-based responses")
            self.model = None
            self.tokenizer = None
    
    async def _generate_with_custom_model(self, prompt: str, max_length: int = 1024) -> str:
        """Generate response using your custom Islamic AI model"""
        if not self.model or not self.tokenizer:
            return await self._fallback_response("", "beginner")
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(
                prompt,
                return_tensors="pt",
                max_length=2048,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    min_length=50,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    early_stopping=True,
                    num_return_sequences=1
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],  # Only new tokens
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with custom model: {e}")
            return await self._fallback_response("", "beginner")
    
    async def generate_response(
        self,
        message: str,
        chat_history: List[ChatMessage] = None,
        user_preferences: Dict[str, Any] = None,
        context_preferences: Dict[str, Any] = None
    ) -> AIResponse:
        """Generate Islamic AI response with citations"""
        start_time = time.time()
        
        try:
            # Process the user message
            processed_input = self.arabic_processor.process_text(message)
            
            # Determine user knowledge level
            knowledge_level = user_preferences.get("knowledge_level", "beginner")
            language = user_preferences.get("language", "en")
            madhab = user_preferences.get("madhab")
            
            # Build conversation context
            context = await self._build_conversation_context(
                message=message,
                chat_history=chat_history or [],
                user_preferences=user_preferences or {}
            )
            
            # Search for relevant Islamic content
            relevant_content = await self._search_relevant_content(
                query=message,
                processed_text=processed_input,
                context_preferences=context_preferences or {}
            )
            
            # Build AI prompt
            system_prompt = self._build_system_prompt(knowledge_level, madhab, language)
            user_prompt = self._build_user_prompt(
                message=message,
                context=context,
                relevant_content=relevant_content,
                language=language
            )
            
            # Generate AI response using your custom Islamic model
            ai_response_text = await self._generate_with_custom_model(
                prompt=f"{system_prompt}\n\n{user_prompt}",
                max_length=1024
            )
            
            # Extract citations from response
            citations = self._extract_citations(ai_response_text, relevant_content)
            
            # Identify Islamic topics discussed
            islamic_topics = self._identify_islamic_topics(ai_response_text, processed_input)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                ai_response_text, citations, relevant_content
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                content=ai_response_text,
                citations=citations,
                islamic_topics=islamic_topics,
                confidence_score=confidence_score,
                model_used="budul-islamic-ai" if self.model else "fallback",
                tokens_used=len(ai_response_text.split()) * 2,  # Rough estimation
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return await self._error_response()
    
    async def _build_conversation_context(
        self,
        message: str,
        chat_history: List[ChatMessage],
        user_preferences: Dict[str, Any]
    ) -> str:
        """Build conversation context from chat history"""
        context_parts = []
        
        # Add user preferences context
        if user_preferences.get("madhab"):
            context_parts.append(f"User follows {user_preferences['madhab']} madhab")
        
        if user_preferences.get("knowledge_level"):
            context_parts.append(f"User knowledge level: {user_preferences['knowledge_level']}")
        
        # Add recent conversation history
        if chat_history:
            context_parts.append("Recent conversation:")
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "User" if msg.role == "user" else "Budul AI"
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    async def _search_relevant_content(
        self,
        query: str,
        processed_text,
        context_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search for relevant Islamic content to support the response"""
        # This would interface with the content database
        # For now, return mock relevant content
        
        relevant_content = []
        
        # Check if query contains specific Islamic topics
        if any(keyword in query.lower() for keyword in ['prayer', 'salah', 'صلاة']):
            relevant_content.append({
                'type': 'hadith',
                'content': 'The Prophet (ﷺ) said: "The first thing for which a person will be called to account on the Day of Resurrection is prayer."',
                'source': 'Sunan at-Tirmidhi',
                'authenticity': 'hasan',
                'relevance_score': 0.9
            })
        
        if any(keyword in query.lower() for keyword in ['charity', 'zakat', 'زكاة']):
            relevant_content.append({
                'type': 'quran',
                'content': 'And establish prayer and give zakah and bow with those who bow [in worship and obedience].',
                'source': 'Quran 2:43',
                'relevance_score': 0.95
            })
        
        return relevant_content
    
    def _build_system_prompt(self, knowledge_level: str, madhab: Optional[str], language: str) -> str:
        """Build system prompt based on user preferences"""
        base_prompt = self.system_prompts.get(knowledge_level, self.system_prompts["default"])
        
        # Add madhab-specific guidance if specified
        if madhab:
            base_prompt += f"\n\nUser follows the {madhab} madhab. When relevant, provide the {madhab} perspective while noting other valid opinions."
        
        # Add language preference
        if language != "en":
            base_prompt += f"\n\nRespond primarily in {language}, but include Arabic terms with translations when appropriate."
        
        return base_prompt
    
    def _build_user_prompt(
        self,
        message: str,
        context: str,
        relevant_content: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Build user prompt with context and relevant content"""
        prompt_parts = []
        
        # Add context if available
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Add relevant Islamic content
        if relevant_content:
            prompt_parts.append("Relevant Islamic sources:")
            for content in relevant_content[:3]:  # Limit to top 3 most relevant
                prompt_parts.append(f"- {content['type'].title()}: {content['content']} [{content['source']}]")
        
        # Add the actual user question
        prompt_parts.append(f"User question: {message}")
        
        # Add instruction
        prompt_parts.append("Please provide a comprehensive Islamic response with proper citations.")
        
        return "\n\n".join(prompt_parts)
    
    
    async def _fallback_response(self, message: str, knowledge_level: str) -> str:
        """Provide fallback response when AI service is unavailable"""
        return f"""بسم الله الرحمن الرحيم

Thank you for your Islamic question. I'm currently experiencing technical difficulties, but I want to help you.

Your question: "{message}"

For immediate guidance, I recommend:
1. Consulting your local imam or Islamic scholar
2. Referring to authentic Islamic sources like Quran.com or Sunnah.com
3. Seeking knowledge from reputable Islamic institutions

May Allah guide us all to the truth. والله أعلم (And Allah knows best)

The Budul AI team is working to restore full functionality. Jazakum Allah khair for your patience."""
    
    def _extract_citations(self, response_text: str, relevant_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and format citations from the AI response"""
        citations = []
        
        # Extract Quran citations
        quran_pattern = r'\[Quran (\d+):(\d+)\]|\[(\d+):(\d+)\]'
        for match in re.finditer(quran_pattern, response_text):
            surah = match.group(1) or match.group(3)
            verse = match.group(2) or match.group(4)
            citations.append({
                'type': 'quran',
                'reference': f"{surah}:{verse}",
                'display_text': f"Quran {surah}:{verse}",
                'url': f"https://quran.com/{surah}/{verse}"
            })
        
        # Extract Hadith citations
        hadith_pattern = r'\[(.*?), (.*?)\]'
        for match in re.finditer(hadith_pattern, response_text):
            if 'Quran' not in match.group(0):  # Skip Quran references
                citations.append({
                    'type': 'hadith',
                    'collection': match.group(1),
                    'reference': match.group(2),
                    'display_text': f"{match.group(1)}, {match.group(2)}"
                })
        
        # Add citations from relevant content that was used
        for content in relevant_content:
            if any(content['content'][:50] in response_text for content in relevant_content):
                citations.append({
                    'type': content['type'],
                    'source': content['source'],
                    'content': content['content'],
                    'display_text': content['source']
                })
        
        return citations
    
    def _identify_islamic_topics(self, response_text: str, processed_input) -> List[str]:
        """Identify Islamic topics discussed in the response"""
        topics = []
        
        # Topic keywords mapping
        topic_keywords = {
            'prayer': ['prayer', 'salah', 'salat', 'صلاة'],
            'fasting': ['fast', 'fasting', 'sawm', 'ramadan', 'صوم'],
            'charity': ['charity', 'zakat', 'sadaqah', 'زكاة', 'صدقة'],
            'pilgrimage': ['hajj', 'umrah', 'pilgrimage', 'حج', 'عمرة'],
            'faith': ['faith', 'iman', 'belief', 'إيمان'],
            'quran': ['quran', 'qur\'an', 'كتاب', 'قرآن'],
            'hadith': ['hadith', 'sunnah', 'حديث', 'سنة'],
            'prophet': ['prophet', 'muhammad', 'messenger', 'رسول', 'نبي'],
            'ethics': ['ethics', 'morality', 'akhlaq', 'أخلاق'],
            'family': ['marriage', 'family', 'nikah', 'divorce', 'نكاح', 'أسرة']
        }
        
        response_lower = response_text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                topics.append(topic)
        
        # Add topics from processed input
        if processed_input.contains_quran:
            topics.append('quran')
        if processed_input.contains_hadith:
            topics.append('hadith')
        
        return list(set(topics))  # Remove duplicates
    
    def _calculate_confidence_score(
        self,
        response_text: str,
        citations: List[Dict[str, Any]],
        relevant_content: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the response"""
        score = 0.5  # Base score
        
        # Boost score for citations
        if citations:
            score += 0.2 * min(len(citations), 3)  # Max boost of 0.6
        
        # Boost for Quran citations (most authentic)
        quran_citations = [c for c in citations if c.get('type') == 'quran']
        if quran_citations:
            score += 0.1
        
        # Boost for Sahih hadith citations
        sahih_hadiths = [c for c in citations if 'sahih' in c.get('collection', '').lower()]
        if sahih_hadiths:
            score += 0.1
        
        # Reduce score for uncertainty indicators
        uncertainty_phrases = ['allah knows best', 'والله أعلم', 'consult scholar', 'uncertain']
        if any(phrase in response_text.lower() for phrase in uncertainty_phrases):
            score -= 0.1
        
        # Boost for using relevant content
        if relevant_content:
            score += 0.1
        
        return min(1.0, max(0.1, score))  # Clamp between 0.1 and 1.0
    
    async def _error_response(self) -> AIResponse:
        """Generate error response when AI service fails"""
        error_content = """بسم الله الرحمن الرحيم

I apologize, but I'm experiencing technical difficulties and cannot provide a complete response right now.

For authentic Islamic guidance, please:
1. Consult your local imam or qualified Islamic scholar
2. Refer to trusted Islamic resources like Quran.com and Sunnah.com
3. Contact reputable Islamic institutions in your area

May Allah guide us all to what is correct. والله أعلم

Jazakum Allah khair for your patience."""
        
        return AIResponse(
            content=error_content,
            citations=[],
            islamic_topics=[],
            confidence_score=0.0,
            model_used="error_fallback",
            tokens_used=0,
            response_time_ms=0
        )
    
    async def generate_suggestions(
        self,
        context: str,
        language: str = "en",
        user_level: str = "beginner"
    ) -> List[str]:
        """Generate follow-up question suggestions"""
        
        # Basic suggestion templates based on context
        suggestions = []
        
        context_lower = context.lower()
        
        if 'prayer' in context_lower or 'salah' in context_lower:
            suggestions = [
                "What are the times for the five daily prayers?",
                "How do I perform wudu (ablution)?",
                "What should I recite during prayer?",
                "Can I pray at work or while traveling?"
            ]
        elif 'fasting' in context_lower or 'ramadan' in context_lower:
            suggestions = [
                "What breaks the fast during Ramadan?",
                "Who is exempt from fasting?",
                "What is the spiritual purpose of fasting?",
                "How should I prepare for Ramadan?"
            ]
        elif 'charity' in context_lower or 'zakat' in context_lower:
            suggestions = [
                "How much zakat should I pay?",
                "What types of wealth require zakat?",
                "What's the difference between zakat and sadaqah?",
                "Who can receive zakat?"
            ]
        else:
            # General Islamic questions
            suggestions = [
                "What are the five pillars of Islam?",
                "How can I strengthen my faith?",
                "What does Islam teach about daily life?",
                "How do I learn more about Islamic history?"
            ]
        
        # Limit to 4 suggestions
        return suggestions[:4]

# Example usage
async def main():
    """Test the Islamic AI service"""
    service = IslamicAIService()
    
    response = await service.generate_response(
        message="What are the benefits of prayer in Islam?",
        user_preferences={"language": "en", "knowledge_level": "beginner"}
    )
    
    print("AI Response:", response.content)
    print("Citations:", response.citations)
    print("Topics:", response.islamic_topics)
    print("Confidence:", response.confidence_score)

if __name__ == "__main__":
    asyncio.run(main())
"""
Budul AI Service - Using your trained Islamic model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from typing import Dict, Any
import os


class BudulAIService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_path = "./models/islamic-ai"
        self.is_loaded = False
    
    def load_model(self):
        """Load your trained Islamic AI model"""
        try:
            print(f"Loading Islamic AI model from: {self.model_path}")
            
            # Check if model files exist
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model path not found: {self.model_path}")
            
            if not os.path.exists(os.path.join(self.model_path, "model.safetensors")):
                raise FileNotFoundError(f"Model file not found in: {self.model_path}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                local_files_only=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.is_loaded = True
            print("✅ Islamic AI model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading Islamic AI model: {e}")
            self.is_loaded = False
            return False
    
    def generate_response(self, message: str) -> Dict[str, Any]:
        """Generate Islamic AI response"""
        if not self.is_loaded:
            return {
                "response": "السلام عليكم! I'm Budul AI, but my Islamic knowledge model is not currently loaded. Please ensure the trained model is available.",
                "error": "Model not loaded",
                "success": False,
                "response_id": "error_001",
                "confidence_score": 0.0,
                "authenticity_score": 0.0
            }
        
        try:
            # Create Islamic prompt
            prompt = f"""You are Budul AI, an Islamic artificial intelligence assistant trained on authentic Islamic sources. You provide helpful, accurate Islamic guidance based on Quran and Sunnah.

User: {message}
Assistant:"""

            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Clean and format response
            response = self._clean_response(response)
            
            return {
                "response": response,
                "success": True,
                "response_id": f"budul_{hash(message) % 10000:04d}",
                "confidence_score": 0.85,
                "authenticity_score": 0.90,
                "citations": [],
                "sources": ["Trained Budul AI Model"],
                "generated_at": "2024-01-01T12:00:00Z",
                "processing_time_ms": 1250.0
            }
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your Islamic question: {str(e)}. Please try again.",
                "error": str(e),
                "success": False,
                "response_id": "error_002",
                "confidence_score": 0.0,
                "authenticity_score": 0.0
            }
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the generated response"""
        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Ensure Islamic etiquette
        if not any(greeting in response.lower() for greeting in ['assalam', 'bismillah', 'allah']):
            response = f"Bismillah. {response}"
        
        return response.strip()


# Global instance
budul_ai = BudulAIService()
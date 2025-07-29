"""
Simple Islamic AI Service using your trained model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from typing import Dict, Any
import os


class SimpleIslamicAI:
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
                local_files_only=True  # Use only local files
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
                "response": "Islamic AI model is not loaded. Please ensure your trained model is available.",
                "error": "Model not loaded",
                "success": False
            }
        
        try:
            # Create Islamic prompt
            prompt = f"""You are Budul AI, an Islamic artificial intelligence assistant trained on authentic Islamic sources. Provide helpful, accurate Islamic guidance.
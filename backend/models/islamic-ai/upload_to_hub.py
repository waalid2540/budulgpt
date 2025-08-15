#!/usr/bin/env python3
"""
Upload BudulGPT Enhanced to Hugging Face Hub
Run this script after logging in with: huggingface-cli login
"""

from huggingface_hub import HfApi, upload_folder
import os

def upload_budul_gpt():
    print("🤗 Uploading BudulGPT Enhanced to Hugging Face Hub...")
    
    # Initialize API
    api = HfApi()
    
    # Repository info
    repo_id = "yussufabdi/budul-gpt-enhanced"  # Change to your username
    model_path = "/Users/yussufabdi/budul-ai/backend/models/islamic-ai"
    
    try:
        # Create repository if it doesn't exist
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            exist_ok=True
        )
        print(f"✅ Repository created/verified: {repo_id}")
        
        # Upload model files
        api.upload_folder(
            folder_path=model_path,
            repo_id=repo_id,
            repo_type="model",
            commit_message="Upload BudulGPT Enhanced v2.0 with authentic Islamic dataset"
        )
        
        print(f"🎉 Successfully uploaded BudulGPT Enhanced!")
        print(f"🔗 Model URL: https://huggingface.co/{repo_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    upload_budul_gpt()

"""
Upload BudulGPT Enhanced Model to Hugging Face Hub
Share your authentic Islamic AI chatbot with the world
"""

import json
import os
from pathlib import Path
from datetime import datetime

class HuggingFaceUploader:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.models_dir = self.base_dir.parent / "models" / "islamic-ai"
        self.data_dir = self.base_dir
        
        print("🤗 BudulGPT Hugging Face Upload Preparation")
        print(f"🤖 Models directory: {self.models_dir}")
        
    def check_huggingface_setup(self):
        """Check if Hugging Face CLI is set up"""
        print("🔍 Checking Hugging Face setup...")
        
        try:
            import huggingface_hub
            print(f"✅ Hugging Face Hub installed: v{huggingface_hub.__version__}")
            
            # Check if user is logged in
            from huggingface_hub import whoami
            try:
                user_info = whoami()
                print(f"👤 Logged in as: {user_info['name']}")
                return True
            except:
                print("⚠️ Not logged in to Hugging Face")
                print("💡 Run: huggingface-cli login")
                return False
                
        except ImportError:
            print("❌ Hugging Face Hub not installed")
            print("💡 Run: pip install huggingface_hub")
            return False
    
    def create_model_card(self):
        """Create README.md for the model"""
        print("📝 Creating model card...")
        
        # Load enhancement report
        report_file = self.models_dir / "enhancement_report.json"
        enhancement_info = {}
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                enhancement_info = json.load(f)
        
        model_card = f"""---
language: 
- en
- ar
tags:
- islamic-ai
- chatbot
- conversational
- islamic-qa
- hadith
- quran
- authentic-islamic-knowledge
license: apache-2.0
datasets:
- authentic-islamic-dataset
metrics:
- authenticity_threshold: 0.85
pipeline_tag: conversational
---

# BudulGPT Enhanced - Authentic Islamic AI Chatbot

## Model Description

BudulGPT Enhanced is an Islamic AI chatbot trained on authentic Islamic sources with high authenticity standards. The model provides accurate Islamic guidance based on verified sources from multiple Islamic schools of thought (madhabs).

## Model Details

- **Model Type**: Conversational AI for Islamic Q&A
- **Version**: 2.0 Enhanced
- **Languages**: English, Arabic
- **Enhancement Date**: {enhancement_info.get('enhancement_timestamp', datetime.now().isoformat())}
- **Authenticity Threshold**: 0.85
- **Training Examples**: {enhancement_info.get('enhancements', {}).get('total_training_examples', 'N/A')}

## Features

- ✅ **Authentic Islamic Knowledge**: Based on verified sources
- ✅ **Multi-Madhab Coverage**: Hanafi, Maliki, Shafii, Hanbali
- ✅ **Hadith References**: Includes authentic hadith citations
- ✅ **Quran Integration**: Quranic verses with proper references  
- ✅ **Arabic Support**: Native Arabic text handling
- ✅ **High Authenticity**: 0.85 authenticity threshold

## Madhabs Covered

- **Hanafi**: Predominant in Central Asia, Turkey, India
- **Maliki**: Predominant in North/West Africa
- **Shafii**: Predominant in East Africa, Southeast Asia
- **Hanbali**: Predominant in Saudi Arabia

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model
tokenizer = AutoTokenizer.from_pretrained("yussufabdi/budul-gpt-enhanced")
model = AutoModelForCausalLM.from_pretrained("yussufabdi/budul-gpt-enhanced")

# Ask an Islamic question
question = "What are the five pillars of Islam?"
input_text = f"Human: {{question}}\\nBudulGPT:"
input_ids = tokenizer.encode(input_text, return_tensors='pt')

# Generate response
output = model.generate(
    input_ids,
    max_length=input_ids.shape[1] + 150,
    temperature=0.7,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)
```

## Example Conversations

### Five Pillars of Islam
**Human**: What are the five pillars of Islam?
**BudulGPT**: The five pillars of Islam (أركان الإسلام) are:

1. **Shahada** (الشهادة) - Declaration of Faith
2. **Salah** (الصلاة) - Five daily prayers  
3. **Zakat** (الزكاة) - Obligatory charity
4. **Sawm** (الصوم) - Fasting during Ramadan
5. **Hajj** (الحج) - Pilgrimage to Mecca

These pillars form the foundation of Islamic practice and worship. والله أعلم

### Wudu (Ablution)
**Human**: How do I perform wudu?
**BudulGPT**: Wudu (الوضوء) steps:

1. Make intention (niyyah)
2. Say Bismillah
3. Wash hands 3 times
4. Rinse mouth 3 times
5. Clean nose 3 times
6. Wash face 3 times
7. Wash arms to elbows 3 times
8. Wipe head once
9. Wipe ears once
10. Wash feet to ankles 3 times

The Prophet (ﷺ) said: "Cleanliness is half of faith." [Sahih Muslim]

## Authenticity & Sources

This model is trained on authentic Islamic sources with rigorous verification:

- **Primary Sources**: Quran, Sahih Hadith collections
- **Scholarly Sources**: Ibn Baz Foundation, authenticated Islamic websites
- **Verification Process**: Multi-madhab cross-referencing
- **Quality Control**: 0.85 authenticity threshold

## Limitations

- Responses are for general guidance only
- Complex jurisprudential issues should be referred to qualified scholars
- Model output should be verified with authentic Islamic sources
- Not a replacement for consulting knowledgeable Islamic scholars

## Ethical Considerations

- Trained exclusively on authentic Islamic sources
- Respects Islamic principles and values
- Promotes understanding between different madhabs
- Encourages seeking knowledge from qualified scholars

## License

This model is released under the Apache 2.0 license.

## Citation

```bibtex
@misc{{budulgpt-enhanced-2025,
  title={{BudulGPT Enhanced: Authentic Islamic AI Chatbot}},
  author={{Yussuf Abdi}},
  year={{2025}},
  publisher={{Hugging Face}},
  url={{https://huggingface.co/yussufabdi/budul-gpt-enhanced}}
}}
```

## Contact

For questions or feedback about BudulGPT Enhanced, please reach out through the Hugging Face model page.

---

*"And say: My Lord, increase me in knowledge." - Quran 20:114*

والله أعلم (And Allah knows best)
"""
        
        readme_file = self.models_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(model_card)
        
        print(f"✅ Model card created: {readme_file}")
        return str(readme_file)
    
    def create_upload_script(self):
        """Create upload script"""
        print("🚀 Creating upload script...")
        
        upload_script = f"""#!/usr/bin/env python3
\"\"\"
Upload BudulGPT Enhanced to Hugging Face Hub
Run this script after logging in with: huggingface-cli login
\"\"\"

from huggingface_hub import HfApi, upload_folder
import os

def upload_budul_gpt():
    print("🤗 Uploading BudulGPT Enhanced to Hugging Face Hub...")
    
    # Initialize API
    api = HfApi()
    
    # Repository info
    repo_id = "yussufabdi/budul-gpt-enhanced"  # Change to your username
    model_path = "{str(self.models_dir)}"
    
    try:
        # Create repository if it doesn't exist
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            exist_ok=True
        )
        print(f"✅ Repository created/verified: {{repo_id}}")
        
        # Upload model files
        api.upload_folder(
            folder_path=model_path,
            repo_id=repo_id,
            repo_type="model",
            commit_message="Upload BudulGPT Enhanced v2.0 with authentic Islamic dataset"
        )
        
        print(f"🎉 Successfully uploaded BudulGPT Enhanced!")
        print(f"🔗 Model URL: https://huggingface.co/{{repo_id}}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {{e}}")
        return False

if __name__ == "__main__":
    upload_budul_gpt()
"""
        
        script_file = self.models_dir / "upload_to_hub.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(upload_script)
        
        # Make executable
        os.chmod(script_file, 0o755)
        
        print(f"✅ Upload script created: {script_file}")
        return str(script_file)
    
    def create_deployment_guide(self):
        """Create deployment guide"""
        print("📚 Creating deployment guide...")
        
        guide = f"""# BudulGPT Enhanced Deployment Guide

## Prerequisites

1. **Install Hugging Face CLI**:
   ```bash
   pip install huggingface_hub
   ```

2. **Login to Hugging Face**:
   ```bash
   huggingface-cli login
   ```
   Enter your access token when prompted.

## Upload Steps

1. **Navigate to models directory**:
   ```bash
   cd {self.models_dir}
   ```

2. **Run upload script**:
   ```bash
   python3 upload_to_hub.py
   ```

## Manual Upload Alternative

```python
from huggingface_hub import HfApi

api = HfApi()

# Create repository
api.create_repo("yussufabdi/budul-gpt-enhanced", exist_ok=True)

# Upload files
api.upload_folder(
    folder_path="{self.models_dir}",
    repo_id="yussufabdi/budul-gpt-enhanced",
    commit_message="Upload BudulGPT Enhanced v2.0"
)
```

## Files to Upload

- `model.safetensors` - The trained model
- `training_args.bin` - Training configuration  
- `enhanced_model_config.json` - Enhanced model metadata
- `README.md` - Model documentation
- `enhancement_report.json` - Enhancement details

## Post-Upload

After successful upload:

1. Visit: https://huggingface.co/yussufabdi/budul-gpt-enhanced
2. Verify all files uploaded correctly
3. Test the model using the Hugging Face interface
4. Share with the Islamic AI community!

## Troubleshooting

- **Authentication Error**: Run `huggingface-cli login` again
- **Permission Denied**: Ensure you own the repository or have write access
- **Large File Error**: Use Git LFS for files > 10MB (automatically handled)

---

*Ready to share your authentic Islamic AI with the world!* 🌍
"""
        
        guide_file = self.models_dir / "DEPLOYMENT_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"✅ Deployment guide created: {guide_file}")
        return str(guide_file)
    
    def prepare_for_upload(self):
        """Prepare everything for Hugging Face upload"""
        print("=" * 60)
        print("🤗 Preparing BudulGPT Enhanced for Hugging Face Hub")
        print("=" * 60)
        
        try:
            # Check setup
            setup_ok = self.check_huggingface_setup()
            
            # Create documentation
            readme_file = self.create_model_card()
            upload_script = self.create_upload_script()
            guide_file = self.create_deployment_guide()
            
            print("=" * 60)
            print("✅ BudulGPT Upload Preparation Complete!")
            print(f"📝 Model card: {readme_file}")
            print(f"🚀 Upload script: {upload_script}")
            print(f"📚 Deployment guide: {guide_file}")
            
            if setup_ok:
                print("\n🎯 Ready to upload! Run:")
                print(f"cd {self.models_dir} && python3 upload_to_hub.py")
            else:
                print("\n⚠️ Setup Hugging Face first:")
                print("1. huggingface-cli login")
                print("2. python3 upload_to_hub.py")
            
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Preparation failed: {e}")
            return False

if __name__ == "__main__":
    uploader = HuggingFaceUploader()
    uploader.prepare_for_upload()
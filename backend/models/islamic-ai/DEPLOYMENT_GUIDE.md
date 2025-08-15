# BudulGPT Enhanced Deployment Guide

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
   cd /Users/yussufabdi/budul-ai/backend/models/islamic-ai
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
    folder_path="/Users/yussufabdi/budul-ai/backend/models/islamic-ai",
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

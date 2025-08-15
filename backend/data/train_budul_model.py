"""
BudulGPT Model Training Script
Train Islamic AI model with authentic Islamic dataset
"""

import json
import os
import torch
from pathlib import Path
from datetime import datetime
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BudulGPTTrainer:
    def __init__(self, base_model="microsoft/DialoGPT-small"):
        self.base_model = base_model
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "authentic_islamic_dataset"
        self.models_dir = self.base_dir.parent / "models" / "islamic-ai"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🤖 BudulGPT Training Initialized")
        print(f"📚 Data directory: {self.data_dir}")
        print(f"🏗️ Models directory: {self.models_dir}")
        
        # Check if CUDA is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🖥️ Training device: {self.device}")
    
    def load_training_data(self):
        """Load and prepare training data"""
        print("📖 Loading training data...")
        
        training_file = self.data_dir / "budul_islamic_training.jsonl"
        
        if not training_file.exists():
            raise FileNotFoundError(f"Training file not found: {training_file}")
        
        # Load JSONL data
        training_data = []
        with open(training_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    training_data.append(data)
        
        print(f"✅ Loaded {len(training_data)} training examples")
        
        # Prepare conversational format
        conversations = []
        for item in training_data:
            # Format as conversation for Islamic chatbot
            conversation = f"Human: {item['input']}\nBudulGPT: {item['output']}"
            conversations.append({
                'text': conversation,
                'topic': item.get('topic', 'islamic'),
                'authenticity': item.get('authenticity', 'verified')
            })
        
        return conversations
    
    def prepare_dataset(self, conversations):
        """Prepare dataset for training"""
        print("🔄 Preparing dataset for training...")
        
        # Initialize tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Tokenize conversations
        def tokenize_function(examples):
            return tokenizer(
                examples['text'],
                truncation=True,
                padding='max_length',
                max_length=512,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_list(conversations)
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        print(f"✅ Dataset prepared: {len(tokenized_dataset)} examples")
        return tokenized_dataset, tokenizer
    
    def setup_model_and_trainer(self, tokenized_dataset, tokenizer):
        """Setup model and trainer"""
        print(f"🏗️ Setting up model: {self.base_model}")
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(self.base_model)
        model.resize_token_embeddings(len(tokenizer))
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.models_dir),
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=2,
            warmup_steps=10,
            max_steps=100,  # Limited for demo
            logging_dir=str(self.models_dir / "logs"),
            logging_steps=10,
            save_steps=50,
            save_total_limit=2,
            prediction_loss_only=True,
            learning_rate=5e-5,
            weight_decay=0.01,
            adam_epsilon=1e-8,
            max_grad_norm=1.0,
            dataloader_pin_memory=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset,
            tokenizer=tokenizer,
        )
        
        return model, trainer
    
    def train_model(self):
        """Complete training process"""
        print("=" * 60)
        print("🕌 Starting BudulGPT Training")
        print("=" * 60)
        
        try:
            # Load and prepare data
            conversations = self.load_training_data()
            tokenized_dataset, tokenizer = self.prepare_dataset(conversations)
            
            # Setup model and trainer
            model, trainer = self.setup_model_and_trainer(tokenized_dataset, tokenizer)
            
            # Start training
            print("🚀 Starting model training...")
            training_start = datetime.now()
            
            trainer.train()
            
            training_end = datetime.now()
            training_duration = training_end - training_start
            
            print(f"✅ Training completed in {training_duration}")
            
            # Save the model
            final_model_path = self.models_dir / "budul-islamic-model"
            model.save_pretrained(final_model_path)
            tokenizer.save_pretrained(final_model_path)
            
            print(f"💾 Model saved to: {final_model_path}")
            
            # Save training info
            training_info = {
                'base_model': self.base_model,
                'training_examples': len(conversations),
                'training_start': training_start.isoformat(),
                'training_end': training_end.isoformat(),
                'training_duration': str(training_duration),
                'model_path': str(final_model_path),
                'device': str(self.device)
            }
            
            info_file = self.models_dir / "training_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(training_info, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Training info saved to: {info_file}")
            print("=" * 60)
            print("🎉 BudulGPT training completed successfully!")
            print("=" * 60)
            
            return str(final_model_path)
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise e
    
    def test_trained_model(self, model_path):
        """Test the trained model"""
        print("🧪 Testing trained BudulGPT...")
        
        try:
            # Load trained model
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Test questions
            test_questions = [
                "What are the five pillars of Islam?",
                "How do I perform wudu?",
                "What is the meaning of Bismillah?"
            ]
            
            for question in test_questions:
                input_text = f"Human: {question}\nBudulGPT:"
                input_ids = tokenizer.encode(input_text, return_tensors='pt')
                
                with torch.no_grad():
                    output = model.generate(
                        input_ids,
                        max_length=input_ids.shape[1] + 100,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )
                
                response = tokenizer.decode(output[0], skip_special_tokens=True)
                print(f"\n🤖 Q: {question}")
                print(f"💬 A: {response[len(input_text):]}")
            
            print("\n✅ Model testing completed!")
            
        except Exception as e:
            print(f"❌ Model testing failed: {e}")

if __name__ == "__main__":
    # Check if transformers is installed
    try:
        import transformers
        print(f"🔧 Transformers version: {transformers.__version__}")
    except ImportError:
        print("❌ Please install transformers: pip install transformers datasets torch")
        exit(1)
    
    # Initialize and run training
    trainer = BudulGPTTrainer()
    model_path = trainer.train_model()
    
    # Test the model
    trainer.test_trained_model(model_path)
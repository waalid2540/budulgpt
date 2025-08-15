"""
Simplified Islamic Dataset Collection for BudulGPT
Collect authentic Islamic content from verified sources
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class SimpleIslamicCollector:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.scraper_dir = self.base_dir / "islamic_scraper"
        self.output_dir = self.base_dir / "authentic_islamic_dataset"
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"🚀 Starting Simple BudulGPT Islamic Dataset Collection...")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🔧 Scraper directory: {self.scraper_dir}")
    
    def collect_from_existing_data(self):
        """Process existing Islamic training data"""
        print(f"📚 Processing existing Islamic training data...")
        
        # Check for existing data files
        training_file = self.base_dir.parent / "data" / "islamic_training_data.jsonl"
        if training_file.exists():
            print(f"✅ Found existing training data: {training_file}")
            self.process_jsonl_data(training_file)
        
        # Check dataset collection outputs
        dataset_dir = self.base_dir.parent.parent / "dataset_collection" / "sunni_outputs"
        if dataset_dir.exists():
            for json_file in dataset_dir.glob("*.json"):
                print(f"✅ Found dataset: {json_file}")
                self.process_dataset_json(json_file)
    
    def process_jsonl_data(self, file_path):
        """Process JSONL training data"""
        try:
            training_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        training_data.append(data)
            
            print(f"📖 Processed {len(training_data)} training examples")
            
            # Save processed data
            output_file = self.output_dir / "processed_training_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to: {output_file}")
            return training_data
            
        except Exception as e:
            print(f"❌ Error processing JSONL: {e}")
            return []
    
    def process_dataset_json(self, file_path):
        """Process dataset JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            metadata = dataset.get('metadata', {})
            print(f"📊 Dataset info:")
            print(f"   - Total content: {metadata.get('total_content', 'unknown')}")
            print(f"   - Authenticity threshold: {metadata.get('authenticity_threshold', 'unknown')}")
            print(f"   - Madhabs included: {metadata.get('madhabs_included', [])}")
            
            # Extract actual content
            content = dataset.get('data', [])
            if content:
                print(f"📚 Found {len(content)} content items")
                
                # Save processed content
                output_file = self.output_dir / f"processed_{file_path.name}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'metadata': metadata,
                        'content': content,
                        'processed_at': datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved processed dataset to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing dataset: {e}")
    
    def create_training_format(self):
        """Convert collected data to training format"""
        print(f"🔄 Converting data to training format...")
        
        all_data = []
        
        # Process all JSON files in output directory
        for json_file in self.output_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    all_data.extend(data)
                elif isinstance(data, dict):
                    content = data.get('content', [])
                    if content:
                        all_data.extend(content)
                
            except Exception as e:
                print(f"❌ Error reading {json_file}: {e}")
        
        print(f"📚 Total items for training: {len(all_data)}")
        
        # Create training JSONL
        if all_data:
            training_file = self.output_dir / "budul_islamic_training.jsonl"
            with open(training_file, 'w', encoding='utf-8') as f:
                for item in all_data:
                    # Ensure proper format for training
                    if isinstance(item, dict):
                        # Convert to training format if needed
                        if 'question' in item and 'answer' in item:
                            training_item = {
                                'input': item['question'],
                                'output': item['answer'],
                                'topic': item.get('topic', 'islamic'),
                                'authenticity': item.get('authenticity', 'verified')
                            }
                        else:
                            training_item = item
                        
                        f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
            
            print(f"✅ Training data saved to: {training_file}")
            return str(training_file)
        
        return None
    
    def run_collection(self):
        """Run the complete collection process"""
        print("=" * 60)
        print("🕌 BudulGPT Islamic Dataset Collection")
        print("=" * 60)
        
        # Step 1: Process existing data
        self.collect_from_existing_data()
        
        # Step 2: Create training format
        training_file = self.create_training_format()
        
        # Step 3: Generate summary
        self.generate_summary()
        
        print("=" * 60)
        print("✅ Collection completed!")
        if training_file:
            print(f"📚 Training file: {training_file}")
        print("=" * 60)
        
        return training_file
    
    def generate_summary(self):
        """Generate collection summary"""
        print(f"📊 Generating collection summary...")
        
        summary = {
            'collection_date': datetime.now().isoformat(),
            'output_directory': str(self.output_dir),
            'files_created': [],
            'total_items': 0
        }
        
        for file in self.output_dir.iterdir():
            if file.suffix == '.json':
                summary['files_created'].append(str(file.name))
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            summary['total_items'] += len(data)
                        elif isinstance(data, dict) and 'content' in data:
                            summary['total_items'] += len(data['content'])
                except:
                    pass
        
        # Save summary
        summary_file = self.output_dir / "collection_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Summary saved to: {summary_file}")

if __name__ == "__main__":
    collector = SimpleIslamicCollector()
    collector.run_collection()
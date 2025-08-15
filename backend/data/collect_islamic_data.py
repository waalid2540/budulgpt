"""
Islamic Dataset Collection Pipeline for BudulGPT
Collect authentic Islamic content from verified sources
"""

import os
import json
import subprocess
import pandas as pd
from datetime import datetime
from pathlib import Path

class IslamicDataCollector:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.scraper_dir = self.base_dir / "islamic_scraper"
        self.output_dir = self.base_dir / "authentic_islamic_dataset"
        self.output_dir.mkdir(exist_ok=True)
        
        # Authentic Islamic sources
        self.islamic_sources = {
            "binbaz": {
                "base_url": "https://binbaz.org.sa/",
                "content_type": "fatwas",
                "description": "Ibn Baz Foundation - Authentic Saudi Fatwas"
            },
            "youtube_islamic": {
                "channels": [
                    "islamweb",
                    "islamicknowledgechannel", 
                    "authenticislam"
                ],
                "description": "Authentic Islamic YouTube channels"
            }
        }
    
    def collect_binbaz_fatwas(self, total_pages=100):
        """Collect authentic fatwas from binbaz.org.sa"""
        print(f"🕌 Collecting fatwas from Ibn Baz Foundation...")
        
        output_file = self.output_dir / "binbaz_fatwas.json"
        
        cmd = [
            "python3", str(self.scraper_dir / "scraping.py"),
            "--action", "static",
            "--outfile", str(output_file),
            "--base_url", "https://binbaz.org.sa/",
            "--list_content", "fatwas",
            "--total_pages", str(total_pages)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.scraper_dir)
            if result.returncode == 0:
                print(f"✅ Successfully collected fatwas: {output_file}")
                return str(output_file)
            else:
                print(f"❌ Error collecting fatwas: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Exception collecting fatwas: {e}")
            return None
    
    def collect_islamic_youtube_transcripts(self, playlists):
        """Collect Islamic content from YouTube playlists"""
        print(f"📺 Collecting Islamic content from YouTube...")
        
        output_file = self.output_dir / "islamic_youtube_transcripts.json"
        
        cmd = [
            "python3", str(self.scraper_dir / "scraping.py"),
            "--action", "transcripts",
            "--playlists", ",".join(playlists),
            "--channel", "islamic_content",
            "--outfile", str(output_file),
            "--missed_reader", str(self.output_dir / "missed_videos.txt")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.scraper_dir)
            if result.returncode == 0:
                print(f"✅ Successfully collected YouTube transcripts: {output_file}")
                return str(output_file)
            else:
                print(f"❌ Error collecting YouTube transcripts: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Exception collecting YouTube transcripts: {e}")
            return None
    
    def process_and_format_data(self, raw_files):
        """Process raw scraped data into training format"""
        print(f"🔄 Processing raw data into training format...")
        
        training_data = []
        
        for file_path in raw_files:
            if not file_path or not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Process based on source type
                if "binbaz" in file_path:
                    processed = self._process_fatwa_data(raw_data)
                elif "youtube" in file_path:
                    processed = self._process_youtube_data(raw_data)
                else:
                    continue
                
                training_data.extend(processed)
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        
        # Save processed training data
        training_file = self.output_dir / "budul_training_data.jsonl"
        
        with open(training_file, 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"✅ Processed {len(training_data)} training examples")
        print(f"💾 Saved to: {training_file}")
        
        return str(training_file)
    
    def _process_fatwa_data(self, raw_data):
        """Process fatwa data into conversational format"""
        processed = []
        
        for item in raw_data:
            if isinstance(item, dict) and 'question' in item and 'answer' in item:
                processed.append({
                    "messages": [
                        {"role": "user", "content": item['question']},
                        {"role": "assistant", "content": f"بسم الله الرحمن الرحيم\n\n{item['answer']}\n\nوالله أعلم (And Allah knows best)"}
                    ],
                    "source": "binbaz.org.sa",
                    "authenticity": "high",
                    "type": "fatwa"
                })
        
        return processed
    
    def _process_youtube_data(self, raw_data):
        """Process YouTube transcript data"""
        processed = []
        
        for item in raw_data:
            if isinstance(item, dict) and 'transcript' in item:
                # Create conversational pairs from transcripts
                transcript = item['transcript']
                if len(transcript) > 100:  # Only use substantial content
                    processed.append({
                        "messages": [
                            {"role": "user", "content": "Please explain this Islamic topic"},
                            {"role": "assistant", "content": f"بسم الله الرحمن الرحيم\n\n{transcript}"}
                        ],
                        "source": "youtube_islamic",
                        "authenticity": "medium",
                        "type": "educational"
                    })
        
        return processed
    
    def generate_dataset_report(self, training_file):
        """Generate report about collected dataset"""
        if not os.path.exists(training_file):
            return
        
        with open(training_file, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        
        report = {
            "total_examples": len(data),
            "sources": {},
            "types": {},
            "authenticity_levels": {},
            "collection_date": datetime.now().isoformat()
        }
        
        for item in data:
            source = item.get('source', 'unknown')
            type_val = item.get('type', 'unknown')
            auth_level = item.get('authenticity', 'unknown')
            
            report["sources"][source] = report["sources"].get(source, 0) + 1
            report["types"][type_val] = report["types"].get(type_val, 0) + 1
            report["authenticity_levels"][auth_level] = report["authenticity_levels"].get(auth_level, 0) + 1
        
        report_file = self.output_dir / "dataset_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Dataset Report:")
        print(f"   Total Examples: {report['total_examples']}")
        print(f"   Sources: {report['sources']}")
        print(f"   Types: {report['types']}")
        print(f"   Authenticity: {report['authenticity_levels']}")
        
        return str(report_file)

def main():
    """Main collection pipeline"""
    collector = IslamicDataCollector()
    
    print("🚀 Starting BudulGPT Islamic Dataset Collection...")
    
    # Collect data from sources
    raw_files = []
    
    # 1. Collect fatwas from binbaz.org.sa
    fatwa_file = collector.collect_binbaz_fatwas(total_pages=50)
    if fatwa_file:
        raw_files.append(fatwa_file)
    
    # 2. Collect Islamic YouTube content (example playlists)
    islamic_playlists = [
        "https://www.youtube.com/playlist?list=PLgaTRTylCbZDP43U58PFXNflz-8zzUwvJ"
    ]
    youtube_file = collector.collect_islamic_youtube_transcripts(islamic_playlists)
    if youtube_file:
        raw_files.append(youtube_file)
    
    # 3. Process into training format
    if raw_files:
        training_file = collector.process_and_format_data(raw_files)
        collector.generate_dataset_report(training_file)
        
        print(f"\n🎉 BudulGPT Dataset Collection Complete!")
        print(f"📁 Training data: {training_file}")
        print(f"🔥 Ready for model training!")
    else:
        print("❌ No data collected. Check internet connection and source availability.")

if __name__ == "__main__":
    main()
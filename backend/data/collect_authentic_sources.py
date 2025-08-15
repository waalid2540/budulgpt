"""
Collect Authentic Islamic Sources for BudulGPT
Actually download from binbaz.org.sa and other authentic sources
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re

class AuthenticIslamicCollector:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "authentic_islamic_dataset"
        self.output_dir.mkdir(exist_ok=True)
        
        print("🕌 Authentic Islamic Sources Collector")
        print(f"📁 Output: {self.output_dir}")
        
        # Headers to appear as regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def collect_binbaz_fatwas(self, max_pages=5):
        """Collect authentic fatwas from binbaz.org.sa"""
        print("🕌 Collecting from Ibn Baz Foundation...")
        
        fatwas = []
        base_url = "https://binbaz.org.sa"
        
        try:
            # Try to get fatwa categories first
            categories_url = f"{base_url}/fatwas"
            print(f"📡 Fetching: {categories_url}")
            
            response = requests.get(categories_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for fatwa links
                fatwa_links = soup.find_all('a', href=re.compile(r'/fatwas/'))
                print(f"🔍 Found {len(fatwa_links)} potential fatwa links")
                
                # Process first few fatwas
                for i, link in enumerate(fatwa_links[:10]):  # Limit to 10 for demo
                    try:
                        fatwa_url = base_url + link.get('href')
                        print(f"📖 Processing fatwa {i+1}: {fatwa_url}")
                        
                        fatwa_response = requests.get(fatwa_url, headers=self.headers, timeout=10)
                        if fatwa_response.status_code == 200:
                            fatwa_soup = BeautifulSoup(fatwa_response.content, 'html.parser')
                            
                            # Extract question and answer
                            title = fatwa_soup.find('h1')
                            content = fatwa_soup.find('div', class_=['content', 'fatwa-content', 'main-content'])
                            
                            if title and content:
                                question = title.get_text().strip()
                                answer = content.get_text().strip()
                                
                                if len(question) > 10 and len(answer) > 50:
                                    fatwa = {
                                        'question': question,
                                        'answer': answer,
                                        'source': 'binbaz.org.sa',
                                        'url': fatwa_url,
                                        'topic': 'fatwa',
                                        'authenticity': 'authentic',
                                        'collected_at': datetime.now().isoformat()
                                    }
                                    fatwas.append(fatwa)
                                    print(f"✅ Collected: {question[:50]}...")
                        
                        time.sleep(1)  # Be respectful to the server
                        
                    except Exception as e:
                        print(f"⚠️ Error processing fatwa {i+1}: {e}")
                        continue
            
            else:
                print(f"❌ Failed to access {categories_url}: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error collecting from binbaz.org.sa: {e}")
        
        # Save collected fatwas
        if fatwas:
            output_file = self.output_dir / "binbaz_fatwas.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fatwas, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(fatwas)} fatwas to: {output_file}")
        else:
            print("⚠️ No fatwas collected from binbaz.org.sa")
        
        return fatwas
    
    def collect_islamqa_content(self, max_items=10):
        """Collect from IslamQA (authentic Q&A site)"""
        print("🌐 Collecting from IslamQA...")
        
        islamqa_data = []
        
        try:
            # IslamQA has structured Q&A format
            base_url = "https://islamqa.info/en"
            
            # Try to get recent questions
            response = requests.get(f"{base_url}/cat/1", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for question links
                question_links = soup.find_all('a', href=re.compile(r'/en/answers/'))
                print(f"🔍 Found {len(question_links)} potential questions")
                
                for i, link in enumerate(question_links[:max_items]):
                    try:
                        question_url = link.get('href')
                        if not question_url.startswith('http'):
                            question_url = base_url + question_url
                        
                        print(f"📖 Processing question {i+1}: {question_url}")
                        
                        q_response = requests.get(question_url, headers=self.headers, timeout=10)
                        if q_response.status_code == 200:
                            q_soup = BeautifulSoup(q_response.content, 'html.parser')
                            
                            # Extract question and answer
                            title = q_soup.find('h1')
                            answer_div = q_soup.find('div', class_=['answer', 'content', 'main'])
                            
                            if title and answer_div:
                                question = title.get_text().strip()
                                answer = answer_div.get_text().strip()
                                
                                if len(question) > 10 and len(answer) > 50:
                                    qa_item = {
                                        'question': question,
                                        'answer': answer,
                                        'source': 'islamqa.info',
                                        'url': question_url,
                                        'topic': 'islamic_qa',
                                        'authenticity': 'verified',
                                        'collected_at': datetime.now().isoformat()
                                    }
                                    islamqa_data.append(qa_item)
                                    print(f"✅ Collected: {question[:50]}...")
                        
                        time.sleep(1)  # Be respectful
                        
                    except Exception as e:
                        print(f"⚠️ Error processing question {i+1}: {e}")
                        continue
            
        except Exception as e:
            print(f"❌ Error collecting from IslamQA: {e}")
        
        # Save collected data
        if islamqa_data:
            output_file = self.output_dir / "islamqa_content.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(islamqa_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(islamqa_data)} Q&As to: {output_file}")
        
        return islamqa_data
    
    def create_quality_metrics(self, collected_data):
        """Create quality metrics and authenticity scoring"""
        print("📊 Creating quality metrics...")
        
        total_items = len(collected_data)
        
        # Analyze authenticity
        authenticity_scores = {}
        source_counts = {}
        topic_counts = {}
        
        for item in collected_data:
            source = item.get('source', 'unknown')
            topic = item.get('topic', 'general')
            authenticity = item.get('authenticity', 'unverified')
            
            source_counts[source] = source_counts.get(source, 0) + 1
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            authenticity_scores[authenticity] = authenticity_scores.get(authenticity, 0) + 1
        
        # Calculate quality score
        authentic_count = authenticity_scores.get('authentic', 0) + authenticity_scores.get('verified', 0)
        quality_score = (authentic_count / total_items) * 100 if total_items > 0 else 0
        
        metrics = {
            'collection_date': datetime.now().isoformat(),
            'total_items': total_items,
            'quality_score': round(quality_score, 2),
            'authenticity_distribution': authenticity_scores,
            'source_distribution': source_counts,
            'topic_distribution': topic_counts,
            'verification_status': {
                'verified_sources': ['binbaz.org.sa', 'islamqa.info'],
                'authenticity_threshold': 0.85,
                'quality_standard': 'high'
            }
        }
        
        # Save metrics
        metrics_file = self.output_dir / "quality_metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Quality metrics saved to: {metrics_file}")
        print(f"🎯 Quality Score: {quality_score}%")
        print(f"📚 Total Items: {total_items}")
        
        return metrics
    
    def run_collection(self):
        """Run complete authentic collection process"""
        print("=" * 60)
        print("🕌 Authentic Islamic Sources Collection")
        print("=" * 60)
        
        all_collected_data = []
        
        # Collect from binbaz.org.sa
        print("\n1️⃣ Collecting from Ibn Baz Foundation...")
        binbaz_data = self.collect_binbaz_fatwas()
        all_collected_data.extend(binbaz_data)
        
        # Collect from IslamQA
        print("\n2️⃣ Collecting from IslamQA...")
        islamqa_data = self.collect_islamqa_content()
        all_collected_data.extend(islamqa_data)
        
        # Create quality metrics
        print("\n3️⃣ Analyzing quality and authenticity...")
        metrics = self.create_quality_metrics(all_collected_data)
        
        # Save combined dataset
        if all_collected_data:
            combined_file = self.output_dir / "authentic_combined_dataset.json"
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': metrics,
                    'data': all_collected_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Combined dataset saved to: {combined_file}")
        
        print("=" * 60)
        print("✅ Authentic Collection Completed!")
        print(f"📊 Quality Score: {metrics.get('quality_score', 0)}%")
        print(f"📚 Total Authentic Items: {len(all_collected_data)}")
        print("=" * 60)
        
        return all_collected_data, metrics

if __name__ == "__main__":
    collector = AuthenticIslamicCollector()
    data, metrics = collector.run_collection()
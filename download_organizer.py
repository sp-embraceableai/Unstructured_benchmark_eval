#!/usr/bin/env python3
"""
German PDF Download and Organizer

This script helps download and organize German PDFs for benchmarking Unstructured.
It provides utilities to download PDFs from various sources and organize them
into the appropriate benchmark categories.
"""

import os
import requests
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional
import time
import logging

class PDFDownloader:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def download_pdf(self, url: str, filename: str, category: str) -> Optional[Path]:
        """Download a PDF from URL and save to appropriate category folder"""
        try:
            category_dir = self.benchmarks_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = category_dir / filename
            
            if file_path.exists():
                self.logger.info(f"File already exists: {file_path}")
                return file_path
            
            self.logger.info(f"Downloading {url} to {file_path}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not filename.lower().endswith('.pdf'):
                self.logger.warning(f"Response doesn't appear to be a PDF: {content_type}")
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Successfully downloaded: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return None
    
    def search_bundesanzeiger(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search Bundesanzeiger for PDFs (simulated - you'll need to implement actual search)"""
        # This is a placeholder - you'll need to implement actual search
        # Bundesanzeiger has a search API that you can use
        self.logger.info(f"Searching Bundesanzeiger for: {query}")
        
        # Example URLs (you'll need to find actual URLs)
        example_urls = [
            f"https://www.bundesanzeiger.de/pub/de/amtsblatt/{query}",
            f"https://www.bundesanzeiger.de/pub/de/amtsblatt/2024/{query}",
        ]
        
        return [{"url": url, "title": f"Bundesanzeiger {query}", "category": "short_text"} 
                for url in example_urls]

class PDFOrganizer:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.downloader = PDFDownloader(benchmarks_dir)
        
        # Define document mappings
        self.document_mappings = {
            "short_text": [
                {
                    "name": "bundesanzeiger_kurzbericht_sicherheit.pdf",
                    "description": "Bundesanzeiger Kurzbericht über Sicherheit & klinische Leistung",
                    "url": "https://www.bundesanzeiger.de/pub/de/amtsblatt/2024/kurzbericht-sicherheit",
                    "pages": 4
                },
                {
                    "name": "bekanntmachung_20240402_B3.pdf", 
                    "description": "Bundesanzeiger Bekanntmachung 02.04.2024 B3 (project summary)",
                    "url": "https://www.bundesanzeiger.de/pub/de/amtsblatt/2024/bekanntmachung-20240402-b3",
                    "pages": 3
                },
                {
                    "name": "bekanntmachung_20220527_B4.pdf",
                    "description": "Bundesanzeiger Bekanntmachung 27.05.2022 B4 (regulation notice)", 
                    "url": "https://www.bundesanzeiger.de/pub/de/amtsblatt/2022/bekanntmachung-20220527-b4",
                    "pages": 4
                }
            ],
            "long_text": [
                {
                    "name": "statistisches_jahrbuch_2019_bevoelkerung.pdf",
                    "description": "Statistisches Jahrbuch 2019 - Bevölkerung chapter",
                    "url": "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Publikationen/Downloads-Bevoelkerung/statistisches-jahrbuch-2019-bevoelkerung.pdf",
                    "pages": 25
                },
                {
                    "name": "statistische_bibliothek_bericht.pdf",
                    "description": "Statistische Bibliothek Reports (multi-chapter)",
                    "url": "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Publikationen/Downloads-Bevoelkerung/statistische-bibliothek-bericht.pdf", 
                    "pages": 30
                },
                {
                    "name": "saechsische_laengsschnittstudie_welle1.pdf",
                    "description": "Sächsische Längsschnittstudie – Welle 1",
                    "url": "https://www.statistik.sachsen.de/download/laengsschnittstudie-welle1.pdf",
                    "pages": 15
                }
            ],
            "table_heavy": [
                {
                    "name": "verbraucherpreisindex_lange_reihen.pdf",
                    "description": "Verbraucherpreisindex für Deutschland – Lange Reihen ab 1948",
                    "url": "https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Verbraucherpreisindex/Publikationen/Downloads-Verbraucherpreisindex/verbraucherpreisindex-lange-reihen.pdf",
                    "pages": 20
                },
                {
                    "name": "bevoelkerungsstand_tabellen.pdf",
                    "description": "Bevölkerungsstand – Tabellen und Zeitreihen",
                    "url": "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Bevoelkerungsstand/Publikationen/Downloads-Bevoelkerungsstand/bevoelkerungsstand-tabellen.pdf",
                    "pages": 18
                },
                {
                    "name": "jahrbuch_2019_preise.pdf",
                    "description": "Statistisches Jahrbuch 2019 – Preise chapter (data-loaded)",
                    "url": "https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Publikationen/Downloads-Preise/jahrbuch-2019-preise.pdf",
                    "pages": 22
                }
            ],
            "image_heavy": [
                {
                    "name": "demografie_trends_visuals.pdf",
                    "description": "Destatis demographic trend visuals",
                    "url": "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Publikationen/Downloads-Bevoelkerung/demografie-trends-visuals.pdf",
                    "pages": 12
                },
                {
                    "name": "umweltbericht_scan.pdf",
                    "description": "OpenGovData.de environmental impact report (scan-based)",
                    "url": "https://opengovdata.de/reports/umweltbericht-2024.pdf",
                    "pages": 16
                },
                {
                    "name": "zensus_2022_report.pdf",
                    "description": "Zensus 2022 report with images/graphics",
                    "url": "https://www.zensus2022.de/DE/Service/Downloads/zensus-2022-report.pdf",
                    "pages": 14
                }
            ]
        }
    
    def create_folder_structure(self):
        """Create the benchmark folder structure"""
        categories = ["short_text", "long_text", "table_heavy", "image_heavy"]
        
        for category in categories:
            category_dir = self.benchmarks_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {category_dir}")
    
    def download_all_pdfs(self, max_retries: int = 3):
        """Download all PDFs for the benchmark"""
        print("🚀 Starting PDF download process...")
        print("⚠️  Note: Some URLs may be example/placeholder URLs")
        print("   You may need to manually find and download the actual PDFs")
        print()
        
        total_downloads = 0
        successful_downloads = 0
        
        for category, documents in self.document_mappings.items():
            print(f"📁 Processing category: {category}")
            
            for doc in documents:
                total_downloads += 1
                print(f"  📄 {doc['name']}")
                print(f"     Description: {doc['description']}")
                print(f"     Pages: {doc['pages']}")
                
                # Try to download
                result = self.downloader.download_pdf(
                    doc['url'], 
                    doc['name'], 
                    category
                )
                
                if result:
                    successful_downloads += 1
                    print(f"     ✅ Downloaded successfully")
                else:
                    print(f"     ❌ Download failed (URL may be placeholder)")
                
                print()
                time.sleep(1)  # Be nice to servers
        
        print(f"📊 Download Summary:")
        print(f"   Total attempted: {total_downloads}")
        print(f"   Successful: {successful_downloads}")
        print(f"   Failed: {total_downloads - successful_downloads}")
        
        if successful_downloads < total_downloads:
            print()
            print("💡 Manual Download Instructions:")
            print("1. Visit the source websites:")
            print("   - bundesanzeiger.de")
            print("   - destatis.de") 
            print("   - opengovdata.de")
            print("   - zensus2022.de")
            print("2. Search for the documents listed above")
            print("3. Download and place them in the appropriate folders")
    
    def generate_download_guide(self):
        """Generate a markdown guide for manual downloads"""
        guide = []
        guide.append("# German PDF Download Guide")
        guide.append("")
        guide.append("This guide helps you manually download the German PDFs for benchmarking.")
        guide.append("")
        
        for category, documents in self.document_mappings.items():
            guide.append(f"## {category.replace('_', ' ').title()}")
            guide.append("")
            
            for doc in documents:
                guide.append(f"### {doc['name']}")
                guide.append(f"- **Description**: {doc['description']}")
                guide.append(f"- **Expected Pages**: {doc['pages']}")
                guide.append(f"- **Source**: {doc['url']}")
                guide.append(f"- **Save to**: `benchmarks/{category}/{doc['name']}`")
                guide.append("")
        
        guide.append("## Source Websites")
        guide.append("")
        guide.append("- **Bundesanzeiger**: https://www.bundesanzeiger.de")
        guide.append("- **Destatis (Federal Statistical Office)**: https://www.destatis.de")
        guide.append("- **OpenGovData**: https://opengovdata.de")
        guide.append("- **Zensus 2022**: https://www.zensus2022.de")
        guide.append("")
        guide.append("## Download Tips")
        guide.append("")
        guide.append("1. Use the search functions on each website")
        guide.append("2. Look for 'Publikationen' or 'Downloads' sections")
        guide.append("3. Some documents may require free registration")
        guide.append("4. Check for different years if current year not available")
        
        with open("download_guide.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(guide))
        
        print("📝 Download guide saved to 'download_guide.md'")
    
    def verify_downloads(self):
        """Verify which PDFs have been downloaded"""
        print("🔍 Verifying downloaded PDFs...")
        print()
        
        total_expected = 0
        total_found = 0
        
        for category, documents in self.document_mappings.items():
            category_dir = self.benchmarks_dir / category
            print(f"📁 {category}:")
            
            for doc in documents:
                total_expected += 1
                file_path = category_dir / doc['name']
                
                if file_path.exists():
                    file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                    print(f"  ✅ {doc['name']} ({file_size:.2f} MB)")
                    total_found += 1
                else:
                    print(f"  ❌ {doc['name']} (missing)")
            
            print()
        
        print(f"📊 Summary: {total_found}/{total_expected} PDFs found")
        
        if total_found < total_expected:
            print("💡 Run 'python download_organizer.py --guide' to see manual download instructions")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and organize German PDFs for benchmarking")
    parser.add_argument("--create-folders", action="store_true", help="Create folder structure only")
    parser.add_argument("--download", action="store_true", help="Download PDFs (may fail for placeholder URLs)")
    parser.add_argument("--verify", action="store_true", help="Verify which PDFs are downloaded")
    parser.add_argument("--guide", action="store_true", help="Generate download guide")
    parser.add_argument("--all", action="store_true", help="Run all operations")
    
    args = parser.parse_args()
    
    organizer = PDFOrganizer()
    
    if args.create_folders or args.all:
        organizer.create_folder_structure()
    
    if args.download or args.all:
        organizer.download_all_pdfs()
    
    if args.verify or args.all:
        organizer.verify_downloads()
    
    if args.guide or args.all:
        organizer.generate_download_guide()
    
    if not any([args.create_folders, args.download, args.verify, args.guide, args.all]):
        print("🔧 German PDF Organizer")
        print()
        print("Usage:")
        print("  python download_organizer.py --create-folders  # Create folder structure")
        print("  python download_organizer.py --download        # Download PDFs")
        print("  python download_organizer.py --verify          # Check what's downloaded")
        print("  python download_organizer.py --guide           # Generate download guide")
        print("  python download_organizer.py --all             # Run everything")
        print()
        print("Note: Some URLs may be placeholders. Check the download guide for manual instructions.")

if __name__ == "__main__":
    main() 
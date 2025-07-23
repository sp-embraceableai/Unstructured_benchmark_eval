#!/usr/bin/env python3
"""
Baden-Württemberg Budget PDF Downloader

This script downloads PDFs from the Baden-Württemberg state budget website
and organizes them for benchmarking Unstructured performance.
"""

import requests
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
import logging

class BWBudgetDownloader:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.base_url = "https://fm.baden-wuerttemberg.de"
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
    
    def get_budget_page(self, url: str) -> str:
        """Get the main budget page content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to get page {url}: {e}")
            return ""
    
    def extract_pdf_links(self, html_content: str) -> list:
        """Extract PDF links from the HTML content"""
        pdf_links = []
        
        # Look for PDF links in the content
        # Common patterns for budget PDFs
        patterns = [
            r'href=["\']([^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*download[^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*haushalt[^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*einzelplan[^"\']*\.pdf)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    pdf_links.append(match)
                else:
                    pdf_links.append(urljoin(self.base_url, match))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in pdf_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def download_pdf(self, url: str, filename: str, category: str) -> bool:
        """Download a PDF from URL and save to appropriate category folder"""
        try:
            category_dir = self.benchmarks_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = category_dir / filename
            
            if file_path.exists():
                self.logger.info(f"File already exists: {file_path}")
                return True
            
            self.logger.info(f"Downloading {url} to {file_path}")
            
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not filename.lower().endswith('.pdf'):
                self.logger.warning(f"Response doesn't appear to be a PDF: {content_type}")
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Successfully downloaded: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def categorize_pdf(self, url: str, filename: str) -> str:
        """Categorize PDF based on URL and filename"""
        url_lower = url.lower()
        filename_lower = filename.lower()
        
        # Check for table-heavy documents (budget plans, financial data)
        if any(keyword in url_lower or keyword in filename_lower for keyword in [
            'einzelplan', 'haushalt', 'budget', 'finanz', 'rechnung', 'ausgaben', 'einnahmen'
        ]):
            return "table_heavy"
        
        # Check for long text documents (reports, explanations)
        if any(keyword in url_lower or keyword in filename_lower for keyword in [
            'bericht', 'erklärung', 'vorheft', 'dokumentation'
        ]):
            return "long_text"
        
        # Default to short text for budget documents
        return "short_text"
    
    def download_budget_pdfs(self, budget_url: str):
        """Download all budget PDFs from the Baden-Württemberg website"""
        print("🚀 Downloading Baden-Württemberg Budget PDFs...")
        print(f"Source: {budget_url}")
        print()
        
        # Get the main page
        html_content = self.get_budget_page(budget_url)
        if not html_content:
            print("❌ Failed to get budget page")
            return
        
        # Extract PDF links
        pdf_links = self.extract_pdf_links(html_content)
        
        if not pdf_links:
            print("❌ No PDF links found on the page")
            print("💡 The page might not contain direct PDF links")
            return
        
        print(f"📄 Found {len(pdf_links)} potential PDF links")
        print()
        
        successful_downloads = 0
        total_attempts = 0
        
        for i, pdf_url in enumerate(pdf_links, 1):
            total_attempts += 1
            
            # Generate filename from URL
            parsed_url = urlparse(pdf_url)
            filename = parsed_url.path.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Clean filename
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            filename = f"bw_budget_{i:02d}_{filename}"
            
            # Categorize the PDF
            category = self.categorize_pdf(pdf_url, filename)
            
            print(f"📄 [{i}/{len(pdf_links)}] {filename}")
            print(f"    URL: {pdf_url}")
            print(f"    Category: {category}")
            
            # Download the PDF
            if self.download_pdf(pdf_url, filename, category):
                successful_downloads += 1
                print(f"    ✅ Downloaded successfully")
            else:
                print(f"    ❌ Download failed")
            
            print()
            time.sleep(1)  # Be nice to the server
        
        print(f"📊 Download Summary:")
        print(f"   Total attempted: {total_attempts}")
        print(f"   Successful: {successful_downloads}")
        print(f"   Failed: {total_attempts - successful_downloads}")
        
        if successful_downloads > 0:
            print(f"\n✅ Successfully downloaded {successful_downloads} budget PDFs!")
            print("📁 Check the benchmarks/ directory for the downloaded files")
        else:
            print("\n❌ No PDFs were successfully downloaded")
            print("💡 The website might require authentication or have different link structures")

def main():
    """Main function"""
    downloader = BWBudgetDownloader()
    
    budget_url = "https://fm.baden-wuerttemberg.de/de/landesfinanzen/landeshaushalt-2025/2026/einzelplaene"
    
    print("🔧 Baden-Württemberg Budget PDF Downloader")
    print("=" * 50)
    print(f"Target URL: {budget_url}")
    print()
    
    # Download budget PDFs
    downloader.download_budget_pdfs(budget_url)
    
    print("\n🔍 Next steps:")
    print("1. Check the downloaded PDFs in the benchmarks/ directories")
    print("2. Run 'python benchmark_runner.py' to test Unstructured performance")
    print("3. Run 'python advanced_analyzer.py' for detailed analysis")

if __name__ == "__main__":
    main() 
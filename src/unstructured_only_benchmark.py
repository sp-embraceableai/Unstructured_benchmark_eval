#!/usr/bin/env python3
"""
Unstructured Performance Benchmark Runner (Unstructured Only)

This script benchmarks Unstructured's performance across different document types:
- Short text documents (<5 pages)
- Long text documents (>20 pages) 
- Table-heavy documents (≥30% tables)
- Image-heavy documents (many charts/scans)

Measures:
- Processing time per document
- Time per page
- GPU vs CPU performance
- Chunk generation analysis
- Image description quality
- Table chunk qualitative comparison
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
from datetime import datetime

# Unstructured imports only
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Table, Text, Image, Title, NarrativeText, 
    ListItem, Address, PageBreak
)

# Optional GPU detection
try:
    import torch
    HAS_GPU = torch.cuda.is_available()
    GPU_COUNT = torch.cuda.device_count() if HAS_GPU else 0
except ImportError:
    HAS_GPU = False
    GPU_COUNT = 0

@dataclass
class BenchmarkResult:
    document_name: str
    document_type: str
    file_path: str
    file_size_mb: float
    page_count: int
    processing_time_seconds: float
    total_elements: int
    text_elements: int
    table_elements: int
    image_elements: int
    chunk_count: int
    avg_chunk_size: float
    table_chunks: Optional[List[str]] = None
    image_chunks: Optional[List[str]] = None
    error: Optional[str] = None

@dataclass
class CategorySummary:
    category: str
    document_count: int
    avg_processing_time: float
    avg_time_per_page: float
    avg_file_size_mb: float
    avg_page_count: float
    total_elements: int
    text_elements: int
    table_elements: int
    image_elements: int
    success_rate: float
    errors: List[str]

class UnstructuredOnlyBenchmark:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.logger = self._setup_logging()
        self.results = []
        
        # Create output directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('benchmark.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def get_document_info(self, file_path: Path) -> Dict[str, Any]:
        """Get basic document information"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(file_path))
            page_count = len(doc)
            doc.close()
        except ImportError:
            # Fallback: estimate page count from file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            page_count = max(1, int(file_size_mb * 2))  # Rough estimate
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        return {
            "file_size_mb": file_size_mb,
            "page_count": page_count
        }

    def analyze_elements(self, elements: List) -> Dict[str, int]:
        """Analyze and count different types of elements"""
        counts = {
            'text': 0,
            'table': 0,
            'image': 0,
            'title': 0,
            'narrative': 0,
            'list_item': 0,
            'address': 0,
            'page_break': 0
        }
        
        for element in elements:
            if isinstance(element, Table):
                counts['table'] += 1
            elif isinstance(element, Image):
                counts['image'] += 1
            elif isinstance(element, Title):
                counts['title'] += 1
            elif isinstance(element, NarrativeText):
                counts['narrative'] += 1
            elif isinstance(element, ListItem):
                counts['list_item'] += 1
            elif isinstance(element, Address):
                counts['address'] += 1
            elif isinstance(element, PageBreak):
                counts['page_break'] += 1
            elif isinstance(element, Text):
                counts['text'] += 1
        
        return counts

    def smart_chunk_text(self, text: str, max_words_per_chunk: int = 500) -> List[str]:
        """
        Smart chunking that respects markdown patterns and combines small chunks
        until reaching the word limit for better readability.
        """
        import re
        
        # Define markdown patterns for splitting
        markdown_patterns = [
            r'^#{1,6}\s+',  # Headers
            r'^\*\s+',      # Bullet points
            r'^\d+\.\s+',   # Numbered lists
            r'^\n+',        # Multiple newlines
            r'^---\s*$',    # Horizontal rules
            r'^```',        # Code blocks
        ]
        
        # Create split pattern
        split_pattern = '|'.join(markdown_patterns)
        
        # Split text by markdown patterns
        initial_chunks = re.split(split_pattern, text)
        initial_chunks = [chunk.strip() for chunk in initial_chunks if chunk.strip()]
        
        # Combine small chunks until reaching word limit
        final_chunks = []
        current_chunk = ""
        current_word_count = 0
        
        for chunk in initial_chunks:
            chunk_words = len(chunk.split())
            
            # If adding this chunk would exceed the limit and we have content, save current chunk
            if current_word_count + chunk_words > max_words_per_chunk and current_chunk:
                final_chunks.append(current_chunk.strip())
                current_chunk = chunk
                current_word_count = chunk_words
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + chunk
                else:
                    current_chunk = chunk
                current_word_count += chunk_words
        
        # Add the last chunk if it exists
        if current_chunk:
            final_chunks.append(current_chunk.strip())
        
        return final_chunks

    def process_document(self, file_path: Path, doc_type: str) -> BenchmarkResult:
        """Process a single document with Unstructured"""
        self.logger.info(f"Processing {file_path.name} ({doc_type})")
        doc_info = self.get_document_info(file_path)

        # Unstructured extraction
        start_time = time.time()
        error = None
        
        try:
            # Use hi_res strategy for better table detection
            elements = partition(str(file_path), strategy="hi_res")
            processing_time_seconds = time.time() - start_time
            
            # Analyze elements
            element_counts = self.analyze_elements(elements)
            total_elements = len(elements)
            text_elements = element_counts.get('text', 0) + element_counts.get('narrative', 0)
            table_elements = element_counts.get('table', 0)
            image_elements = element_counts.get('image', 0)
            
            # Extract all text content and apply smart chunking
            all_text = ""
            table_chunks = []
            image_chunks = []
            
            for element in elements:
                if hasattr(element, 'text') and element.text:
                    if isinstance(element, Table):
                        table_chunks.append(element.text)
                    elif isinstance(element, Image):
                        # Get image description if available
                        image_desc = getattr(element, 'text', 'No description available')
                        image_chunks.append(image_desc)
                    else:
                        all_text += element.text + "\n\n"
            
            # Apply smart chunking to create meaningful chunks
            text_content = self.smart_chunk_text(all_text, max_words_per_chunk=500)
            chunk_count = len(text_content)
            avg_chunk_size = sum(len(chunk.split()) for chunk in text_content) / len(text_content) if text_content else 0
            
        except Exception as e:
            error = str(e)
            processing_time_seconds = None
            total_elements = 0
            text_elements = 0
            table_elements = 0
            image_elements = 0
            text_content = []
            chunk_count = 0
            avg_chunk_size = 0
            table_chunks = []
            image_chunks = []

        return BenchmarkResult(
            document_name=file_path.name,
            document_type=doc_type,
            file_path=str(file_path),
            file_size_mb=doc_info["file_size_mb"],
            page_count=doc_info["page_count"],
            processing_time_seconds=processing_time_seconds,
            total_elements=total_elements,
            text_elements=text_elements,
            table_elements=table_elements,
            image_elements=image_elements,
            chunk_count=chunk_count,
            avg_chunk_size=avg_chunk_size,
            table_chunks=table_chunks,
            image_chunks=image_chunks,
            error=error
        )

    def run_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmarks on all documents in the benchmarks directory"""
        self.logger.info("Starting Unstructured benchmarks...")
        
        if not self.benchmarks_dir.exists():
            self.logger.error(f"Benchmarks directory not found: {self.benchmarks_dir}")
            return []
        
        results = []
        
        # Process each category
        categories = ['short_text', 'long_text', 'table_heavy', 'image_heavy']
        
        for category in categories:
            category_dir = self.benchmarks_dir / category
            if not category_dir.exists():
                self.logger.warning(f"Category directory not found: {category_dir}")
                continue
            
            self.logger.info(f"Processing category: {category}")
            
            # Process all PDFs in the category
            pdf_files = list(category_dir.glob("*.pdf"))
            if not pdf_files:
                self.logger.warning(f"No PDF files found in {category}")
                continue
            
            for pdf_file in pdf_files:
                try:
                    result = self.process_document(pdf_file, category)
                    results.append(result)
                    self.logger.info(f"Completed: {pdf_file.name}")
                except Exception as e:
                    self.logger.error(f"Error processing {pdf_file.name}: {e}")
        
        self.results = results
        return results

    def generate_summary(self) -> Dict[str, CategorySummary]:
        """Generate summary statistics by category"""
        summaries = {}
        
        for category in ['short_text', 'long_text', 'table_heavy', 'image_heavy']:
            category_results = [r for r in self.results if r.document_type == category]
            
            if not category_results:
                continue
            
            # Calculate statistics
            processing_times = [r.processing_time_seconds for r in category_results if r.processing_time_seconds is not None]
            file_sizes = [r.file_size_mb for r in category_results]
            page_counts = [r.page_count for r in category_results]
            
            total_elements = sum(r.total_elements for r in category_results)
            text_elements = sum(r.text_elements for r in category_results)
            table_elements = sum(r.table_elements for r in category_results)
            image_elements = sum(r.image_elements for r in category_results)
            
            errors = [r.error for r in category_results if r.error]
            success_rate = (len(category_results) - len(errors)) / len(category_results) * 100
            
            # Calculate averages
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            avg_file_size = statistics.mean(file_sizes) if file_sizes else 0
            avg_page_count = statistics.mean(page_counts) if page_counts else 0
            
            # Calculate time per page
            total_pages = sum(page_counts)
            avg_time_per_page = avg_processing_time / avg_page_count if avg_page_count > 0 else 0
            
            summaries[category] = CategorySummary(
                category=category,
                document_count=len(category_results),
                avg_processing_time=avg_processing_time,
                avg_time_per_page=avg_time_per_page,
                avg_file_size_mb=avg_file_size,
                avg_page_count=avg_page_count,
                total_elements=total_elements,
                text_elements=text_elements,
                table_elements=table_elements,
                image_elements=image_elements,
                success_rate=success_rate,
                errors=errors
            )
        
        return summaries

    def save_results(self):
        """Save benchmark results to JSON file"""
        results_data = [asdict(result) for result in self.results]
        
        with open("data/unstructured_benchmark_results.json", "w") as f:
            json.dump(results_data, f, indent=2, default=str)
        
        self.logger.info("Results saved to data/unstructured_benchmark_results.json")

    def print_summary(self):
        """Print a summary of benchmark results"""
        if not self.results:
            print("No results to display")
            return
        
        summaries = self.generate_summary()
        
        print("\n" + "="*80)
        print("UNSTRUCTURED BENCHMARK RESULTS")
        print("="*80)
        
        # System information
        print(f"\n🔧 System Information:")
        print(f"   GPU Available: {HAS_GPU}")
        print(f"   GPU Count: {GPU_COUNT}")
        print(f"   Total Documents Processed: {len(self.results)}")
        
        # Category summaries
        for category, summary in summaries.items():
            print(f"\n📁 {category.upper().replace('_', ' ')} ({summary.document_count} documents)")
            print(f"   Success Rate: {summary.success_rate:.1f}%")
            print(f"   Avg Processing Time: {summary.avg_processing_time:.3f}s")
            print(f"   Avg Time per Page: {summary.avg_time_per_page:.3f}s")
            print(f"   Avg File Size: {summary.avg_file_size_mb:.2f}MB")
            print(f"   Avg Page Count: {summary.avg_page_count:.1f}")
            print(f"   Total Elements: {summary.total_elements}")
            print(f"   - Text: {summary.text_elements}")
            print(f"   - Tables: {summary.table_elements}")
            print(f"   - Images: {summary.image_elements}")
            
            if summary.errors:
                print(f"   Errors: {len(summary.errors)}")
                for error in summary.errors[:3]:  # Show first 3 errors
                    print(f"     - {error[:100]}...")
        
        # Overall statistics
        all_processing_times = [r.processing_time_seconds for r in self.results if r.processing_time_seconds is not None]
        if all_processing_times:
            print(f"\n📊 Overall Statistics:")
            print(f"   Total Processing Time: {sum(all_processing_times):.3f}s")
            print(f"   Average Processing Time: {statistics.mean(all_processing_times):.3f}s")
            print(f"   Fastest Document: {min(all_processing_times):.3f}s")
            print(f"   Slowest Document: {max(all_processing_times):.3f}s")
        
        print("\n" + "="*80)

    def generate_report(self):
        """Generate a detailed markdown report"""
        summaries = self.generate_summary()
        
        report = f"""# Unstructured Performance Benchmark Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Information
- **GPU Available**: {HAS_GPU}
- **GPU Count**: {GPU_COUNT}
- **Total Documents Processed**: {len(self.results)}

## Category Analysis

"""
        
        for category, summary in summaries.items():
            report += f"""### {category.replace('_', ' ').title()} ({summary.document_count} documents)

- **Success Rate**: {summary.success_rate:.1f}%
- **Average Processing Time**: {summary.avg_processing_time:.3f}s
- **Average Time per Page**: {summary.avg_time_per_page:.3f}s
- **Average File Size**: {summary.avg_file_size_mb:.2f}MB
- **Average Page Count**: {summary.avg_page_count:.1f}

#### Element Counts
- **Total Elements**: {summary.total_elements}
- **Text Elements**: {summary.text_elements}
- **Table Elements**: {summary.table_elements}
- **Image Elements**: {summary.image_elements}

"""
            
            if summary.errors:
                report += f"#### Errors ({len(summary.errors)})\n"
                for error in summary.errors:
                    report += f"- {error}\n"
                report += "\n"
        
        # Overall statistics
        all_processing_times = [r.processing_time_seconds for r in self.results if r.processing_time_seconds is not None]
        if all_processing_times:
            report += f"""## Overall Statistics

- **Total Processing Time**: {sum(all_processing_times):.3f}s
- **Average Processing Time**: {statistics.mean(all_processing_times):.3f}s
- **Fastest Document**: {min(all_processing_times):.3f}s
- **Slowest Document**: {max(all_processing_times):.3f}s

"""
        
        # Detailed results table
        report += """## Detailed Results

| Document | Type | Size (MB) | Pages | Time (s) | Elements | Text | Tables | Images | Chunks | Avg Chunk Size |
|----------|------|-----------|-------|----------|----------|------|--------|--------|--------|----------------|
"""
        
        for result in self.results:
            report += f"| {result.document_name} | {result.document_type} | {result.file_size_mb:.2f} | {result.page_count} | {result.processing_time_seconds:.3f} | {result.total_elements} | {result.text_elements} | {result.table_elements} | {result.image_elements} | {result.chunk_count} | {result.avg_chunk_size:.1f} |\n"
        
        # Save report
        with open("reports/unstructured_benchmark_report.md", "w") as f:
            f.write(report)
        
        self.logger.info("Report saved to reports/unstructured_benchmark_report.md")

def main():
    """Main function to run the benchmark"""
    benchmark = UnstructuredOnlyBenchmark()
    
    # Run benchmarks
    results = benchmark.run_benchmarks()
    
    if results:
        # Save results
        benchmark.save_results()
        
        # Print summary
        benchmark.print_summary()
        
        # Generate report
        benchmark.generate_report()
        
        print(f"\n✅ Benchmark completed! Processed {len(results)} documents.")
        print("📁 Results saved to:")
        print("   - data/unstructured_benchmark_results.json")
        print("   - reports/unstructured_benchmark_report.md")
        print("   - benchmark.log")
    else:
        print("❌ No documents were processed. Check the benchmarks directory.")

if __name__ == "__main__":
    main() 
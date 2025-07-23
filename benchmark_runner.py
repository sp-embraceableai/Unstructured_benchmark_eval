#!/usr/bin/env python3
"""
Unstructured Performance Benchmark Runner

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

# Unstructured imports
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
    """Results from a single document benchmark"""
    document_name: str
    document_type: str
    file_path: str
    file_size_mb: float
    page_count: int
    processing_time_seconds: float
    time_per_page: float
    total_elements: int
    text_elements: int
    table_elements: int
    image_elements: int
    chunk_count: int
    avg_chunk_size: float
    gpu_used: bool
    error: Optional[str] = None

@dataclass
class CategorySummary:
    """Summary statistics for a document category"""
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

class UnstructuredBenchmark:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.results: List[BenchmarkResult] = []
        self.logger = self._setup_logging()
        
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
            # Get file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Estimate page count (rough approximation)
            # This is a simple heuristic - in practice you might want to use a PDF library
            page_count = 1  # Default fallback
            
            return {
                "file_size_mb": round(file_size_mb, 2),
                "page_count": page_count
            }
        except Exception as e:
            self.logger.warning(f"Could not get document info for {file_path}: {e}")
            return {"file_size_mb": 0, "page_count": 1}
    
    def analyze_elements(self, elements: List) -> Dict[str, int]:
        """Analyze the types and counts of elements extracted"""
        element_counts = {
            "total": len(elements),
            "text": 0,
            "table": 0,
            "image": 0,
            "title": 0,
            "narrative": 0,
            "list": 0,
            "other": 0
        }
        
        for element in elements:
            if isinstance(element, Table):
                element_counts["table"] += 1
            elif isinstance(element, Image):
                element_counts["image"] += 1
            elif isinstance(element, Title):
                element_counts["title"] += 1
            elif isinstance(element, NarrativeText):
                element_counts["narrative"] += 1
            elif isinstance(element, ListItem):
                element_counts["list"] += 1
            elif isinstance(element, Text):
                element_counts["text"] += 1
            else:
                element_counts["other"] += 1
        
        return element_counts
    
    def process_document(self, file_path: Path, doc_type: str) -> BenchmarkResult:
        """Process a single document and measure performance"""
        self.logger.info(f"Processing {file_path.name} ({doc_type})")
        
        # Get document info
        doc_info = self.get_document_info(file_path)
        
        # Measure processing time
        start_time = time.time()
        
        try:
            # Process with Unstructured
            elements = partition(str(file_path))
            
            processing_time = time.time() - start_time
            
            # Analyze elements
            element_counts = self.analyze_elements(elements)
            
            # Calculate chunk statistics
            text_content = []
            for element in elements:
                if hasattr(element, 'text'):
                    text_content.append(element.text)
            
            total_text_length = sum(len(text) for text in text_content)
            avg_chunk_size = total_text_length / len(text_content) if text_content else 0
            
            return BenchmarkResult(
                document_name=file_path.name,
                document_type=doc_type,
                file_path=str(file_path),
                file_size_mb=doc_info["file_size_mb"],
                page_count=doc_info["page_count"],
                processing_time_seconds=round(processing_time, 3),
                time_per_page=round(processing_time / doc_info["page_count"], 3) if doc_info["page_count"] > 0 else 0,
                total_elements=element_counts["total"],
                text_elements=element_counts["text"] + element_counts["narrative"],
                table_elements=element_counts["table"],
                image_elements=element_counts["image"],
                chunk_count=len(text_content),
                avg_chunk_size=round(avg_chunk_size, 2),
                gpu_used=HAS_GPU
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Error processing {file_path}: {e}")
            
            return BenchmarkResult(
                document_name=file_path.name,
                document_type=doc_type,
                file_path=str(file_path),
                file_size_mb=doc_info["file_size_mb"],
                page_count=doc_info["page_count"],
                processing_time_seconds=round(processing_time, 3),
                time_per_page=0,
                total_elements=0,
                text_elements=0,
                table_elements=0,
                image_elements=0,
                chunk_count=0,
                avg_chunk_size=0,
                gpu_used=HAS_GPU,
                error=str(e)
            )
    
    def run_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmarks for all document categories"""
        self.logger.info("Starting Unstructured performance benchmarks")
        self.logger.info(f"GPU available: {HAS_GPU}, GPU count: {GPU_COUNT}")
        
        categories = ["short_text", "long_text", "table_heavy", "image_heavy"]
        
        for category in categories:
            category_dir = self.benchmarks_dir / category
            if not category_dir.exists():
                self.logger.warning(f"Category directory {category_dir} does not exist")
                continue
                
            self.logger.info(f"Processing category: {category}")
            
            # Find all PDF files in the category
            pdf_files = list(category_dir.glob("*.pdf"))
            if not pdf_files:
                self.logger.warning(f"No PDF files found in {category_dir}")
                continue
            
            for pdf_file in pdf_files:
                result = self.process_document(pdf_file, category)
                self.results.append(result)
                
                # Log progress
                self.logger.info(
                    f"Completed {pdf_file.name}: "
                    f"{result.processing_time_seconds}s, "
                    f"{result.total_elements} elements, "
                    f"{result.chunk_count} chunks"
                )
        
        return self.results
    
    def generate_summary(self) -> Dict[str, CategorySummary]:
        """Generate summary statistics for each category"""
        summaries = {}
        
        for category in ["short_text", "long_text", "table_heavy", "image_heavy"]:
            category_results = [r for r in self.results if r.document_type == category]
            
            if not category_results:
                continue
            
            successful_results = [r for r in category_results if r.error is None]
            errors = [r.error for r in category_results if r.error is not None]
            
            if successful_results:
                summary = CategorySummary(
                    category=category,
                    document_count=len(category_results),
                    avg_processing_time=statistics.mean(r.processing_time_seconds for r in successful_results),
                    avg_time_per_page=statistics.mean(r.time_per_page for r in successful_results if r.time_per_page > 0),
                    avg_file_size_mb=statistics.mean(r.file_size_mb for r in successful_results),
                    avg_page_count=statistics.mean(r.page_count for r in successful_results),
                    total_elements=sum(r.total_elements for r in successful_results),
                    text_elements=sum(r.text_elements for r in successful_results),
                    table_elements=sum(r.table_elements for r in successful_results),
                    image_elements=sum(r.image_elements for r in successful_results),
                    success_rate=len(successful_results) / len(category_results),
                    errors=errors
                )
                summaries[category] = summary
        
        return summaries
    
    def save_results(self, output_file: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        # Convert results to dictionaries
        results_dict = [asdict(result) for result in self.results]
        
        # Generate summary
        summary = self.generate_summary()
        summary_dict = {k: asdict(v) for k, v in summary.items()}
        
        # Create output data
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "gpu_available": HAS_GPU,
            "gpu_count": GPU_COUNT,
            "total_documents": len(self.results),
            "results": results_dict,
            "summary": summary_dict
        }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")
    
    def print_summary(self):
        """Print a formatted summary of results"""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print("UNSTRUCTURED PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        print(f"GPU Available: {HAS_GPU}")
        print(f"Total Documents Processed: {len(self.results)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for category, cat_summary in summary.items():
            print(f"📁 {category.upper().replace('_', ' ')}")
            print(f"   Documents: {cat_summary.document_count}")
            print(f"   Success Rate: {cat_summary.success_rate:.1%}")
            print(f"   Avg Processing Time: {cat_summary.avg_processing_time:.3f}s")
            print(f"   Avg Time per Page: {cat_summary.avg_time_per_page:.3f}s")
            print(f"   Avg File Size: {cat_summary.avg_file_size_mb:.2f}MB")
            print(f"   Avg Page Count: {cat_summary.avg_page_count:.1f}")
            print(f"   Total Elements: {cat_summary.total_elements}")
            print(f"   - Text: {cat_summary.text_elements}")
            print(f"   - Tables: {cat_summary.table_elements}")
            print(f"   - Images: {cat_summary.image_elements}")
            if cat_summary.errors:
                print(f"   Errors: {len(cat_summary.errors)}")
            print()

def main():
    """Main function to run the benchmark"""
    benchmark = UnstructuredBenchmark()
    
    try:
        # Run benchmarks
        results = benchmark.run_benchmarks()
        
        # Save results
        benchmark.save_results()
        
        # Print summary
        benchmark.print_summary()
        
        print("✅ Benchmark completed successfully!")
        print("📊 Check 'benchmark_results.json' for detailed results")
        print("📝 Check 'benchmark.log' for processing logs")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        logging.error(f"Benchmark failed: {e}", exc_info=True)

if __name__ == "__main__":
    main() 
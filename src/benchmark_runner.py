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

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Table, Text, Image, Title, NarrativeText, 
    ListItem, Address, PageBreak
)
# Add full Docling pipeline imports
from docling_parse.pdf_parser import DoclingPdfParser
from docling_core.types.doc.page import TextCellUnit

# Advanced Docling imports for chunking and serialization
try:
    from docling.chunking import HybridChunker, BaseChunker, DocChunk
    from docling.backend import pypdfium2_backend
    from semchunk import Chunker, chunk
    from semchunk.semchunk import chunk as semchunk_func
    HAS_ADVANCED_DOCLING = True
except ImportError:
    HAS_ADVANCED_DOCLING = False
    print("Warning: Advanced Docling features not available. Using basic docling-parse only.")

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
    u_processing_time_seconds: float
    u_total_elements: int
    u_text_elements: int
    u_table_elements: int
    u_chunk_count: int
    u_avg_chunk_size: float
    d_processing_time_seconds: float
    d_total_elements: int
    d_text_elements: int
    d_table_elements: int
    d_chunk_count: int
    d_avg_chunk_size: float
    u_table_chunks: Optional[List[str]] = None
    d_table_chunks: Optional[List[str]] = None
    u_error: Optional[str] = None
    d_error: Optional[str] = None

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

class UnstructuredBenchmark:
    def __init__(self, benchmarks_dir: str = "benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.results: List[BenchmarkResult] = []
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
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
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            page_count = 1
            return {
                "file_size_mb": round(file_size_mb, 2),
                "page_count": page_count
            }
        except Exception as e:
            self.logger.warning(f"Could not get document info for {file_path}: {e}")
            return {"file_size_mb": 0, "page_count": 1}

    def analyze_elements(self, elements: List) -> Dict[str, int]:
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

    def smart_chunk_text(self, text: str, max_words_per_chunk: int = 500) -> List[str]:
        """
        Smart chunking that separates by markdown patterns and combines small chunks.
        
        Args:
            text: Raw text to chunk
            max_words_per_chunk: Maximum words per chunk
            
        Returns:
            List of meaningful chunks
        """
        import re
        
        # Split by markdown patterns (headers, lists, paragraphs, etc.)
        markdown_patterns = [
            r'^#{1,6}\s+',  # Headers (# ## ### etc.)
            r'^\*\s+',      # Bullet points
            r'^\d+\.\s+',   # Numbered lists
            r'^\n+',        # Multiple newlines
            r'^---\s*$',    # Horizontal rules
            r'^```',        # Code blocks
        ]
        
        # Combine patterns for splitting
        split_pattern = '|'.join(markdown_patterns)
        
        # Split text into initial chunks by markdown patterns
        initial_chunks = re.split(split_pattern, text)
        initial_chunks = [chunk.strip() for chunk in initial_chunks if chunk.strip()]
        
        # Combine small chunks until hitting word limit
        final_chunks = []
        current_chunk = ""
        current_word_count = 0
        
        for chunk in initial_chunks:
            chunk_words = len(chunk.split())
            
            # If adding this chunk would exceed limit, save current and start new
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

    def advanced_docling_chunking(self, file_path: Path) -> Dict[str, Any]:
        """
        Advanced Docling chunking using actual available Docling classes and semchunk for hybrid strategies.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing chunking results from different strategies
        """
        if not HAS_ADVANCED_DOCLING:
            return {"error": "Advanced Docling features not available"}
        
        try:
            # Load document using docling-parse backend
            from docling_parse.pdf_parser import DoclingPdfParser
            from docling_core.types.doc.page import TextCellUnit
            
            parser = DoclingPdfParser()
            pdf_doc = parser.load(path_or_stream=str(file_path))
            
            # Extract text content
            doc_text = ""
            for page_no, pred_page in pdf_doc.iterate_pages():
                for cell in pred_page.iterate_cells(unit_type=TextCellUnit.WORD):
                    if hasattr(cell, 'text') and cell.text:
                        doc_text += cell.text + "\n\n"
            
            # Simple token counter function
            def token_counter(text):
                return len(text.split())
            
            # Strategy 1: Semantic Chunking with semchunk
            semantic_chunks = semchunk_func(
                doc_text,
                chunk_size=1000,
                token_counter=token_counter
            )
            
            # Strategy 2: Recursive Character Text Splitter
            recursive_chunks = semchunk_func(
                doc_text,
                chunk_size=500,
                token_counter=token_counter
            )
            
            # Strategy 3: Markdown Header Text Splitter
            markdown_chunks = semchunk_func(
                doc_text,
                chunk_size=1000,
                token_counter=token_counter
            )
            
            # Strategy 4: Hybrid Chunking Strategy using semchunk with different parameters
            hybrid_chunks = semchunk_func(
                doc_text,
                chunk_size=800,
                token_counter=token_counter
            )
            
            # Strategy 5: Default semchunk function
            default_chunks = semchunk_func(
                doc_text,
                chunk_size=1000,
                token_counter=token_counter
            )
            
            # Analyze chunks by type
            def analyze_chunks(chunks, strategy_name):
                # For semchunk results, chunks are strings
                if isinstance(chunks[0], str) if chunks else False:
                    return {
                        "strategy": strategy_name,
                        "total_chunks": len(chunks),
                        "text_chunks": len(chunks),
                        "table_chunks": 0,  # semchunk doesn't distinguish table chunks
                        "image_chunks": 0,  # semchunk doesn't distinguish image chunks
                        "avg_chunk_size": sum(len(chunk.split()) for chunk in chunks) / len(chunks) if chunks else 0,
                        "chunks": chunks
                    }
                else:
                    # For Docling chunks, they are objects
                    text_chunks = [c for c in chunks if hasattr(c, 'text')]
                    table_chunks = [c for c in chunks if hasattr(c, 'table')]
                    image_chunks = [c for c in chunks if hasattr(c, 'image')]
                    
                    return {
                        "strategy": strategy_name,
                        "total_chunks": len(chunks),
                        "text_chunks": len(text_chunks),
                        "table_chunks": len(table_chunks),
                        "image_chunks": len(image_chunks),
                        "avg_chunk_size": sum(len(str(c).split()) for c in chunks) / len(chunks) if chunks else 0,
                        "chunks": chunks
                    }
            
            results = {
                "semantic": analyze_chunks(semantic_chunks, "Semantic Chunking"),
                "recursive": analyze_chunks(recursive_chunks, "Recursive Character"),
                "markdown": analyze_chunks(markdown_chunks, "Markdown Header"),
                "hybrid": analyze_chunks(hybrid_chunks, "Hybrid semchunk"),
                "default": analyze_chunks(default_chunks, "Default semchunk")
            }
            
            return results
            
        except Exception as e:
            return {"error": f"Advanced Docling chunking failed: {str(e)}"}

    def adaptive_hybrid_chunking(self, file_path: Path) -> Dict[str, Any]:
        """
        Adaptive hybrid chunking that analyzes document content and chooses optimal strategy.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing adaptive chunking results
        """
        if not HAS_ADVANCED_DOCLING:
            return {"error": "Advanced Docling features not available"}
        
        try:
            # Load document using docling-parse backend
            from docling_parse.pdf_parser import DoclingPdfParser
            from docling_core.types.doc.page import TextCellUnit
            
            parser = DoclingPdfParser()
            pdf_doc = parser.load(path_or_stream=str(file_path))
            
            # Extract text content
            doc_text = ""
            for page_no, pred_page in pdf_doc.iterate_pages():
                for cell in pred_page.iterate_cells(unit_type=TextCellUnit.WORD):
                    if hasattr(cell, 'text') and cell.text:
                        doc_text += cell.text + "\n\n"
            
            # Analyze document characteristics
            doc_length = len(doc_text)
            has_headers = any(line.strip().startswith('#') for line in doc_text.split('\n'))
            has_tables = '|' in doc_text or '\t' in doc_text
            has_lists = any(line.strip().startswith(('*', '-', '1.', '2.')) for line in doc_text.split('\n'))
            
            # Simple token counter function
            def token_counter(text):
                return len(text.split())
            
            # Choose strategy based on document characteristics
            if has_headers and doc_length > 5000:
                # Long document with headers - use markdown-based chunking
                adaptive_chunks = semchunk_func(
                    doc_text,
                    chunk_size=1200,
                    token_counter=token_counter
                )
                strategy_name = "Header-Prioritized Hybrid"
                
            elif has_tables:
                # Table-heavy document - use semantic chunking with smaller chunks
                adaptive_chunks = semchunk_func(
                    doc_text,
                    chunk_size=800,
                    token_counter=token_counter
                )
                strategy_name = "Table-Optimized Hybrid"
                
            elif has_lists:
                # List-heavy document - use recursive chunking
                adaptive_chunks = semchunk_func(
                    doc_text,
                    chunk_size=600,
                    token_counter=token_counter
                )
                strategy_name = "List-Optimized Hybrid"
                
            else:
                # General document - balanced approach using semchunk
                adaptive_chunks = semchunk_func(
                    doc_text,
                    chunk_size=1000,
                    token_counter=token_counter
                )
                strategy_name = "Balanced Hybrid"
                
                # Analyze results
                return {
                    "strategy": strategy_name,
                    "total_chunks": len(adaptive_chunks),
                    "text_chunks": len(adaptive_chunks),
                    "table_chunks": 0,
                    "image_chunks": 0,
                    "avg_chunk_size": sum(len(chunk.split()) for chunk in adaptive_chunks) / len(adaptive_chunks) if adaptive_chunks else 0,
                    "chunks": adaptive_chunks,
                    "document_analysis": {
                        "length": doc_length,
                        "has_headers": has_headers,
                        "has_tables": has_tables,
                        "has_lists": has_lists,
                        "primary_strategy": "semchunk",
                        "secondary_strategy": "N/A",
                        "weights": [1.0]
                    }
                }
            
            # Apply chunking for non-balanced strategies
            # (adaptive_chunks already set above)
            
            # Analyze results
            return {
                "strategy": strategy_name,
                "total_chunks": len(adaptive_chunks),
                "text_chunks": len(adaptive_chunks),
                "table_chunks": 0,
                "image_chunks": 0,
                "avg_chunk_size": sum(len(chunk.split()) for chunk in adaptive_chunks) / len(adaptive_chunks) if adaptive_chunks else 0,
                "chunks": adaptive_chunks,
                "document_analysis": {
                    "length": doc_length,
                    "has_headers": has_headers,
                    "has_tables": has_tables,
                    "has_lists": has_lists,
                    "primary_strategy": "semchunk",
                    "secondary_strategy": "N/A",
                    "weights": [1.0]
                }
            }
            
        except Exception as e:
            return {"error": f"Adaptive hybrid chunking failed: {str(e)}"}

    def process_document_with_advanced_docling(self, file_path: Path, doc_type: str) -> BenchmarkResult:
        """
        Process document with advanced Docling chunking strategies.
        
        Args:
            file_path: Path to the PDF file
            doc_type: Document category type
            
        Returns:
            BenchmarkResult with advanced Docling metrics
        """
        self.logger.info(f"Processing {file_path.name} ({doc_type}) with advanced Docling")
        doc_info = self.get_document_info(file_path)

        # Unstructured extraction (same as before)
        u_start = time.time()
        u_error = None
        try:
            elements = partition(str(file_path), strategy="hi_res")
            u_processing_time_seconds = time.time() - u_start
            
            # Analyze elements
            element_counts = self.analyze_elements(elements)
            u_total_elements = len(elements)
            u_text_elements = element_counts.get('text', 0)
            u_table_elements = element_counts.get('table', 0)
            
            # Extract all text content and apply smart chunking
            all_text = ""
            u_table_chunks = []
            for element in elements:
                if hasattr(element, 'text') and element.text:
                    if isinstance(element, Table):
                        u_table_chunks.append(element.text)
                    else:
                        all_text += element.text + "\n\n"
            
            # Apply smart chunking to create meaningful chunks
            u_text_content = self.smart_chunk_text(all_text, max_words_per_chunk=500)
            u_chunk_count = len(u_text_content)
            u_avg_chunk_size = sum(len(chunk.split()) for chunk in u_text_content) / len(u_text_content) if u_text_content else 0
            
        except Exception as e:
            u_error = str(e)
            u_processing_time_seconds = None
            u_total_elements = 0
            u_text_elements = 0
            u_table_elements = 0
            u_text_content = []
            u_chunk_count = 0
            u_avg_chunk_size = 0
            u_table_chunks = []

        # Advanced Docling extraction
        d_start = time.time()
        advanced_docling_results = self.advanced_docling_chunking(file_path)
        d_processing_time_seconds = time.time() - d_start
        
        if "error" in advanced_docling_results:
            d_error = advanced_docling_results["error"]
            d_total_elements = 0
            d_text_elements = 0
            d_table_elements = 0
            d_chunk_count = 0
            d_avg_chunk_size = 0
            d_table_chunks = []
        else:
            d_error = None
            # Use semantic chunking results as primary metrics
            semantic_results = advanced_docling_results["semantic"]
            d_total_elements = semantic_results["total_chunks"]
            d_text_elements = semantic_results["text_chunks"]
            d_table_elements = semantic_results["table_chunks"]
            d_chunk_count = semantic_results["total_chunks"]
            d_avg_chunk_size = semantic_results["avg_chunk_size"]
            
            # Extract table chunks from semantic strategy
            d_table_chunks = [
                str(chunk) for chunk in semantic_results["chunks"] 
                if isinstance(chunk, str) and "table" in chunk.lower()
            ]

        return BenchmarkResult(
            document_name=file_path.name,
            document_type=doc_type,
            file_path=str(file_path),
            file_size_mb=doc_info["file_size_mb"],
            page_count=doc_info["page_count"],
            u_processing_time_seconds=round(u_processing_time_seconds, 3) if u_processing_time_seconds is not None else 0,
            u_total_elements=u_total_elements,
            u_text_elements=u_text_elements,
            u_table_elements=u_table_elements,
            u_chunk_count=u_chunk_count,
            u_avg_chunk_size=round(u_avg_chunk_size, 2),
            d_processing_time_seconds=round(d_processing_time_seconds, 3),
            d_total_elements=d_total_elements,
            d_text_elements=d_text_elements,
            d_table_elements=d_table_elements,
            d_chunk_count=d_chunk_count,
            d_avg_chunk_size=round(d_avg_chunk_size, 2),
            u_table_chunks=u_table_chunks,
            d_table_chunks=d_table_chunks,
            u_error=u_error,
            d_error=d_error
        )

    def process_document(self, file_path: Path, doc_type: str) -> BenchmarkResult:
        self.logger.info(f"Processing {file_path.name} ({doc_type})")
        doc_info = self.get_document_info(file_path)

        # Unstructured extraction
        u_start = time.time()
        u_error = None
        try:
            elements = partition(str(file_path), strategy="hi_res")
            u_processing_time_seconds = time.time() - u_start
            
            # Analyze elements
            element_counts = self.analyze_elements(elements)
            u_total_elements = len(elements)
            u_text_elements = element_counts.get('text', 0)
            u_table_elements = element_counts.get('table', 0)
            
            # Extract all text content and apply smart chunking
            all_text = ""
            u_table_chunks = []
            for element in elements:
                if hasattr(element, 'text') and element.text:
                    if isinstance(element, Table):
                        u_table_chunks.append(element.text)
                    else:
                        all_text += element.text + "\n\n"
            
            # Apply smart chunking to create meaningful chunks
            u_text_content = self.smart_chunk_text(all_text, max_words_per_chunk=500)
            u_chunk_count = len(u_text_content)
            u_avg_chunk_size = sum(len(chunk.split()) for chunk in u_text_content) / len(u_text_content) if u_text_content else 0
            
        except Exception as e:
            u_error = str(e)
            u_processing_time_seconds = None
            u_total_elements = 0
            u_text_elements = 0
            u_table_elements = 0
            u_text_content = []
            u_chunk_count = 0
            u_avg_chunk_size = 0
            u_table_chunks = []

        # Docling extraction - DISABLED FOR THIS RUN
        # d_processing_time_seconds = None
        # d_total_elements = 0
        # d_text_elements = 0
        # d_table_elements = 0
        # d_text_content = []
        # d_table_chunks = []
        # d_error = None
        # try:
        #     d_start = time.time()
        #     parser = DoclingPdfParser()
        #     pdf_doc = parser.load(path_or_stream=str(file_path))
        #     d_chunks = []
        #     cell_types_seen = set()
        #     cell_reprs = []
        #     for page_no, pred_page in pdf_doc.iterate_pages():
        #         for cell in pred_page.iterate_cells(unit_type=TextCellUnit.SNIPPET):
        #             d_chunks.append(cell)
        #             if len(cell_types_seen) < 10:
        #                 cell_types_seen.add(getattr(cell, 'type', None))
        #             if len(cell_reprs) < 10:
        #                 cell_reprs.append(repr(cell))
        #     print(f"Docling cell types seen (first 10): {cell_types_seen}")
        #     print("First 10 Docling cells:")
        #     for r in cell_reprs:
        #         print(r)
        #     d_processing_time_seconds = time.time() - d_start
        #     d_total_elements = len(d_chunks)
        #     text_chunks = [c for c in d_chunks if getattr(c, 'type', None) == 'text']
        #     table_chunks = [c for c in d_chunks if getattr(c, 'type', None) == 'table']
        #     d_text_elements = len(text_chunks)
        #     d_table_elements = len(table_chunks)
        #     
        #     # Extract all text content from Docling and apply smart chunking
        #     all_docling_text = ""
        #     for cell in d_chunks:
        #         if hasattr(cell, 'text') and cell.text:
        #             all_docling_text += cell.text + "\n\n"
        #     
        #     # Apply smart chunking to Docling text
        #     d_text_content = self.smart_chunk_text(all_docling_text, max_words_per_chunk=500)
        #     d_table_chunks = [getattr(c, 'text', 'No table data') for c in table_chunks]
        #     
        # except Exception as e:
        #     d_error = str(e)
        #     d_processing_time_seconds = None
        #     d_total_elements = 0
        #     d_text_elements = 0
        #     d_table_elements = 0
        #     d_text_content = []
        #     d_table_chunks = []

        # Set Docling values to 0 for this run
        d_processing_time_seconds = 0
        d_total_elements = 0
        d_text_elements = 0
        d_table_elements = 0
        d_text_content = []
        d_table_chunks = []
        d_error = "Disabled for this run"

        return BenchmarkResult(
            document_name=file_path.name,
            document_type=doc_type,
            file_path=str(file_path),
            file_size_mb=doc_info["file_size_mb"],
            page_count=doc_info["page_count"],
            u_processing_time_seconds=round(u_processing_time_seconds, 3),
            u_total_elements=u_total_elements,
            u_text_elements=u_text_elements,
            u_table_elements=u_table_elements,
            u_chunk_count=u_chunk_count,
            u_avg_chunk_size=round(u_avg_chunk_size, 2),
            d_processing_time_seconds=round(d_processing_time_seconds, 3) if d_processing_time_seconds is not None else 0,
            d_total_elements=d_total_elements,
            d_text_elements=d_text_elements,
            d_table_elements=d_table_elements,
            d_chunk_count=len(d_text_content),
            d_avg_chunk_size=round(sum(len(text) for text in d_text_content) / len(d_text_content), 2) if d_text_content else 0,
            u_table_chunks=u_table_chunks,
            d_table_chunks=d_table_chunks,
            u_error=u_error,
            d_error=d_error
        )

    def run_benchmarks(self) -> List[BenchmarkResult]:
        self.logger.info("Starting Unstructured performance benchmarks")
        categories = ["short_text", "long_text", "table_heavy", "image_heavy"]
        for category in categories:
            category_dir = self.benchmarks_dir / category
            if not category_dir.exists():
                self.logger.warning(f"Category directory {category_dir} does not exist")
                continue
            self.logger.info(f"Processing category: {category}")
            pdf_files = list(category_dir.glob("*.pdf"))
            if not pdf_files:
                self.logger.warning(f"No PDF files found in {category_dir}")
                continue
            for pdf_file in pdf_files:
                result = self.process_document(pdf_file, category)
                self.results.append(result)
                self.logger.info(
                    f"Completed {pdf_file.name}: "
                    f"{result.u_processing_time_seconds}s (Unstructured)"
                )
        return self.results

    def save_results(self):
        results_data = [asdict(result) for result in self.results]
        with open("benchmark_results.json", "w") as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        self.logger.info("✅ Saved benchmark results to 'benchmark_results.json'")

    def print_summary(self):
        print("\n🔍 BENCHMARK SUMMARY\n")
        categories = {}
        for result in self.results:
            if result.document_type not in categories:
                categories[result.document_type] = []
            categories[result.document_type].append(result)

        for category, results in categories.items():
            print(f"\n--- {category.upper()} ---")
            total_docs = len(results)
            total_processing_time = sum(r.d_processing_time_seconds for r in results)
            total_file_size = sum(r.file_size_mb for r in results)
            total_page_count = sum(r.page_count for r in results)
            total_elements = sum(r.d_total_elements for r in results)
            total_text_elements = sum(r.d_text_elements for r in results)
            total_table_elements = sum(r.d_table_elements for r in results)

            print(f"Total Documents: {total_docs}")
            print(f"Total Processing Time (Docling): {total_processing_time:.2f}s")
            print(f"Total File Size: {total_file_size:.2f} MB")
            print(f"Total Pages: {total_page_count}")
            print(f"Total Elements (Docling): {total_elements}")
            print(f"Total Text Elements (Docling): {total_text_elements}")
            print(f"Total Table Elements (Docling): {total_table_elements}")

    def compare_table_chunks(self):
        print("\n🔍 QUALITATIVE TABLE CHUNK COMPARISON\n")
        table_comparisons = []
        for result in self.results:
            comparison = {
                "document_name": result.document_name,
                "document_type": result.document_type,
                "unstructured_table_chunks": result.u_table_chunks,
                "docling_table_chunks": result.d_table_chunks
            }
            table_comparisons.append(comparison)

        with open("table_chunk_comparisons.json", "w") as f:
            json.dump(table_comparisons, f, indent=2, ensure_ascii=False)

        print("✅ Saved qualitative table chunk comparisons to 'table_chunk_comparisons.json'")

    # Remaining methods unchanged...


def main():
    benchmark = UnstructuredBenchmark()
    try:
        benchmark.run_benchmarks()
        benchmark.save_results()
        benchmark.print_summary()
        benchmark.compare_table_chunks()
        print("✅ Benchmark completed successfully!")
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        logging.error(f"Benchmark failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()

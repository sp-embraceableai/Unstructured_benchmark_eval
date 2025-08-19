#!/usr/bin/env python3
"""
Extract and analyze chunks from a single document using Unstructured

This script demonstrates how to:
- Extract elements from a PDF using Unstructured
- Apply smart chunking
- Analyze chunk quality and content
- Compare different chunking strategies
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any
import re

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Table, Text, Image, Title, NarrativeText, 
    ListItem, Address, PageBreak
)

def analyze_elements(elements: List) -> Dict[str, int]:
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

def smart_chunk_text(text: str, max_words_per_chunk: int = 500) -> List[str]:
    """
    Smart chunking that respects markdown patterns and combines small chunks
    until reaching the word limit for better readability.
    """
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

def simple_chunk_text(text: str, max_words_per_chunk: int = 500) -> List[str]:
    """
    Simple chunking by word count without considering document structure.
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_words_per_chunk):
        chunk_words = words[i:i + max_words_per_chunk]
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
    
    return chunks

def analyze_chunk_quality(chunks: List[str]) -> Dict[str, float]:
    """Analyze the quality of chunks"""
    if not chunks:
        return {}
    
    # Calculate average chunk size
    chunk_sizes = [len(chunk.split()) for chunk in chunks]
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
    
    # Calculate chunk size variance (consistency)
    variance = sum((size - avg_chunk_size) ** 2 for size in chunk_sizes) / len(chunk_sizes)
    
    # Calculate readability (simple word length metric)
    total_words = sum(chunk_sizes)
    total_chars = sum(len(chunk) for chunk in chunks)
    avg_word_length = total_chars / total_words if total_words > 0 else 0
    
    # Calculate completeness (percentage of chunks that end with sentence endings)
    sentence_endings = ['.', '!', '?']
    complete_chunks = sum(1 for chunk in chunks if any(chunk.strip().endswith(end) for end in sentence_endings))
    completeness = complete_chunks / len(chunks) if chunks else 0
    
    return {
        'avg_chunk_size': avg_chunk_size,
        'chunk_size_variance': variance,
        'avg_word_length': avg_word_length,
        'completeness': completeness,
        'total_chunks': len(chunks)
    }

def extract_document_chunks(file_path: str, strategy: str = "hi_res") -> Dict[str, Any]:
    """
    Extract and analyze chunks from a document using Unstructured
    
    Args:
        file_path: Path to the PDF file
        strategy: Unstructured partition strategy ("hi_res", "fast", etc.)
    
    Returns:
        Dictionary containing extraction results and analysis
    """
    print(f"🔍 Processing: {file_path}")
    print(f"📋 Strategy: {strategy}")
    
    start_time = time.time()
    
    try:
        # Extract elements using Unstructured
        elements = partition(file_path, strategy=strategy)
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.3f}s")
        
        # Analyze elements
        element_counts = analyze_elements(elements)
        print(f"📊 Elements found:")
        for element_type, count in element_counts.items():
            if count > 0:
                print(f"   - {element_type}: {count}")
        
        # Extract text content
        all_text = ""
        table_chunks = []
        image_chunks = []
        
        for element in elements:
            if hasattr(element, 'text') and element.text:
                if isinstance(element, Table):
                    table_chunks.append(element.text)
                elif isinstance(element, Image):
                    image_desc = getattr(element, 'text', 'No description available')
                    image_chunks.append(image_desc)
                else:
                    all_text += element.text + "\n\n"
        
        print(f"📝 Total text length: {len(all_text)} characters")
        print(f"📋 Tables found: {len(table_chunks)}")
        print(f"🖼️  Images found: {len(image_chunks)}")
        
        # Apply different chunking strategies
        print(f"\n🔧 Applying chunking strategies...")
        
        # Smart chunking
        smart_chunks = smart_chunk_text(all_text, max_words_per_chunk=500)
        smart_quality = analyze_chunk_quality(smart_chunks)
        
        # Simple chunking
        simple_chunks = simple_chunk_text(all_text, max_words_per_chunk=500)
        simple_quality = analyze_chunk_quality(simple_chunks)
        
        # Large chunking
        large_chunks = smart_chunk_text(all_text, max_words_per_chunk=1000)
        large_quality = analyze_chunk_quality(large_chunks)
        
        # Small chunking
        small_chunks = smart_chunk_text(all_text, max_words_per_chunk=250)
        small_quality = analyze_chunk_quality(small_chunks)
        
        results = {
            'file_path': file_path,
            'strategy': strategy,
            'processing_time': processing_time,
            'element_counts': element_counts,
            'total_text_length': len(all_text),
            'table_chunks': table_chunks,
            'image_chunks': image_chunks,
            'chunking_results': {
                'smart_500': {
                    'chunks': smart_chunks,
                    'quality': smart_quality
                },
                'simple_500': {
                    'chunks': simple_chunks,
                    'quality': simple_quality
                },
                'large_1000': {
                    'chunks': large_chunks,
                    'quality': large_quality
                },
                'small_250': {
                    'chunks': small_chunks,
                    'quality': small_quality
                }
            }
        }
        
        return results
        
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return {
            'file_path': file_path,
            'error': str(e),
            'processing_time': time.time() - start_time
        }

def print_chunk_analysis(results: Dict[str, Any]):
    """Print detailed chunk analysis"""
    if 'error' in results:
        print(f"❌ Processing failed: {results['error']}")
        return
    
    print(f"\n" + "="*80)
    print(f"CHUNK ANALYSIS RESULTS")
    print(f"="*80)
    
    print(f"📄 Document: {results['file_path']}")
    print(f"⏱️  Processing Time: {results['processing_time']:.3f}s")
    print(f"📝 Text Length: {results['total_text_length']:,} characters")
    
    print(f"\n📊 Chunking Strategy Comparison:")
    print(f"{'Strategy':<15} {'Chunks':<8} {'Avg Size':<10} {'Variance':<10} {'Completeness':<12}")
    print(f"-" * 60)
    
    for strategy_name, strategy_data in results['chunking_results'].items():
        quality = strategy_data['quality']
        print(f"{strategy_name:<15} {quality['total_chunks']:<8} {quality['avg_chunk_size']:<10.1f} {quality['chunk_size_variance']:<10.1f} {quality['completeness']:<12.2%}")
    
    # Show sample chunks
    print(f"\n📋 Sample Chunks (Smart 500 strategy):")
    smart_chunks = results['chunking_results']['smart_500']['chunks']
    
    for i, chunk in enumerate(smart_chunks[:3]):  # Show first 3 chunks
        print(f"\n--- Chunk {i+1} ({len(chunk.split())} words) ---")
        print(chunk[:500] + "..." if len(chunk) > 500 else chunk)
    
    if len(smart_chunks) > 3:
        print(f"\n... and {len(smart_chunks) - 3} more chunks")
    
    # Show table chunks if available
    if results['table_chunks']:
        print(f"\n📊 Table Chunks ({len(results['table_chunks'])} tables):")
        for i, table in enumerate(results['table_chunks'][:2]):  # Show first 2 tables
            print(f"\n--- Table {i+1} ---")
            print(table[:300] + "..." if len(table) > 300 else table)
    
    # Show image chunks if available
    if results['image_chunks']:
        print(f"\n🖼️  Image Descriptions ({len(results['image_chunks'])} images):")
        for i, image in enumerate(results['image_chunks'][:2]):  # Show first 2 images
            print(f"\n--- Image {i+1} ---")
            print(image[:200] + "..." if len(image) > 200 else image)

def main():
    """Main function to demonstrate chunk extraction"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_chunks_unstructured.py <pdf_file_path>")
        print("Example: python extract_chunks_unstructured.py benchmarks/short_text/sample.pdf")
        return
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Extract chunks
    results = extract_document_chunks(file_path, strategy="hi_res")
    
    # Print analysis
    print_chunk_analysis(results)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
MarkItDown vs Unstructured Markdown Conversion Comparison
Tests both MarkItDown and Unstructured markdown conversion on one PDF from each category
"""

import os
import time
import json
import re
from pathlib import Path
from datetime import datetime

# MarkItDown import
from markitdown import MarkItDown

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Table, Text, Image, Title, NarrativeText, 
    ListItem, Address, PageBreak
)

def convert_elements_to_markdown_unstructured(elements):
    """
    Custom function to convert Unstructured elements to markdown format
    """
    markdown_parts = []
    
    for element in elements:
        if hasattr(element, 'text') and element.text:
            if isinstance(element, Title):
                # Convert titles to markdown headers
                markdown_parts.append(f"# {element.text}\n")
            elif isinstance(element, Table):
                # Convert tables to markdown tables
                table_text = element.text
                # Try to format as markdown table if it has tabular structure
                lines = table_text.strip().split('\n')
                if len(lines) > 1 and '|' in lines[0]:
                    # Already in table format
                    markdown_parts.append(f"\n{table_text}\n")
                else:
                    # Convert to simple table format
                    markdown_parts.append(f"\n```\n{table_text}\n```\n")
            elif isinstance(element, ListItem):
                # Convert list items to markdown lists
                markdown_parts.append(f"* {element.text}\n")
            elif isinstance(element, Image):
                # Convert images to markdown image references
                image_desc = getattr(element, 'text', 'Image')
                markdown_parts.append(f"![{image_desc}](image)\n")
            elif isinstance(element, PageBreak):
                # Add page break marker
                markdown_parts.append("\n---\n")
            else:
                # Regular text content
                markdown_parts.append(f"{element.text}\n\n")
    
    return "".join(markdown_parts)

def identify_markdown_blocks(markdown_text):
    """
    Identify and classify markdown blocks while preserving context
    """
    lines = markdown_text.split('\n')
    blocks = []
    current_block = []
    current_block_type = 'text'
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if current_block:
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            continue
        
        # Identify block type
        if line.startswith('#'):
            # Header block
            if current_block and current_block_type != 'header':
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'header'
            current_block.append(line)
        elif line.startswith('*') or line.startswith('-') or re.match(r'^\d+\.', line):
            # List block
            if current_block and current_block_type != 'list':
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'list'
            current_block.append(line)
        elif line.startswith('```') or line.startswith('|'):
            # Code/table block
            if current_block and current_block_type not in ['code', 'table']:
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'code' if line.startswith('```') else 'table'
            current_block.append(line)
        elif line.startswith('!['):
            # Image block
            if current_block:
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'image'
            current_block.append(line)
        elif line == '---':
            # Horizontal rule
            if current_block:
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'hr'
            current_block.append(line)
        else:
            # Text block
            if current_block and current_block_type != 'text':
                blocks.append((current_block_type, '\n'.join(current_block)))
                current_block = []
            current_block_type = 'text'
            current_block.append(line)
    
    # Add the last block
    if current_block:
        blocks.append((current_block_type, '\n'.join(current_block)))
    
    return blocks

def split_text_with_sentence_awareness(text, max_words_per_chunk=500):
    """
    Split text with sentence-ending awareness per paragraph
    """
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        # Count words in this paragraph
        paragraph_words = len(paragraph.split())
        
        # If adding this paragraph would exceed the limit
        if current_word_count + paragraph_words > max_words_per_chunk and current_chunk:
            # Try to split the paragraph at sentence boundaries
            sentences = re.split(r'[.!?]+', paragraph)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Add complete sentences to current chunk
            for sentence in sentences:
                sentence_words = len(sentence.split())
                if current_word_count + sentence_words <= max_words_per_chunk:
                    current_chunk.append(sentence)
                    current_word_count += sentence_words
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_word_count = sentence_words
            
            # If we still have content, start a new chunk
            if current_word_count > max_words_per_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_word_count = 0
        else:
            # Add the whole paragraph
            current_chunk.append(paragraph)
            current_word_count += paragraph_words
    
    # Add the last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def block_aware_markdown_chunking(markdown_text, max_words_per_chunk=500):
    """
    Block-aware markdown chunking that preserves markdown structure and context
    """
    # Identify markdown blocks
    blocks = identify_markdown_blocks(markdown_text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for block_type, block_content in blocks:
        block_words = len(block_content.split())
        
        # Special handling for different block types
        if block_type == 'header':
            # Headers should start new chunks if they would exceed the limit
            if current_word_count + block_words > max_words_per_chunk and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [block_content]
                current_word_count = block_words
            else:
                current_chunk.append(block_content)
                current_word_count += block_words
                
        elif block_type in ['list', 'code', 'table']:
            # Lists, code blocks, and tables should stay together
            if current_word_count + block_words > max_words_per_chunk and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [block_content]
                current_word_count = block_words
            else:
                current_chunk.append(block_content)
                current_word_count += block_words
                
        elif block_type == 'image':
            # Images can be added to current chunk
            current_chunk.append(block_content)
            current_word_count += block_words
            
        elif block_type == 'hr':
            # Horizontal rules can be used as chunk boundaries
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_word_count = 0
                
        elif block_type == 'text':
            # For text blocks, apply sentence-aware splitting
            if current_word_count + block_words > max_words_per_chunk and current_chunk:
                # Split the text block with sentence awareness
                text_chunks = split_text_with_sentence_awareness(block_content, max_words_per_chunk - current_word_count)
                
                # Add first part to current chunk
                if text_chunks:
                    current_chunk.append(text_chunks[0])
                    chunks.append('\n\n'.join(current_chunk))
                    
                    # Create new chunks for remaining parts
                    for text_chunk in text_chunks[1:]:
                        chunks.append(text_chunk)
                    
                    current_chunk = []
                    current_word_count = 0
            else:
                current_chunk.append(block_content)
                current_word_count += block_words
    
    # Add the last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def analyze_chunk_quality(chunks):
    """Analyze the quality of markdown chunks"""
    if not chunks:
        return {}
    
    # Calculate average chunk size
    chunk_sizes = [len(chunk.split()) for chunk in chunks]
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
    
    # Calculate chunk size variance (consistency)
    variance = sum((size - avg_chunk_size) ** 2 for size in chunk_sizes) / len(chunk_sizes)
    
    # Count markdown elements in chunks
    header_count = sum(1 for chunk in chunks if re.search(r'^#{1,6}\s+', chunk, re.MULTILINE))
    list_count = sum(1 for chunk in chunks if re.search(r'^[\*\-\d\.]\s+', chunk, re.MULTILINE))
    table_count = sum(1 for chunk in chunks if '```' in chunk or '|' in chunk)
    image_count = sum(1 for chunk in chunks if re.search(r'!\[.*\]\(.*\)', chunk))
    
    # Calculate completeness (percentage of chunks that end with sentence endings)
    sentence_endings = ['.', '!', '?']
    complete_chunks = sum(1 for chunk in chunks if any(chunk.strip().endswith(end) for end in sentence_endings))
    completeness = complete_chunks / len(chunks) if chunks else 0
    
    # Calculate sentence completeness per paragraph
    total_paragraphs = 0
    complete_paragraphs = 0
    
    for chunk in chunks:
        paragraphs = chunk.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                total_paragraphs += 1
                if any(paragraph.strip().endswith(end) for end in sentence_endings):
                    complete_paragraphs += 1
    
    paragraph_completeness = complete_paragraphs / total_paragraphs if total_paragraphs > 0 else 0
    
    return {
        'avg_chunk_size': avg_chunk_size,
        'chunk_size_variance': variance,
        'total_chunks': len(chunks),
        'header_chunks': header_count,
        'list_chunks': list_count,
        'table_chunks': table_count,
        'image_chunks': image_count,
        'completeness': completeness,
        'paragraph_completeness': paragraph_completeness,
        'total_paragraphs': total_paragraphs,
        'complete_paragraphs': complete_paragraphs
    }

def test_markitdown_vs_unstructured():
    """Test MarkItDown vs Unstructured markdown conversion on one PDF from each category"""
    
    print("🚀 Testing MarkItDown vs Unstructured Markdown Conversion")
    print("=" * 80)
    
    # Initialize MarkItDown
    md = MarkItDown(enable_plugins=False)
    
    results = []
    categories = ['short_text', 'long_text', 'table_heavy', 'image_heavy']
    
    for category in categories:
        category_dir = Path(f"benchmarks/{category}")
        if not category_dir.exists():
            print(f"❌ Category directory not found: {category_dir}")
            continue
        
        # Get first PDF in category
        pdf_files = list(category_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDFs found in {category}")
            continue
        
        pdf_file = pdf_files[0]
        print(f"\n📁 Testing {category}: {pdf_file.name}")
        
        result = {
            'category': category,
            'file_name': pdf_file.name,
            'file_size_mb': pdf_file.stat().st_size / (1024 * 1024),
            'unstructured': {},
            'markitdown': {},
            'comparison': {}
        }
        
        # Test Unstructured
        try:
            print(f"  🔍 Testing Unstructured...")
            unstructured_start = time.time()
            
            # Extract elements
            elements = partition(str(pdf_file), strategy="hi_res")
            extraction_time = time.time() - unstructured_start
            
            # Convert to markdown
            markdown_start = time.time()
            unstructured_markdown = convert_elements_to_markdown_unstructured(elements)
            markdown_time = time.time() - markdown_start
            
            # Apply chunking
            chunking_start = time.time()
            unstructured_chunks = block_aware_markdown_chunking(unstructured_markdown, max_words_per_chunk=500)
            chunking_time = time.time() - chunking_start
            
            total_unstructured_time = time.time() - unstructured_start
            
            # Analyze Unstructured results
            element_count = len(elements)
            table_count = sum(1 for el in elements if isinstance(el, Table))
            image_count = sum(1 for el in elements if isinstance(el, Image))
            title_count = sum(1 for el in elements if isinstance(el, Title))
            list_count = sum(1 for el in elements if isinstance(el, ListItem))
            text_count = sum(1 for el in elements if isinstance(el, (Text, NarrativeText)))
            
            unstructured_quality = analyze_chunk_quality(unstructured_chunks)
            
            result['unstructured'] = {
                'success': True,
                'extraction_time_seconds': extraction_time,
                'markdown_conversion_time_seconds': markdown_time,
                'chunking_time_seconds': chunking_time,
                'total_time_seconds': total_unstructured_time,
                'element_count': element_count,
                'text_elements': text_count,
                'table_elements': table_count,
                'image_elements': image_count,
                'title_elements': title_count,
                'list_elements': list_count,
                'markdown_length': len(unstructured_markdown),
                'chunk_count': len(unstructured_chunks),
                'chunk_quality': unstructured_quality,
                'sample_chunks': unstructured_chunks[:3] if len(unstructured_chunks) >= 3 else unstructured_chunks
            }
            
            print(f"    ✅ Unstructured: {len(unstructured_chunks)} chunks, {total_unstructured_time:.3f}s")
            
        except Exception as e:
            print(f"    ❌ Unstructured Error: {e}")
            result['unstructured'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test MarkItDown
        try:
            print(f"  🔍 Testing MarkItDown...")
            markitdown_start = time.time()
            
            # Convert PDF to markdown using MarkItDown
            markitdown_result = md.convert(str(pdf_file))
            markitdown_markdown = markitdown_result.text_content
            markitdown_time = time.time() - markitdown_start
            
            # Apply same chunking to MarkItDown output
            chunking_start = time.time()
            markitdown_chunks = block_aware_markdown_chunking(markitdown_markdown, max_words_per_chunk=500)
            chunking_time = time.time() - chunking_start
            
            total_markitdown_time = time.time() - markitdown_start
            
            # Analyze MarkItDown results
            markitdown_quality = analyze_chunk_quality(markitdown_chunks)
            
            result['markitdown'] = {
                'success': True,
                'conversion_time_seconds': markitdown_time,
                'chunking_time_seconds': chunking_time,
                'total_time_seconds': total_markitdown_time,
                'markdown_length': len(markitdown_markdown),
                'chunk_count': len(markitdown_chunks),
                'chunk_quality': markitdown_quality,
                'sample_chunks': markitdown_chunks[:3] if len(markitdown_chunks) >= 3 else markitdown_chunks
            }
            
            print(f"    ✅ MarkItDown: {len(markitdown_chunks)} chunks, {total_markitdown_time:.3f}s")
            
        except Exception as e:
            print(f"    ❌ MarkItDown Error: {e}")
            result['markitdown'] = {
                'success': False,
                'error': str(e)
            }
        
        # Compare results
        if result['unstructured'].get('success', False) and result['markitdown'].get('success', False):
            unstructured_quality = result['unstructured']['chunk_quality']
            markitdown_quality = result['markitdown']['chunk_quality']
            
            result['comparison'] = {
                'speed_advantage': 'markitdown' if result['markitdown']['total_time_seconds'] < result['unstructured']['total_time_seconds'] else 'unstructured',
                'speed_difference_seconds': abs(result['markitdown']['total_time_seconds'] - result['unstructured']['total_time_seconds']),
                'speed_ratio': result['markitdown']['total_time_seconds'] / result['unstructured']['total_time_seconds'] if result['unstructured']['total_time_seconds'] > 0 else float('inf'),
                'chunk_count_difference': abs(len(markitdown_chunks) - len(unstructured_chunks)),
                'chunk_count_ratio': len(markitdown_chunks) / len(unstructured_chunks) if len(unstructured_chunks) > 0 else float('inf'),
                'avg_chunk_size_difference': abs(markitdown_quality['avg_chunk_size'] - unstructured_quality['avg_chunk_size']),
                'avg_chunk_size_ratio': markitdown_quality['avg_chunk_size'] / unstructured_quality['avg_chunk_size'] if unstructured_quality['avg_chunk_size'] > 0 else float('inf'),
                'paragraph_completeness_difference': abs(markitdown_quality['paragraph_completeness'] - unstructured_quality['paragraph_completeness']),
                'header_chunks_difference': abs(markitdown_quality['header_chunks'] - unstructured_quality['header_chunks']),
                'table_chunks_difference': abs(markitdown_quality['table_chunks'] - unstructured_quality['table_chunks']),
                'image_chunks_difference': abs(markitdown_quality['image_chunks'] - unstructured_quality['image_chunks']),
                'markdown_length_difference': abs(result['markitdown']['markdown_length'] - result['unstructured']['markdown_length']),
                'markdown_length_ratio': result['markitdown']['markdown_length'] / result['unstructured']['markdown_length'] if result['unstructured']['markdown_length'] > 0 else float('inf')
            }
            
            print(f"    📊 Comparison: MarkItDown is {result['comparison']['speed_ratio']:.2f}x {'faster' if result['comparison']['speed_advantage'] == 'markitdown' else 'slower'}")
            print(f"       Chunks: {result['comparison']['chunk_count_difference']} difference, {result['comparison']['chunk_count_ratio']:.2f}x ratio")
            print(f"       Avg chunk size: {result['comparison']['avg_chunk_size_difference']:.1f} words difference")
            print(f"       Paragraph completeness: {result['comparison']['paragraph_completeness_difference']:.2%} difference")
        
        results.append(result)
    
    # Save results
    os.makedirs("data", exist_ok=True)
    with open("data/markitdown_vs_unstructured_comparison.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "=" * 80)
    print("📊 COMPARISON SUMMARY")
    print("=" * 80)
    
    successful_comparisons = [r for r in results if r['unstructured'].get('success', False) and r['markitdown'].get('success', False)]
    
    if successful_comparisons:
        # Speed analysis
        markitdown_faster = sum(1 for r in successful_comparisons if r['comparison']['speed_advantage'] == 'markitdown')
        unstructured_faster = len(successful_comparisons) - markitdown_faster
        
        avg_speed_ratio = sum(r['comparison']['speed_ratio'] for r in successful_comparisons) / len(successful_comparisons)
        avg_chunk_ratio = sum(r['comparison']['chunk_count_ratio'] for r in successful_comparisons) / len(successful_comparisons)
        avg_completeness_diff = sum(r['comparison']['paragraph_completeness_difference'] for r in successful_comparisons) / len(successful_comparisons)
        
        print(f"🏁 Speed Performance:")
        print(f"   MarkItDown faster: {markitdown_faster}/{len(successful_comparisons)} cases")
        print(f"   Unstructured faster: {unstructured_faster}/{len(successful_comparisons)} cases")
        print(f"   Average speed ratio (MarkItDown/Unstructured): {avg_speed_ratio:.2f}x")
        
        print(f"\n📝 Content Analysis:")
        print(f"   Average chunk count ratio: {avg_chunk_ratio:.2f}x")
        print(f"   Average paragraph completeness difference: {avg_completeness_diff:.2%}")
        
        # Detailed comparison by category
        print(f"\n📋 Detailed Results by Category:")
        for result in successful_comparisons:
            comp = result['comparison']
            print(f"\n   {result['category']} ({result['file_name']}):")
            print(f"     Speed: MarkItDown is {comp['speed_ratio']:.2f}x {'faster' if comp['speed_advantage'] == 'markitdown' else 'slower'}")
            print(f"     Chunks: {comp['chunk_count_difference']} difference ({comp['chunk_count_ratio']:.2f}x ratio)")
            print(f"     Avg chunk size: {comp['avg_chunk_size_difference']:.1f} words difference")
            print(f"     Paragraph completeness: {comp['paragraph_completeness_difference']:.2%} difference")
            print(f"     Headers: {comp['header_chunks_difference']} difference")
            print(f"     Tables: {comp['table_chunks_difference']} difference")
            print(f"     Images: {comp['image_chunks_difference']} difference")
            print(f"     Markdown length: {comp['markdown_length_ratio']:.2f}x ratio")
    
    print(f"\n📁 Results saved to: data/markitdown_vs_unstructured_comparison.json")
    
    # Show sample chunks comparison
    print(f"\n📝 Sample Chunks Comparison:")
    for result in successful_comparisons:
        print(f"\n--- {result['category']} ({result['file_name']}) ---")
        
        print(f"\nUnstructured (first chunk):")
        if result['unstructured']['sample_chunks']:
            sample = result['unstructured']['sample_chunks'][0]
            print(sample[:300] + "..." if len(sample) > 300 else sample)
        
        print(f"\nMarkItDown (first chunk):")
        if result['markitdown']['sample_chunks']:
            sample = result['markitdown']['sample_chunks'][0]
            print(sample[:300] + "..." if len(sample) > 300 else sample)
        print("-" * 50)

if __name__ == "__main__":
    test_markitdown_vs_unstructured() 
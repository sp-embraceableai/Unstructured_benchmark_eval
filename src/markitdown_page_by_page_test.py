#!/usr/bin/env python3
"""
MarkItDown Page-by-Page vs Whole Document Processing
Tests MarkItDown with page-by-page processing to retain page numbers
"""

import os
import time
import json
import re
from pathlib import Path
from datetime import datetime

# MarkItDown import
from markitdown import MarkItDown

# PyMuPDF for page-by-page processing
import fitz  # PyMuPDF

def process_pdf_page_by_page_markitdown(pdf_path, md):
    """
    Process PDF page by page using MarkItDown to retain page numbers
    """
    markdown_parts = []
    page_count = 0
    
    # Open PDF with PyMuPDF to get page count
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    
    print(f"    📄 Processing {total_pages} pages individually...")
    
    for page_num in range(total_pages):
        try:
            # Create a new PDF document with just this page
            new_doc = fitz.open()
            new_doc.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            
            # Save the single page as a temporary PDF
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            new_doc.save(temp_path)
            new_doc.close()
            
            # Process single page with MarkItDown
            page_start = time.time()
            result = md.convert(temp_path)
            page_time = time.time() - page_start
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Add page number header
            page_content = f"# Page {page_num + 1} of {total_pages}\n\n"
            page_content += result.text_content
            
            markdown_parts.append(page_content)
            page_count += 1
            
            if page_num % 10 == 0:  # Progress indicator every 10 pages
                print(f"      Processed page {page_num + 1}/{total_pages} ({page_time:.3f}s)")
                
        except Exception as e:
            print(f"      ❌ Error processing page {page_num + 1}: {e}")
            # Add error marker for this page
            markdown_parts.append(f"# Page {page_num + 1} of {total_pages}\n\n[Error processing this page: {e}]\n")
    
    pdf_document.close()
    
    return "\n\n---\n\n".join(markdown_parts), page_count

def process_pdf_whole_document_markitdown(pdf_path, md):
    """
    Process entire PDF document with MarkItDown (original approach)
    """
    print(f"    📄 Processing entire document...")
    start_time = time.time()
    result = md.convert(pdf_path)
    processing_time = time.time() - start_time
    
    return result.text_content, processing_time

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
    
    # Count page number headers
    page_header_count = sum(1 for chunk in chunks if re.search(r'^# Page \d+ of \d+', chunk, re.MULTILINE))
    
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
        'page_header_chunks': page_header_count,
        'completeness': completeness,
        'paragraph_completeness': paragraph_completeness,
        'total_paragraphs': total_paragraphs,
        'complete_paragraphs': complete_paragraphs
    }

def test_page_by_page_vs_whole_document():
    """Test MarkItDown page-by-page vs whole document processing"""
    
    print("🚀 Testing MarkItDown: Page-by-Page vs Whole Document Processing")
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
            'whole_document': {},
            'page_by_page': {},
            'comparison': {}
        }
        
        # Test whole document processing
        try:
            print(f"  🔍 Testing whole document processing...")
            whole_start = time.time()
            
            # Process entire document
            whole_markdown, whole_time = process_pdf_whole_document_markitdown(str(pdf_file), md)
            
            # Apply chunking
            chunking_start = time.time()
            whole_chunks = block_aware_markdown_chunking(whole_markdown, max_words_per_chunk=500)
            chunking_time = time.time() - chunking_start
            
            total_whole_time = time.time() - whole_start
            
            # Analyze whole document results
            whole_quality = analyze_chunk_quality(whole_chunks)
            
            result['whole_document'] = {
                'success': True,
                'conversion_time_seconds': whole_time,
                'chunking_time_seconds': chunking_time,
                'total_time_seconds': total_whole_time,
                'markdown_length': len(whole_markdown),
                'chunk_count': len(whole_chunks),
                'chunk_quality': whole_quality,
                'sample_chunks': whole_chunks[:3] if len(whole_chunks) >= 3 else whole_chunks
            }
            
            print(f"    ✅ Whole document: {len(whole_chunks)} chunks, {total_whole_time:.3f}s")
            
        except Exception as e:
            print(f"    ❌ Whole document Error: {e}")
            result['whole_document'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test page-by-page processing
        try:
            print(f"  🔍 Testing page-by-page processing...")
            page_start = time.time()
            
            # Process page by page
            page_markdown, page_count = process_pdf_page_by_page_markitdown(str(pdf_file), md)
            
            # Apply chunking
            chunking_start = time.time()
            page_chunks = block_aware_markdown_chunking(page_markdown, max_words_per_chunk=500)
            chunking_time = time.time() - chunking_start
            
            total_page_time = time.time() - page_start
            
            # Analyze page-by-page results
            page_quality = analyze_chunk_quality(page_chunks)
            
            result['page_by_page'] = {
                'success': True,
                'conversion_time_seconds': total_page_time - chunking_time,
                'chunking_time_seconds': chunking_time,
                'total_time_seconds': total_page_time,
                'page_count': page_count,
                'markdown_length': len(page_markdown),
                'chunk_count': len(page_chunks),
                'chunk_quality': page_quality,
                'sample_chunks': page_chunks[:3] if len(page_chunks) >= 3 else page_chunks
            }
            
            print(f"    ✅ Page-by-page: {len(page_chunks)} chunks, {total_page_time:.3f}s, {page_count} pages")
            
        except Exception as e:
            print(f"    ❌ Page-by-page Error: {e}")
            result['page_by_page'] = {
                'success': False,
                'error': str(e)
            }
        
        # Compare results
        if result['whole_document'].get('success', False) and result['page_by_page'].get('success', False):
            whole_quality = result['whole_document']['chunk_quality']
            page_quality = result['page_by_page']['chunk_quality']
            
            result['comparison'] = {
                'speed_advantage': 'whole_document' if result['whole_document']['total_time_seconds'] < result['page_by_page']['total_time_seconds'] else 'page_by_page',
                'speed_difference_seconds': abs(result['page_by_page']['total_time_seconds'] - result['whole_document']['total_time_seconds']),
                'speed_ratio': result['page_by_page']['total_time_seconds'] / result['whole_document']['total_time_seconds'] if result['whole_document']['total_time_seconds'] > 0 else float('inf'),
                'chunk_count_difference': abs(len(page_chunks) - len(whole_chunks)),
                'chunk_count_ratio': len(page_chunks) / len(whole_chunks) if len(whole_chunks) > 0 else float('inf'),
                'avg_chunk_size_difference': abs(page_quality['avg_chunk_size'] - whole_quality['avg_chunk_size']),
                'avg_chunk_size_ratio': page_quality['avg_chunk_size'] / whole_quality['avg_chunk_size'] if whole_quality['avg_chunk_size'] > 0 else float('inf'),
                'paragraph_completeness_difference': abs(page_quality['paragraph_completeness'] - whole_quality['paragraph_completeness']),
                'page_header_presence': page_quality['page_header_chunks'] > 0,
                'page_header_count': page_quality['page_header_chunks'],
                'markdown_length_difference': abs(result['page_by_page']['markdown_length'] - result['whole_document']['markdown_length']),
                'markdown_length_ratio': result['page_by_page']['markdown_length'] / result['whole_document']['markdown_length'] if result['whole_document']['markdown_length'] > 0 else float('inf')
            }
            
            print(f"    📊 Comparison: Page-by-page is {result['comparison']['speed_ratio']:.2f}x {'faster' if result['comparison']['speed_advantage'] == 'page_by_page' else 'slower'}")
            print(f"       Page headers: {result['comparison']['page_header_count']} found in page-by-page")
            print(f"       Chunks: {result['comparison']['chunk_count_difference']} difference")
            print(f"       Avg chunk size: {result['comparison']['avg_chunk_size_difference']:.1f} words difference")
        
        results.append(result)
    
    # Save results
    os.makedirs("data", exist_ok=True)
    with open("data/markitdown_page_by_page_comparison.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "=" * 80)
    print("📊 PAGE-BY-PAGE vs WHOLE DOCUMENT SUMMARY")
    print("=" * 80)
    
    successful_comparisons = [r for r in results if r['whole_document'].get('success', False) and r['page_by_page'].get('success', False)]
    
    if successful_comparisons:
        # Speed analysis
        page_faster = sum(1 for r in successful_comparisons if r['comparison']['speed_advantage'] == 'page_by_page')
        whole_faster = len(successful_comparisons) - page_faster
        
        avg_speed_ratio = sum(r['comparison']['speed_ratio'] for r in successful_comparisons) / len(successful_comparisons)
        avg_page_headers = sum(r['comparison']['page_header_count'] for r in successful_comparisons) / len(successful_comparisons)
        
        print(f"🏁 Speed Performance:")
        print(f"   Page-by-page faster: {page_faster}/{len(successful_comparisons)} cases")
        print(f"   Whole document faster: {whole_faster}/{len(successful_comparisons)} cases")
        print(f"   Average speed ratio (Page-by-page/Whole): {avg_speed_ratio:.2f}x")
        
        print(f"\n📄 Page Number Preservation:")
        print(f"   Average page headers found: {avg_page_headers:.1f}")
        print(f"   Page headers preserved: {sum(1 for r in successful_comparisons if r['comparison']['page_header_presence'])}/{len(successful_comparisons)} cases")
        
        # Detailed comparison by category
        print(f"\n📋 Detailed Results by Category:")
        for result in successful_comparisons:
            comp = result['comparison']
            print(f"\n   {result['category']} ({result['file_name']}):")
            print(f"     Speed: Page-by-page is {comp['speed_ratio']:.2f}x {'faster' if comp['speed_advantage'] == 'page_by_page' else 'slower'}")
            print(f"     Page headers: {comp['page_header_count']} found")
            print(f"     Chunks: {comp['chunk_count_difference']} difference ({comp['chunk_count_ratio']:.2f}x ratio)")
            print(f"     Avg chunk size: {comp['avg_chunk_size_difference']:.1f} words difference")
            print(f"     Markdown length: {comp['markdown_length_ratio']:.2f}x ratio")
    
    print(f"\n📁 Results saved to: data/markitdown_page_by_page_comparison.json")
    
    # Show sample chunks comparison
    print(f"\n📝 Sample Chunks Comparison:")
    for result in successful_comparisons:
        print(f"\n--- {result['category']} ({result['file_name']}) ---")
        
        print(f"\nWhole Document (first chunk):")
        if result['whole_document']['sample_chunks']:
            sample = result['whole_document']['sample_chunks'][0]
            print(sample[:300] + "..." if len(sample) > 300 else sample)
        
        print(f"\nPage-by-Page (first chunk):")
        if result['page_by_page']['sample_chunks']:
            sample = result['page_by_page']['sample_chunks'][0]
            print(sample[:300] + "..." if len(sample) > 300 else sample)
        print("-" * 50)

if __name__ == "__main__":
    test_page_by_page_vs_whole_document() 
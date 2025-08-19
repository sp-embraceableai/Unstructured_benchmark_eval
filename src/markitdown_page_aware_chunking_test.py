#!/usr/bin/env python3
"""
MarkItDown with Page-Aware Chunking
Tests MarkItDown with page-by-page processing and page-aware chunking to preserve ALL page numbers
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

def page_aware_chunking(markdown_text, max_words_per_chunk=500):
    """
    Page-aware chunking that preserves page boundaries and never splits across pages
    """
    # Split by the triple dash separators that separate pages
    page_sections = markdown_text.split('\n\n---\n\n')
    
    chunks = []
    
    for section in page_sections:
        if not section.strip():
            continue
        
        # Each section should start with a page header
        # Check if this page content exceeds the word limit
        word_count = len(section.split())
        
        if word_count <= max_words_per_chunk:
            # Page fits in one chunk - keep it as is
            chunks.append(section.strip())
        else:
            # Page is too large, split it with sentence awareness but preserve page header
            page_chunks = split_page_with_sentence_awareness(section.strip(), max_words_per_chunk)
            chunks.extend(page_chunks)
    
    return chunks

def split_page_with_sentence_awareness(page_content, max_words_per_chunk=500):
    """
    Split a single page content with sentence awareness while preserving the page header
    """
    # Extract page header
    header_match = re.match(r'^(# Page \d+ of \d+\n)', page_content)
    if header_match:
        page_header = header_match.group(1)
        content = page_content[len(page_header):]
    else:
        page_header = ""
        content = page_content
    
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = page_header  # Start with page header
    current_word_count = len(page_header.split())
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        paragraph_words = len(paragraph.split())
        
        # If adding this paragraph would exceed the limit
        if current_word_count + paragraph_words > max_words_per_chunk and current_chunk.strip() != page_header.strip():
            # Save current chunk and start new one
            chunks.append(current_chunk.strip())
            current_chunk = page_header  # New chunk starts with page header
            current_word_count = len(page_header.split())
        
        # Add paragraph to current chunk
        if current_chunk.strip() != page_header.strip():
            current_chunk += "\n\n" + paragraph
        else:
            current_chunk += paragraph
        current_word_count += paragraph_words
    
    # Add the last chunk
    if current_chunk.strip() != page_header.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

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

def test_page_aware_chunking():
    """Test MarkItDown with page-aware chunking"""
    
    print("🚀 Testing MarkItDown with Page-Aware Chunking")
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
            'page_aware_chunking': {},
            'block_aware_chunking': {},
            'comparison': {}
        }
        
        # Test page-by-page processing with page-aware chunking
        try:
            print(f"  🔍 Testing page-by-page processing...")
            page_start = time.time()
            
            # Process page by page
            page_markdown, page_count = process_pdf_page_by_page_markitdown(str(pdf_file), md)
            
            # Apply page-aware chunking
            chunking_start = time.time()
            page_aware_chunks = page_aware_chunking(page_markdown, max_words_per_chunk=500)
            page_aware_chunking_time = time.time() - chunking_start
            
            # Apply block-aware chunking for comparison
            block_chunking_start = time.time()
            block_aware_chunks = block_aware_markdown_chunking(page_markdown, max_words_per_chunk=500)
            block_aware_chunking_time = time.time() - block_chunking_start
            
            total_page_time = time.time() - page_start
            
            # Analyze results
            page_aware_quality = analyze_chunk_quality(page_aware_chunks)
            block_aware_quality = analyze_chunk_quality(block_aware_chunks)
            
            result['page_aware_chunking'] = {
                'success': True,
                'conversion_time_seconds': total_page_time - page_aware_chunking_time - block_aware_chunking_time,
                'chunking_time_seconds': page_aware_chunking_time,
                'total_time_seconds': total_page_time,
                'page_count': page_count,
                'markdown_length': len(page_markdown),
                'chunk_count': len(page_aware_chunks),
                'chunk_quality': page_aware_quality,
                'sample_chunks': page_aware_chunks[:3] if len(page_aware_chunks) >= 3 else page_aware_chunks
            }
            
            result['block_aware_chunking'] = {
                'success': True,
                'chunking_time_seconds': block_aware_chunking_time,
                'chunk_count': len(block_aware_chunks),
                'chunk_quality': block_aware_quality,
                'sample_chunks': block_aware_chunks[:3] if len(block_aware_chunks) >= 3 else block_aware_chunks
            }
            
            print(f"    ✅ Page-aware: {len(page_aware_chunks)} chunks, {page_aware_chunking_time:.3f}s")
            print(f"    ✅ Block-aware: {len(block_aware_chunks)} chunks, {block_aware_chunking_time:.3f}s")
            print(f"    📄 Page headers: {page_aware_quality['page_header_chunks']} found (expected: {page_count})")
            
            # Compare results
            result['comparison'] = {
                'page_header_preservation': page_aware_quality['page_header_chunks'] == page_count,
                'page_header_difference': page_aware_quality['page_header_chunks'] - page_count,
                'chunk_count_difference': len(page_aware_chunks) - len(block_aware_chunks),
                'chunk_count_ratio': len(page_aware_chunks) / len(block_aware_chunks) if len(block_aware_chunks) > 0 else float('inf'),
                'avg_chunk_size_difference': abs(page_aware_quality['avg_chunk_size'] - block_aware_quality['avg_chunk_size']),
                'avg_chunk_size_ratio': page_aware_quality['avg_chunk_size'] / block_aware_quality['avg_chunk_size'] if block_aware_quality['avg_chunk_size'] > 0 else float('inf'),
                'paragraph_completeness_difference': abs(page_aware_quality['paragraph_completeness'] - block_aware_quality['paragraph_completeness'])
            }
            
            if result['comparison']['page_header_preservation']:
                print(f"    ✅ ALL page numbers preserved!")
            else:
                print(f"    ⚠️  Missing {result['comparison']['page_header_difference']} page numbers")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            result['page_aware_chunking'] = {
                'success': False,
                'error': str(e)
            }
        
        results.append(result)
    
    # Save results
    os.makedirs("data", exist_ok=True)
    with open("data/markitdown_page_aware_chunking_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "=" * 80)
    print("📊 PAGE-AWARE CHUNKING SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['page_aware_chunking'].get('success', False)]
    
    if successful_tests:
        # Page number preservation analysis
        all_preserved = sum(1 for r in successful_tests if r['comparison']['page_header_preservation'])
        total_pages = sum(r['page_aware_chunking']['page_count'] for r in successful_tests)
        total_page_headers = sum(r['page_aware_chunking']['chunk_quality']['page_header_chunks'] for r in successful_tests)
        
        print(f"📄 Page Number Preservation:")
        print(f"   All pages preserved: {all_preserved}/{len(successful_tests)} documents")
        print(f"   Total pages processed: {total_pages}")
        print(f"   Total page headers found: {total_page_headers}")
        print(f"   Success rate: {total_page_headers/total_pages*100:.1f}%")
        
        # Chunking comparison
        avg_chunk_ratio = sum(r['comparison']['chunk_count_ratio'] for r in successful_tests) / len(successful_tests)
        avg_size_ratio = sum(r['comparison']['avg_chunk_size_ratio'] for r in successful_tests) / len(successful_tests)
        
        print(f"\n📊 Chunking Comparison:")
        print(f"   Average chunk count ratio: {avg_chunk_ratio:.2f}x")
        print(f"   Average chunk size ratio: {avg_size_ratio:.2f}x")
        
        # Detailed results by category
        print(f"\n📋 Detailed Results by Category:")
        for result in successful_tests:
            comp = result['comparison']
            page_quality = result['page_aware_chunking']['chunk_quality']
            print(f"\n   {result['category']} ({result['file_name']}):")
            print(f"     Pages: {result['page_aware_chunking']['page_count']}")
            print(f"     Page headers found: {page_quality['page_header_chunks']}")
            print(f"     All preserved: {'✅' if comp['page_header_preservation'] else '❌'}")
            print(f"     Chunks: {result['page_aware_chunking']['chunk_count']} vs {result['block_aware_chunking']['chunk_count']}")
            print(f"     Avg chunk size: {page_quality['avg_chunk_size']:.1f} words")
    
    print(f"\n📁 Results saved to: data/markitdown_page_aware_chunking_results.json")
    
    # Show sample chunks
    print(f"\n📝 Sample Chunks (Page-Aware):")
    for result in successful_tests:
        print(f"\n--- {result['category']} ({result['file_name']}) ---")
        if result['page_aware_chunking']['sample_chunks']:
            sample = result['page_aware_chunking']['sample_chunks'][0]
            print(sample[:300] + "..." if len(sample) > 300 else sample)
        print("-" * 50)

if __name__ == "__main__":
    test_page_aware_chunking() 
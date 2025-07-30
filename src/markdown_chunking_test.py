#!/usr/bin/env python3
"""
Unstructured Markdown Conversion + Chunking Test
Tests markdown conversion and markdown-sensitive chunking on one PDF from each category
"""

import os
import time
import json
import re
from pathlib import Path
from datetime import datetime

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Table, Text, Image, Title, NarrativeText, 
    ListItem, Address, PageBreak
)

def convert_elements_to_markdown(elements):
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

def test_markdown_chunking():
    """Test markdown conversion and chunking on one PDF from each category"""
    
    print("🚀 Testing Block-Aware Markdown Conversion + Chunking with Unstructured")
    print("=" * 80)
    
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
        
        try:
            # Time the processing
            start_time = time.time()
            
            # Extract elements
            print(f"  🔍 Extracting elements...")
            elements = partition(str(pdf_file), strategy="hi_res")
            extraction_time = time.time() - start_time
            
            # Convert to markdown
            print(f"  Converting to markdown...")
            markdown_start = time.time()
            markdown_text = convert_elements_to_markdown(elements)
            markdown_time = time.time() - markdown_start
            
            # Apply block-aware markdown chunking
            print(f"  Applying block-aware markdown chunking...")
            chunking_start = time.time()
            chunks = block_aware_markdown_chunking(markdown_text, max_words_per_chunk=500)
            chunking_time = time.time() - chunking_start
            
            total_time = time.time() - start_time
            
            # Analyze results
            element_count = len(elements)
            markdown_length = len(markdown_text)
            
            # Count different element types
            table_count = sum(1 for el in elements if isinstance(el, Table))
            image_count = sum(1 for el in elements if isinstance(el, Image))
            title_count = sum(1 for el in elements if isinstance(el, Title))
            list_count = sum(1 for el in elements if isinstance(el, ListItem))
            text_count = sum(1 for el in elements if isinstance(el, (Text, NarrativeText)))
            
            # Analyze chunk quality
            chunk_quality = analyze_chunk_quality(chunks)
            
            # Get sample chunks
            sample_chunks = chunks[:3] if len(chunks) >= 3 else chunks
            
            result = {
                'category': category,
                'file_name': pdf_file.name,
                'file_size_mb': pdf_file.stat().st_size / (1024 * 1024),
                'extraction_time_seconds': extraction_time,
                'markdown_conversion_time_seconds': markdown_time,
                'chunking_time_seconds': chunking_time,
                'total_time_seconds': total_time,
                'element_count': element_count,
                'text_elements': text_count,
                'table_elements': table_count,
                'image_elements': image_count,
                'title_elements': title_count,
                'list_elements': list_count,
                'markdown_length': markdown_length,
                'chunk_count': len(chunks),
                'chunk_quality': chunk_quality,
                'sample_chunks': sample_chunks,
                'success': True
            }
            
            print(f"  ✅ Success!")
            print(f"     Elements: {element_count} (Text: {text_count}, Tables: {table_count}, Images: {image_count}, Titles: {title_count}, Lists: {list_count})")
            print(f"     Markdown length: {markdown_length:,} characters")
            print(f"     Chunks: {len(chunks)} (avg size: {chunk_quality['avg_chunk_size']:.1f} words)")
            print(f"     Paragraph completeness: {chunk_quality['paragraph_completeness']:.2%}")
            print(f"     Extraction time: {extraction_time:.3f}s")
            print(f"     Markdown conversion time: {markdown_time:.3f}s")
            print(f"     Chunking time: {chunking_time:.3f}s")
            print(f"     Total time: {total_time:.3f}s")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            result = {
                'category': category,
                'file_name': pdf_file.name,
                'error': str(e),
                'success': False
            }
        
        results.append(result)
    
    # Save results
    os.makedirs("data", exist_ok=True)
    with open("data/block_aware_markdown_chunking_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        total_extraction_time = sum(r['extraction_time_seconds'] for r in successful)
        total_markdown_time = sum(r['markdown_conversion_time_seconds'] for r in successful)
        total_chunking_time = sum(r['chunking_time_seconds'] for r in successful)
        total_time = sum(r['total_time_seconds'] for r in successful)
        
        print(f"\n⏱️  Performance:")
        print(f"   Total extraction time: {total_extraction_time:.3f}s")
        print(f"   Total markdown conversion time: {total_markdown_time:.3f}s")
        print(f"   Total chunking time: {total_chunking_time:.3f}s")
        print(f"   Total processing time: {total_time:.3f}s")
        print(f"   Average extraction time: {total_extraction_time/len(successful):.3f}s")
        print(f"   Average markdown conversion time: {total_markdown_time/len(successful):.3f}s")
        print(f"   Average chunking time: {total_chunking_time/len(successful):.3f}s")
    
    print(f"\n📁 Results saved to: data/block_aware_markdown_chunking_results.json")
    
    # Show chunk samples
    print(f"\n📝 Chunk Samples:")
    for result in successful:
        print(f"\n--- {result['category']} ({result['file_name']}) ---")
        print(f"Total chunks: {result['chunk_count']}")
        print(f"Average chunk size: {result['chunk_quality']['avg_chunk_size']:.1f} words")
        print(f"Header chunks: {result['chunk_quality']['header_chunks']}")
        print(f"List chunks: {result['chunk_quality']['list_chunks']}")
        print(f"Table chunks: {result['chunk_quality']['table_chunks']}")
        print(f"Image chunks: {result['chunk_quality']['image_chunks']}")
        print(f"Paragraph completeness: {result['chunk_quality']['paragraph_completeness']:.2%}")
        
        # Show first chunk sample
        if result['sample_chunks']:
            print(f"\nFirst chunk sample:")
            print(result['sample_chunks'][0][:300] + "..." if len(result['sample_chunks'][0]) > 300 else result['sample_chunks'][0])
        print("-" * 50)

if __name__ == "__main__":
    test_markdown_chunking() 
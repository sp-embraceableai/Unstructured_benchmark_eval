#!/usr/bin/env python3
"""
Unstructured Markdown Conversion Test
Tests markdown conversion on one PDF from each category
"""

import os
import time
import json
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

def test_markdown_conversion():
    """Test markdown conversion on one PDF from each category"""
    
    print("🚀 Testing Markdown Conversion with Unstructured")
    print("=" * 60)
    
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
            output_text = markdown_text
            output_type = "markdown"
            
            total_time = time.time() - start_time
            
            # Analyze results
            element_count = len(elements)
            output_length = len(output_text)
            
            # Count different element types
            table_count = sum(1 for el in elements if isinstance(el, Table))
            image_count = sum(1 for el in elements if isinstance(el, Image))
            title_count = sum(1 for el in elements if isinstance(el, Title))
            list_count = sum(1 for el in elements if isinstance(el, ListItem))
            text_count = sum(1 for el in elements if isinstance(el, (Text, NarrativeText)))
            
            # Get sample of output
            output_sample = output_text[:500] + "..." if len(output_text) > 500 else output_text
            
            result = {
                'category': category,
                'file_name': pdf_file.name,
                'file_size_mb': pdf_file.stat().st_size / (1024 * 1024),
                'extraction_time_seconds': extraction_time,
                'conversion_time_seconds': markdown_time,
                'total_time_seconds': total_time,
                'element_count': element_count,
                'text_elements': text_count,
                'table_elements': table_count,
                'image_elements': image_count,
                'title_elements': title_count,
                'list_elements': list_count,
                'output_length': output_length,
                'output_type': output_type,
                'output_sample': output_sample,
                'success': True
            }
            
            print(f"  ✅ Success!")
            print(f"     Elements: {element_count} (Text: {text_count}, Tables: {table_count}, Images: {image_count}, Titles: {title_count}, Lists: {list_count})")
            print(f"     {output_type.title()} length: {output_length:,} characters")
            print(f"     Extraction time: {extraction_time:.3f}s")
            print(f"     Conversion time: {markdown_time:.3f}s")
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
    with open("data/markdown_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        total_extraction_time = sum(r['extraction_time_seconds'] for r in successful)
        total_conversion_time = sum(r['conversion_time_seconds'] for r in successful)
        total_time = sum(r['total_time_seconds'] for r in successful)
        
        print(f"\n⏱️  Performance:")
        print(f"   Total extraction time: {total_extraction_time:.3f}s")
        print(f"   Total conversion time: {total_conversion_time:.3f}s")
        print(f"   Total processing time: {total_time:.3f}s")
        print(f"   Average extraction time: {total_extraction_time/len(successful):.3f}s")
        print(f"   Average conversion time: {total_conversion_time/len(successful):.3f}s")
    
    print(f"\n📁 Results saved to: data/markdown_test_results.json")
    
    # Show output samples
    print(f"\n📝 Output Samples:")
    for result in successful:
        print(f"\n--- {result['category']} ({result['file_name']}) ---")
        print(f"Type: {result['output_type']}")
        print(result['output_sample'])
        print("-" * 40)

if __name__ == "__main__":
    test_markdown_conversion() 
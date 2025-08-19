#!/usr/bin/env python3
"""
Test script for advanced Docling chunking methods.
Tests the implementation against a single PDF to verify functionality.
"""

import sys
from pathlib import Path
from benchmark_runner import UnstructuredBenchmark

def test_advanced_docling():
    """Test advanced Docling chunking on a single PDF."""
    
    # Initialize benchmark runner
    benchmark = UnstructuredBenchmark()
    
    # Find a test PDF
    test_pdf = None
    for category in ["short_text", "long_text", "table_heavy", "image_heavy"]:
        category_dir = benchmark.benchmarks_dir / category
        if category_dir.exists():
            pdf_files = list(category_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf = pdf_files[0]
                break
    
    if not test_pdf:
        print("❌ No test PDF found in any category directory")
        return
    
    print(f"🧪 Testing advanced Docling chunking on: {test_pdf.name}")
    print(f"📁 Category: {test_pdf.parent.name}")
    print()
    
    try:
        # Test advanced Docling chunking
        print("🔍 Testing advanced Docling chunking...")
        advanced_results = benchmark.advanced_docling_chunking(test_pdf)
        
        if "error" in advanced_results:
            print(f"❌ Advanced Docling failed: {advanced_results['error']}")
            return
        
        print("✅ Advanced Docling chunking successful!")
        print()
        
        # Display results for each strategy
        for strategy_name, results in advanced_results.items():
            print(f"📊 {results['strategy']} Strategy:")
            print(f"   Total chunks: {results['total_chunks']}")
            print(f"   Text chunks: {results['text_chunks']}")
            print(f"   Table chunks: {results['table_chunks']}")
            print(f"   Image chunks: {results['image_chunks']}")
            print(f"   Average chunk size: {results['avg_chunk_size']:.1f} words")
            print()
        
        # Test adaptive hybrid chunking
        print("🔍 Testing adaptive hybrid chunking...")
        adaptive_results = benchmark.adaptive_hybrid_chunking(test_pdf)
        
        if "error" in adaptive_results:
            print(f"❌ Adaptive hybrid chunking failed: {adaptive_results['error']}")
        else:
            print("✅ Adaptive hybrid chunking successful!")
            print()
            print(f"📊 {adaptive_results['strategy']}:")
            print(f"   Total chunks: {adaptive_results['total_chunks']}")
            print(f"   Text chunks: {adaptive_results['text_chunks']}")
            print(f"   Table chunks: {adaptive_results['table_chunks']}")
            print(f"   Image chunks: {adaptive_results['image_chunks']}")
            print(f"   Average chunk size: {adaptive_results['avg_chunk_size']:.1f} words")
            print()
            
            # Display document analysis
            analysis = adaptive_results['document_analysis']
            print("📋 Document Analysis:")
            print(f"   Document length: {analysis['length']} characters")
            print(f"   Has headers: {analysis['has_headers']}")
            print(f"   Has tables: {analysis['has_tables']}")
            print(f"   Has lists: {analysis['has_lists']}")
            print(f"   Primary strategy: {analysis['primary_strategy']}")
            print(f"   Secondary strategy: {analysis['secondary_strategy']}")
            print(f"   Strategy weights: {analysis['weights']}")
            print()
        
        # Test full document processing
        print("🔍 Testing full document processing with advanced Docling...")
        result = benchmark.process_document_with_advanced_docling(test_pdf, test_pdf.parent.name)
        
        print("✅ Full document processing successful!")
        print()
        print("📊 Results Summary:")
        print(f"   Document: {result.document_name}")
        print(f"   Type: {result.document_type}")
        print(f"   File size: {result.file_size_mb:.2f} MB")
        print()
        print("   Unstructured:")
        print(f"     Processing time: {result.u_processing_time_seconds}s")
        print(f"     Total elements: {result.u_total_elements}")
        print(f"     Text elements: {result.u_text_elements}")
        print(f"     Table elements: {result.u_table_elements}")
        print(f"     Chunk count: {result.u_chunk_count}")
        print(f"     Avg chunk size: {result.u_avg_chunk_size:.1f} words")
        print()
        print("   Advanced Docling:")
        print(f"     Processing time: {result.d_processing_time_seconds}s")
        print(f"     Total elements: {result.d_total_elements}")
        print(f"     Text elements: {result.d_text_elements}")
        print(f"     Table elements: {result.d_table_elements}")
        print(f"     Chunk count: {result.d_chunk_count}")
        print(f"     Avg chunk size: {result.d_avg_chunk_size:.1f} words")
        print()
        
        if result.d_error:
            print(f"   Docling error: {result.d_error}")
        
        print("🎉 Advanced Docling test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_docling() 
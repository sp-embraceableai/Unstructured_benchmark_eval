#!/usr/bin/env python3
"""
Unstructured Performance Benchmark Framework
Main Entry Point

This script provides easy access to all main functionalities:
1. Basic benchmarking (Unstructured only)
2. Single document chunk extraction and analysis
3. Category-based analysis
4. All analyses combined
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Unstructured Performance Benchmark Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py benchmark                    # Run basic Unstructured benchmark
  python main.py extract <pdf_file>          # Extract chunks from single PDF
  python main.py category                     # Run category-based analysis
  python main.py all                          # Run all analyses
        """
    )
    
    parser.add_argument(
        'command',
        choices=['benchmark', 'extract', 'category', 'all'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='PDF file path (for extract command)'
    )
    
    args = parser.parse_args()
    
    # Add src directory to path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    if args.verbose:
        print(f"🔍 Running command: {args.command}")
        print(f"📁 Source path: {src_path}")
    
    try:
        if args.command == 'benchmark':
            print("🚀 Running Unstructured benchmark...")
            from unstructured_only_benchmark import UnstructuredOnlyBenchmark
            benchmark = UnstructuredOnlyBenchmark()
            results = benchmark.run_benchmarks()
            
            if results:
                benchmark.save_results()
                benchmark.print_summary()
                benchmark.generate_report()
                print("✅ Benchmark completed!")
                print("📁 Results saved to:")
                print("   - data/unstructured_benchmark_results.json")
                print("   - reports/unstructured_benchmark_report.md")
                print("   - benchmark.log")
            else:
                print("❌ No documents were processed. Check the benchmarks directory.")
            
        elif args.command == 'extract':
            if not args.file:
                print("❌ Please provide a PDF file path with --file or -f")
                print("Example: python main.py extract --file benchmarks/short_text/sample.pdf")
                return
            
            print(f"🔍 Extracting chunks from: {args.file}")
            from extract_chunks_unstructured import extract_document_chunks, print_chunk_analysis
            results = extract_document_chunks(args.file, strategy="hi_res")
            print_chunk_analysis(results)
            print("✅ Chunk extraction completed!")
            
        elif args.command == 'category':
            print("📊 Running category-based analysis...")
            from run_category_chunk_comparison import run_category_comparison
            run_category_comparison()
            print("✅ Category analysis completed!")
            
        elif args.command == 'all':
            print("🎯 Running all analyses...")
            
            print("\n1️⃣ Running Unstructured benchmark...")
            from unstructured_only_benchmark import UnstructuredOnlyBenchmark
            benchmark = UnstructuredOnlyBenchmark()
            results = benchmark.run_benchmarks()
            
            if results:
                benchmark.save_results()
                benchmark.print_summary()
                benchmark.generate_report()
            
            print("\n2️⃣ Running category analysis...")
            from run_category_chunk_comparison import run_category_comparison
            run_category_comparison()
            
            print("\n✅ All analyses completed!")
            print("\n📄 Reports generated in 'reports/' directory")
            print("📊 Data files in 'data/' directory")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements_unstructured_only.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running {args.command}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
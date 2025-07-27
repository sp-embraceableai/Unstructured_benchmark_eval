#!/usr/bin/env python3
"""
Unstructured vs Docling Performance Benchmark Framework
Main Entry Point

This script provides easy access to all main functionalities:
1. Basic benchmarking (Unstructured only)
2. Chunk quality comparison
3. Category-based analysis
4. Advanced Docling testing
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Unstructured vs Docling Performance Benchmark Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py benchmark                    # Run basic Unstructured benchmark
  python main.py quality                      # Run chunk quality comparison
  python main.py category                     # Run category-based analysis
  python main.py test-docling                 # Test advanced Docling features
  python main.py all                          # Run all analyses
        """
    )
    
    parser.add_argument(
        'command',
        choices=['benchmark', 'quality', 'category', 'test-docling', 'all'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
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
            print("🚀 Running basic Unstructured benchmark...")
            from benchmark_runner import UnstructuredBenchmark
            benchmark = UnstructuredBenchmark()
            benchmark.run_benchmarks()
            print("✅ Basic benchmark completed!")
            
        elif args.command == 'quality':
            print("🔍 Running chunk quality comparison...")
            from chunk_quality_comparison import main as quality_main
            quality_main()
            print("✅ Quality comparison completed!")
            
        elif args.command == 'category':
            print("📊 Running category-based analysis...")
            from run_category_chunk_comparison import run_category_comparison
            run_category_comparison()
            print("✅ Category analysis completed!")
            
        elif args.command == 'test-docling':
            print("🧪 Testing advanced Docling features...")
            from test_advanced_docling import main as test_main
            test_main()
            print("✅ Docling testing completed!")
            
        elif args.command == 'all':
            print("🎯 Running all analyses...")
            
            print("\n1️⃣ Running basic benchmark...")
            from benchmark_runner import UnstructuredBenchmark
            benchmark = UnstructuredBenchmark()
            benchmark.run_benchmarks()
            
            print("\n2️⃣ Running quality comparison...")
            from chunk_quality_comparison import main as quality_main
            quality_main()
            
            print("\n3️⃣ Running category analysis...")
            from run_category_chunk_comparison import run_category_comparison
            run_category_comparison()
            
            print("\n4️⃣ Testing Docling features...")
            from test_advanced_docling import main as test_main
            test_main()
            
            print("\n✅ All analyses completed!")
            print("\n📄 Reports generated in 'reports/' directory")
            print("📊 Data files in 'data/' directory")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running {args.command}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
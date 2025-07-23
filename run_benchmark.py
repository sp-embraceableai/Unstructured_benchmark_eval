#!/usr/bin/env python3
"""
Quick Benchmark Runner

This script orchestrates the entire benchmarking process:
1. Setup folder structure
2. Download/organize PDFs
3. Run benchmarks
4. Analyze results
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import unstructured
        print("✅ Unstructured installed")
    except ImportError:
        print("❌ Unstructured not installed. Run: pip install -r requirements.txt")
        return False
    
    try:
        import torch
        if torch.cuda.is_available():
            print("✅ GPU available")
        else:
            print("⚠️  GPU not available (will use CPU)")
    except ImportError:
        print("⚠️  PyTorch not installed")
    
    return True

def main():
    """Main function to run the complete benchmark"""
    print("🚀 Unstructured Performance Benchmark")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 1: Create folder structure
    if not run_command("python download_organizer.py --create-folders", 
                      "Creating folder structure"):
        sys.exit(1)
    
    # Step 2: Generate download guide
    if not run_command("python download_organizer.py --guide", 
                      "Generating download guide"):
        sys.exit(1)
    
    # Step 3: Check if PDFs are already downloaded
    print("\n🔍 Checking for existing PDFs...")
    benchmarks_dir = Path("benchmarks")
    pdf_count = 0
    
    for category in ["short_text", "long_text", "table_heavy", "image_heavy"]:
        category_dir = benchmarks_dir / category
        if category_dir.exists():
            pdfs = list(category_dir.glob("*.pdf"))
            pdf_count += len(pdfs)
            print(f"  {category}: {len(pdfs)} PDFs")
    
    if pdf_count == 0:
        print("\n⚠️  No PDFs found!")
        print("📝 Please download German PDFs manually:")
        print("1. Check 'download_guide.md' for instructions")
        print("2. Download PDFs from the listed sources")
        print("3. Place them in the appropriate folders under 'benchmarks/'")
        print("4. Run this script again")
        print("\n💡 Or try automatic download (may not work for all URLs):")
        print("python download_organizer.py --download")
        sys.exit(1)
    
    print(f"✅ Found {pdf_count} PDFs ready for benchmarking")
    
    # Step 4: Run benchmarks
    if not run_command("python benchmark_runner.py", 
                      "Running Unstructured benchmarks"):
        sys.exit(1)
    
    # Step 5: Analyze results
    if not run_command("python advanced_analyzer.py", 
                      "Analyzing benchmark results"):
        sys.exit(1)
    
    # Step 6: Show summary
    print("\n🎉 Benchmark completed successfully!")
    print("=" * 50)
    print("📊 Results available:")
    print("  • benchmark_results.json - Raw data")
    print("  • benchmark.log - Processing logs")
    print("  • analysis_plots/ - Visualizations")
    print("  • advanced_analysis_report.md - Detailed report")
    print("  • download_guide.md - PDF download instructions")
    
    # Check if results files exist
    results_file = Path("benchmark_results.json")
    if results_file.exists():
        print(f"\n📈 Quick Summary:")
        try:
            import json
            with open(results_file, 'r') as f:
                data = json.load(f)
            
            total_docs = data.get('total_documents', 0)
            gpu_available = data.get('gpu_available', False)
            
            print(f"  • Total documents processed: {total_docs}")
            print(f"  • GPU used: {'Yes' if gpu_available else 'No'}")
            
            # Show category breakdown
            if 'results' in data:
                categories = {}
                for result in data['results']:
                    cat = result.get('document_type', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print(f"  • Documents by category:")
                for cat, count in categories.items():
                    print(f"    - {cat}: {count}")
                    
        except Exception as e:
            print(f"  • Could not read results: {e}")
    
    print("\n🔍 Next steps:")
    print("1. Review 'advanced_analysis_report.md' for detailed insights")
    print("2. Open 'analysis_plots/interactive_dashboard.html' for interactive visualizations")
    print("3. Check 'benchmark.log' for any processing issues")
    print("4. Add more PDFs to test different document types")

if __name__ == "__main__":
    main() 
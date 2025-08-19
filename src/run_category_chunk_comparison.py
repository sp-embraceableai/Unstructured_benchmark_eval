#!/usr/bin/env python3
"""
Category-based Chunk Quality Comparison

This script runs chunk quality comparison on multiple PDFs from each category:
- short_text
- long_text  
- table_heavy
- image_heavy
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List, Any
from chunk_quality_comparison import ChunkQualityAnalyzer

def run_category_comparison():
    """Run chunk quality comparison on multiple PDFs from each category"""
    
    analyzer = ChunkQualityAnalyzer()
    categories = ["short_text", "long_text", "table_heavy", "image_heavy"]
    
    # Define how many PDFs to analyze per category (limit to avoid long runtime)
    pdfs_per_category = {
        "short_text": 2,      # All available
        "long_text": 1,       # All available  
        "table_heavy": 3,     # Sample from many available
        "image_heavy": 1      # All available
    }
    
    all_results = {}
    category_summaries = {}
    
    print("🔍 Starting category-based chunk quality comparison...")
    print("=" * 60)
    
    for category in categories:
        print(f"\n📁 Processing category: {category}")
        print("-" * 40)
        
        category_dir = Path("benchmarks") / category
        if not category_dir.exists():
            print(f"❌ Category directory not found: {category_dir}")
            continue
        
        # Get PDF files in category
        pdf_files = list(category_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {category}")
            continue
        
        # Limit number of PDFs to process
        max_pdfs = pdfs_per_category.get(category, 2)
        pdf_files = pdf_files[:max_pdfs]
        
        print(f"📊 Found {len(pdf_files)} PDFs to analyze")
        
        category_results = []
        category_metrics = {
            "unstructured_wins": 0,
            "docling_wins": 0,
            "ties": 0,
            "total_documents": 0,
            "avg_content_overlap": 0.0,
            "avg_chunk_count_ratio": 0.0,
            "avg_readability_ratio": 0.0,
            "avg_coherence_ratio": 0.0,
            "avg_completeness_ratio": 0.0
        }
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                # Run chunk quality comparison
                result = analyzer.compare_chunk_quality(pdf_file)
                
                if "error" in result:
                    print(f"❌ Error processing {pdf_file.name}: {result['error']}")
                    continue
                
                # Add category information
                result["category"] = category
                result["file_size_mb"] = pdf_file.stat().st_size / (1024 * 1024)
                
                category_results.append(result)
                category_metrics["total_documents"] += 1
                
                # Analyze winner
                summary = result["comparison_summary"]
                u_metrics = result["unstructured_metrics"]
                d_metrics = result["docling_metrics"]
                
                # Count wins for each metric
                metrics = [
                    ("readability_score", u_metrics["readability_score"], d_metrics["readability_score"]),
                    ("coherence_score", u_metrics["coherence_score"], d_metrics["coherence_score"]),
                    ("completeness_score", u_metrics["completeness_score"], d_metrics["completeness_score"]),
                    ("information_density", u_metrics["information_density"], d_metrics["information_density"]),
                    ("structural_preservation", u_metrics["structural_preservation"], d_metrics["structural_preservation"]),
                    ("language_quality", u_metrics["language_quality"], d_metrics["language_quality"]),
                    ("semantic_continuity", u_metrics["semantic_continuity"], d_metrics["semantic_continuity"])
                ]
                
                unstructured_wins = sum(1 for _, u, d in metrics if u > d)
                docling_wins = sum(1 for _, u, d in metrics if d > u)
                ties = sum(1 for _, u, d in metrics if u == d)
                
                if unstructured_wins > docling_wins:
                    category_metrics["unstructured_wins"] += 1
                elif docling_wins > unstructured_wins:
                    category_metrics["docling_wins"] += 1
                else:
                    category_metrics["ties"] += 1
                
                # Accumulate averages
                category_metrics["avg_content_overlap"] += summary["content_overlap"]
                category_metrics["avg_chunk_count_ratio"] += summary["chunk_count_ratio"]
                category_metrics["avg_readability_ratio"] += summary["readability_ratio"]
                category_metrics["avg_coherence_ratio"] += summary["coherence_ratio"]
                category_metrics["avg_completeness_ratio"] += summary["completeness_ratio"]
                
                print(f"✅ Completed: {pdf_file.name}")
                print(f"   Chunks: U={u_metrics['chunk_count']}, D={d_metrics['chunk_count']}")
                print(f"   Content Overlap: {summary['content_overlap']:.2f}")
                print(f"   Winner: {'Unstructured' if unstructured_wins > docling_wins else 'Docling' if docling_wins > unstructured_wins else 'Tie'}")
                
            except Exception as e:
                print(f"❌ Failed to process {pdf_file.name}: {str(e)}")
                continue
        
        # Calculate averages
        if category_metrics["total_documents"] > 0:
            category_metrics["avg_content_overlap"] /= category_metrics["total_documents"]
            category_metrics["avg_chunk_count_ratio"] /= category_metrics["total_documents"]
            category_metrics["avg_readability_ratio"] /= category_metrics["total_documents"]
            category_metrics["avg_coherence_ratio"] /= category_metrics["total_documents"]
            category_metrics["avg_completeness_ratio"] /= category_metrics["total_documents"]
        
        all_results[category] = category_results
        category_summaries[category] = category_metrics
        
        print(f"\n📊 Category Summary for {category}:")
        print(f"   Documents processed: {category_metrics['total_documents']}")
        print(f"   Unstructured wins: {category_metrics['unstructured_wins']}")
        print(f"   Docling wins: {category_metrics['docling_wins']}")
        print(f"   Ties: {category_metrics['ties']}")
        print(f"   Avg content overlap: {category_metrics['avg_content_overlap']:.2f}")
        print(f"   Avg chunk count ratio: {category_metrics['avg_chunk_count_ratio']:.2f}")
    
    # Generate comprehensive report
    generate_category_report(all_results, category_summaries)
    
    return all_results, category_summaries

def generate_category_report(all_results: Dict, category_summaries: Dict):
    """Generate a comprehensive category-based comparison report"""
    
    report = []
    report.append("# Category-Based Chunk Quality Comparison Report")
    report.append(f"\n**Analysis Date:** {Path(__file__).stat().st_mtime}")
    report.append("")
    
    # Overall summary
    report.append("## 📊 Overall Summary")
    report.append("")
    
    total_docs = sum(summary["total_documents"] for summary in category_summaries.values())
    total_unstructured_wins = sum(summary["unstructured_wins"] for summary in category_summaries.values())
    total_docling_wins = sum(summary["docling_wins"] for summary in category_summaries.values())
    total_ties = sum(summary["ties"] for summary in category_summaries.values())
    
    report.append(f"- **Total Documents Analyzed:** {total_docs}")
    report.append(f"- **Total Unstructured Wins:** {total_unstructured_wins}")
    report.append(f"- **Total Docling Wins:** {total_docling_wins}")
    report.append(f"- **Total Ties:** {total_ties}")
    report.append(f"- **Overall Winner:** {'Unstructured' if total_unstructured_wins > total_docling_wins else 'Docling' if total_docling_wins > total_unstructured_wins else 'Tie'}")
    report.append("")
    
    # Category-by-category analysis
    report.append("## 📈 Category-by-Category Analysis")
    report.append("")
    
    for category, summary in category_summaries.items():
        if summary["total_documents"] == 0:
            continue
            
        report.append(f"### {category.replace('_', ' ').title()}")
        report.append("")
        report.append(f"- **Documents Processed:** {summary['total_documents']}")
        report.append(f"- **Unstructured Wins:** {summary['unstructured_wins']}")
        report.append(f"- **Docling Wins:** {summary['docling_wins']}")
        report.append(f"- **Ties:** {summary['ties']}")
        report.append(f"- **Category Winner:** {'Unstructured' if summary['unstructured_wins'] > summary['docling_wins'] else 'Docling' if summary['docling_wins'] > summary['unstructured_wins'] else 'Tie'}")
        report.append(f"- **Avg Content Overlap:** {summary['avg_content_overlap']:.2f}")
        report.append(f"- **Avg Chunk Count Ratio:** {summary['avg_chunk_count_ratio']:.2f}")
        report.append(f"- **Avg Readability Ratio:** {summary['avg_readability_ratio']:.2f}")
        report.append(f"- **Avg Coherence Ratio:** {summary['avg_coherence_ratio']:.2f}")
        report.append(f"- **Avg Completeness Ratio:** {summary['avg_completeness_ratio']:.2f}")
        report.append("")
    
    # Detailed results table
    report.append("## 📋 Detailed Results")
    report.append("")
    report.append("| Category | Document | File Size (MB) | U Chunks | D Chunks | Content Overlap | Winner |")
    report.append("|----------|----------|----------------|----------|----------|-----------------|--------|")
    
    for category, results in all_results.items():
        for result in results:
            if "error" in result:
                continue
                
            u_chunks = result["unstructured_metrics"]["chunk_count"]
            d_chunks = result["docling_metrics"]["chunk_count"]
            content_overlap = result["comparison_summary"]["content_overlap"]
            
            # Determine winner
            u_metrics = result["unstructured_metrics"]
            d_metrics = result["docling_metrics"]
            
            metrics = [
                ("readability_score", u_metrics["readability_score"], d_metrics["readability_score"]),
                ("coherence_score", u_metrics["coherence_score"], d_metrics["coherence_score"]),
                ("completeness_score", u_metrics["completeness_score"], d_metrics["completeness_score"]),
                ("information_density", u_metrics["information_density"], d_metrics["information_density"]),
                ("structural_preservation", u_metrics["structural_preservation"], d_metrics["structural_preservation"]),
                ("language_quality", u_metrics["language_quality"], d_metrics["language_quality"]),
                ("semantic_continuity", u_metrics["semantic_continuity"], d_metrics["semantic_continuity"])
            ]
            
            unstructured_wins = sum(1 for _, u, d in metrics if u > d)
            docling_wins = sum(1 for _, u, d in metrics if d > u)
            
            if unstructured_wins > docling_wins:
                winner = "Unstructured"
            elif docling_wins > unstructured_wins:
                winner = "Docling"
            else:
                winner = "Tie"
            
            report.append(f"| {category} | {result['document']} | {result['file_size_mb']:.2f} | {u_chunks} | {d_chunks} | {content_overlap:.2f} | {winner} |")
    
    report.append("")
    
    # Key insights
    report.append("## 🎯 Key Insights")
    report.append("")
    
    # Find best performing category for each method
    best_unstructured_category = max(category_summaries.items(), 
                                   key=lambda x: x[1]["unstructured_wins"] if x[1]["total_documents"] > 0 else 0)[0]
    best_docling_category = max(category_summaries.items(), 
                              key=lambda x: x[1]["docling_wins"] if x[1]["total_documents"] > 0 else 0)[0]
    
    report.append(f"- **Best Category for Unstructured:** {best_unstructured_category}")
    report.append(f"- **Best Category for Docling:** {best_docling_category}")
    report.append(f"- **Most Content Overlap:** {max(category_summaries.items(), key=lambda x: x[1]['avg_content_overlap'])[0]}")
    report.append(f"- **Most Variable Chunking:** {max(category_summaries.items(), key=lambda x: x[1]['avg_chunk_count_ratio'])[0]}")
    report.append("")
    
    # Recommendations
    report.append("## 🚀 Recommendations by Category")
    report.append("")
    
    for category, summary in category_summaries.items():
        if summary["total_documents"] == 0:
            continue
            
        report.append(f"### {category.replace('_', ' ').title()}:")
        
        if summary["unstructured_wins"] > summary["docling_wins"]:
            report.append("- **Recommendation:** Use Unstructured for better quality")
            report.append("- **Reason:** Superior performance across quality metrics")
        elif summary["docling_wins"] > summary["unstructured_wins"]:
            report.append("- **Recommendation:** Use Docling for better performance")
            report.append("- **Reason:** Better performance in this document type")
        else:
            report.append("- **Recommendation:** Both methods perform similarly")
            report.append("- **Reason:** Consider speed vs quality trade-off")
        
        report.append(f"- **Content Overlap:** {summary['avg_content_overlap']:.2f} (similar content extraction)")
        report.append(f"- **Chunk Granularity:** {summary['avg_chunk_count_ratio']:.2f}x more chunks with Docling")
        report.append("")
    
    # Save report
    with open("category_chunk_quality_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"\n✅ Category-based comparison completed!")
    print(f"📄 Report saved to: category_chunk_quality_report.md")
    print(f"📊 Total documents analyzed: {total_docs}")
    print(f"🏆 Overall winner: {'Unstructured' if total_unstructured_wins > total_docling_wins else 'Docling' if total_docling_wins > total_unstructured_wins else 'Tie'}")

if __name__ == "__main__":
    run_category_comparison() 
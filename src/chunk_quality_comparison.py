#!/usr/bin/env python3
"""
Chunk Quality Comparison between Unstructured and Docling

This script provides a comprehensive analysis of chunk quality across multiple dimensions:
- Content coherence and readability
- Chunk size distribution and consistency
- Semantic completeness
- Information density
- Structural preservation
- Language quality metrics
"""

import json
import re
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from benchmark_runner import UnstructuredBenchmark

@dataclass
class ChunkQualityMetrics:
    """Metrics for evaluating chunk quality"""
    chunk_count: int
    avg_chunk_size_words: float
    avg_chunk_size_chars: float
    chunk_size_std: float
    readability_score: float
    coherence_score: float
    completeness_score: float
    information_density: float
    structural_preservation: float
    language_quality: float
    content_overlap: float
    semantic_continuity: float

class ChunkQualityAnalyzer:
    def __init__(self):
        self.benchmark = UnstructuredBenchmark()
    
    def analyze_readability(self, text: str) -> float:
        """Calculate readability score using Flesch Reading Ease"""
        try:
            sentences = len(re.split(r'[.!?]+', text))
            words = len(text.split())
            syllables = len(re.findall(r'[aeiouy]+', text.lower()))
            
            if sentences == 0 or words == 0:
                return 0.0
            
            # Flesch Reading Ease formula
            score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            return max(0.0, min(100.0, score))
        except:
            return 0.0
    
    def analyze_coherence(self, chunks: List[str]) -> float:
        """Analyze coherence between chunks"""
        if len(chunks) < 2:
            return 1.0
        
        coherence_scores = []
        for i in range(len(chunks) - 1):
            chunk1 = chunks[i].lower()
            chunk2 = chunks[i + 1].lower()
            
            # Calculate word overlap
            words1 = set(chunk1.split())
            words2 = set(chunk2.split())
            
            if len(words1) == 0 or len(words2) == 0:
                coherence_scores.append(0.0)
                continue
            
            overlap = len(words1.intersection(words2))
            total_unique = len(words1.union(words2))
            coherence_scores.append(overlap / total_unique if total_unique > 0 else 0.0)
        
        return statistics.mean(coherence_scores) if coherence_scores else 0.0
    
    def analyze_completeness(self, chunks: List[str]) -> float:
        """Analyze semantic completeness of chunks"""
        completeness_scores = []
        
        for chunk in chunks:
            # Check for incomplete sentences at chunk boundaries
            sentences = re.split(r'[.!?]+', chunk.strip())
            if len(sentences) > 1:
                # Check if last sentence is complete
                last_sentence = sentences[-1].strip()
                if len(last_sentence.split()) < 3:  # Very short sentence
                    completeness_scores.append(0.8)
                else:
                    completeness_scores.append(1.0)
            else:
                completeness_scores.append(1.0)
        
        return statistics.mean(completeness_scores) if completeness_scores else 0.0
    
    def analyze_information_density(self, chunks: List[str]) -> float:
        """Analyze information density (unique words vs total words)"""
        if not chunks:
            return 0.0
        
        total_words = 0
        unique_words = set()
        
        for chunk in chunks:
            words = chunk.lower().split()
            total_words += len(words)
            unique_words.update(words)
        
        if total_words == 0:
            return 0.0
        
        return len(unique_words) / total_words
    
    def analyze_structural_preservation(self, chunks: List[str]) -> float:
        """Analyze preservation of document structure"""
        structural_indicators = 0
        total_indicators = 0
        
        for chunk in chunks:
            # Check for structural elements
            has_headers = bool(re.search(r'^#{1,6}\s+', chunk, re.MULTILINE))
            has_lists = bool(re.search(r'^[\*\-]\s+', chunk, re.MULTILINE))
            has_numbers = bool(re.search(r'^\d+\.\s+', chunk, re.MULTILINE))
            has_paragraphs = chunk.count('\n\n') > 0
            
            total_indicators += 4
            structural_indicators += sum([has_headers, has_lists, has_numbers, has_paragraphs])
        
        return structural_indicators / total_indicators if total_indicators > 0 else 0.0
    
    def analyze_language_quality(self, chunks: List[str]) -> float:
        """Analyze language quality metrics"""
        quality_scores = []
        
        for chunk in chunks:
            # Check for proper capitalization
            sentences = re.split(r'[.!?]+', chunk)
            proper_caps = 0
            total_sentences = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 0:
                    total_sentences += 1
                    if sentence[0].isupper():
                        proper_caps += 1
            
            cap_score = proper_caps / total_sentences if total_sentences > 0 else 1.0
            
            # Check for punctuation
            punct_score = min(1.0, chunk.count('.') + chunk.count('!') + chunk.count('?') / len(chunk.split()))
            
            # Check for spelling (basic check for common words)
            common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            word_score = sum(1 for word in chunk.lower().split() if word in common_words) / len(chunk.split()) if chunk.split() else 0
            
            quality_scores.append((cap_score + punct_score + word_score) / 3)
        
        return statistics.mean(quality_scores) if quality_scores else 0.0
    
    def analyze_content_overlap(self, unstructured_chunks: List[str], docling_chunks: List[str]) -> float:
        """Analyze content overlap between Unstructured and Docling chunks"""
        if not unstructured_chunks or not docling_chunks:
            return 0.0
        
        # Combine all chunks for each method
        unstructured_text = ' '.join(unstructured_chunks).lower()
        docling_text = ' '.join(docling_chunks).lower()
        
        # Extract unique words
        unstructured_words = set(unstructured_text.split())
        docling_words = set(docling_text.split())
        
        if len(unstructured_words) == 0 or len(docling_words) == 0:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(unstructured_words.intersection(docling_words))
        union = len(unstructured_words.union(docling_words))
        
        return intersection / union if union > 0 else 0.0
    
    def analyze_semantic_continuity(self, chunks: List[str]) -> float:
        """Analyze semantic continuity between chunks"""
        if len(chunks) < 2:
            return 1.0
        
        continuity_scores = []
        
        for i in range(len(chunks) - 1):
            chunk1 = chunks[i]
            chunk2 = chunks[i + 1]
            
            # Check for semantic connectors
            connectors = ['however', 'therefore', 'furthermore', 'moreover', 'additionally', 
                        'consequently', 'thus', 'hence', 'meanwhile', 'subsequently']
            
            connector_count = sum(1 for connector in connectors if connector in chunk2.lower())
            
            # Check for topic continuity (shared key terms)
            words1 = set(chunk1.lower().split())
            words2 = set(chunk2.lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words1 = words1 - stop_words
            words2 = words2 - stop_words
            
            shared_terms = len(words1.intersection(words2))
            total_terms = len(words1.union(words2))
            
            term_similarity = shared_terms / total_terms if total_terms > 0 else 0.0
            
            # Combine connector and term similarity
            continuity_score = (term_similarity * 0.7) + (min(1.0, connector_count * 0.3))
            continuity_scores.append(continuity_score)
        
        return statistics.mean(continuity_scores) if continuity_scores else 0.0
    
    def analyze_chunk_quality(self, chunks: List[str], method_name: str) -> ChunkQualityMetrics:
        """Comprehensive chunk quality analysis"""
        if not chunks:
            return ChunkQualityMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Basic metrics
        chunk_sizes_words = [len(chunk.split()) for chunk in chunks]
        chunk_sizes_chars = [len(chunk) for chunk in chunks]
        
        avg_words = statistics.mean(chunk_sizes_words)
        avg_chars = statistics.mean(chunk_sizes_chars)
        std_words = statistics.stdev(chunk_sizes_words) if len(chunk_sizes_words) > 1 else 0
        
        # Quality metrics
        readability_scores = [self.analyze_readability(chunk) for chunk in chunks]
        avg_readability = statistics.mean(readability_scores)
        
        coherence = self.analyze_coherence(chunks)
        completeness = self.analyze_completeness(chunks)
        info_density = self.analyze_information_density(chunks)
        structural = self.analyze_structural_preservation(chunks)
        language = self.analyze_language_quality(chunks)
        continuity = self.analyze_semantic_continuity(chunks)
        
        return ChunkQualityMetrics(
            chunk_count=len(chunks),
            avg_chunk_size_words=avg_words,
            avg_chunk_size_chars=avg_chars,
            chunk_size_std=std_words,
            readability_score=avg_readability,
            coherence_score=coherence,
            completeness_score=completeness,
            information_density=info_density,
            structural_preservation=structural,
            language_quality=language,
            content_overlap=0.0,  # Will be calculated in comparison
            semantic_continuity=continuity
        )
    
    def compare_chunk_quality(self, file_path: Path) -> Dict[str, Any]:
        """Compare chunk quality between Unstructured and Docling"""
        print(f"🔍 Analyzing chunk quality for: {file_path.name}")
        
        # Get chunks from both methods
        try:
            # Unstructured chunks
            from unstructured.partition.auto import partition
            from unstructured.documents.elements import Table
            
            elements = partition(str(file_path), strategy="hi_res")
            
            # Extract text content and apply smart chunking
            all_text = ""
            for element in elements:
                if hasattr(element, 'text') and element.text and not isinstance(element, Table):
                    all_text += element.text + "\n\n"
            
            unstructured_chunks = self.benchmark.smart_chunk_text(all_text, max_words_per_chunk=500)
            
            # Docling chunks using advanced chunking
            advanced_results = self.benchmark.advanced_docling_chunking(file_path)
            
            if "error" in advanced_results:
                print(f"❌ Docling failed: {advanced_results['error']}")
                return {"error": advanced_results['error']}
            
            # Use semantic chunking results for comparison
            docling_chunks = advanced_results["semantic"]["chunks"]
            
            print(f"📊 Unstructured: {len(unstructured_chunks)} chunks")
            print(f"📊 Docling: {len(docling_chunks)} chunks")
            
            # Analyze quality for each method
            unstructured_metrics = self.analyze_chunk_quality(unstructured_chunks, "Unstructured")
            docling_metrics = self.analyze_chunk_quality(docling_chunks, "Docling")
            
            # Calculate content overlap
            content_overlap = self.analyze_content_overlap(unstructured_chunks, docling_chunks)
            unstructured_metrics.content_overlap = content_overlap
            docling_metrics.content_overlap = content_overlap
            
            # Create comparison report
            comparison = {
                "document": file_path.name,
                "unstructured_metrics": unstructured_metrics.__dict__,
                "docling_metrics": docling_metrics.__dict__,
                "unstructured_chunks": unstructured_chunks,
                "docling_chunks": docling_chunks,
                "comparison_summary": {
                    "chunk_count_ratio": len(docling_chunks) / len(unstructured_chunks) if unstructured_chunks else 0,
                    "avg_size_ratio": docling_metrics.avg_chunk_size_words / unstructured_metrics.avg_chunk_size_words if unstructured_metrics.avg_chunk_size_words > 0 else 0,
                    "readability_ratio": docling_metrics.readability_score / unstructured_metrics.readability_score if unstructured_metrics.readability_score > 0 else 0,
                    "coherence_ratio": docling_metrics.coherence_score / unstructured_metrics.coherence_score if unstructured_metrics.coherence_score > 0 else 0,
                    "completeness_ratio": docling_metrics.completeness_score / unstructured_metrics.completeness_score if unstructured_metrics.completeness_score > 0 else 0,
                    "content_overlap": content_overlap
                }
            }
            
            return comparison
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_quality_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed quality comparison report"""
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        report = []
        report.append("# Chunk Quality Comparison Report")
        report.append(f"\n**Document:** {results['document']}")
        report.append(f"**Analysis Date:** {Path(__file__).stat().st_mtime}")
        report.append("")
        
        # Summary metrics
        summary = results['comparison_summary']
        report.append("## 📊 Summary Comparison")
        report.append("")
        report.append(f"- **Chunk Count Ratio (Docling/Unstructured):** {summary['chunk_count_ratio']:.2f}")
        report.append(f"- **Average Size Ratio (Docling/Unstructured):** {summary['avg_size_ratio']:.2f}")
        report.append(f"- **Readability Ratio (Docling/Unstructured):** {summary['readability_ratio']:.2f}")
        report.append(f"- **Coherence Ratio (Docling/Unstructured):** {summary['coherence_ratio']:.2f}")
        report.append(f"- **Completeness Ratio (Docling/Unstructured):** {summary['completeness_ratio']:.2f}")
        report.append(f"- **Content Overlap:** {summary['content_overlap']:.2f}")
        report.append("")
        
        # Detailed metrics
        u_metrics = results['unstructured_metrics']
        d_metrics = results['docling_metrics']
        
        report.append("## 📈 Detailed Quality Metrics")
        report.append("")
        report.append("| Metric | Unstructured | Docling | Ratio |")
        report.append("|--------|--------------|---------|-------|")
        
        # Calculate ratios with proper error handling
        chunk_count_ratio = d_metrics['chunk_count']/u_metrics['chunk_count'] if u_metrics['chunk_count'] > 0 else 0
        avg_size_ratio = d_metrics['avg_chunk_size_words']/u_metrics['avg_chunk_size_words'] if u_metrics['avg_chunk_size_words'] > 0 else 0
        avg_size_chars_ratio = d_metrics['avg_chunk_size_chars']/u_metrics['avg_chunk_size_chars'] if u_metrics['avg_chunk_size_chars'] > 0 else 0
        std_dev_ratio = d_metrics['chunk_size_std']/u_metrics['chunk_size_std'] if u_metrics['chunk_size_std'] > 0 else 0
        readability_ratio = d_metrics['readability_score']/u_metrics['readability_score'] if u_metrics['readability_score'] > 0 else 0
        coherence_ratio = d_metrics['coherence_score']/u_metrics['coherence_score'] if u_metrics['coherence_score'] > 0 else 0
        completeness_ratio = d_metrics['completeness_score']/u_metrics['completeness_score'] if u_metrics['completeness_score'] > 0 else 0
        info_density_ratio = d_metrics['information_density']/u_metrics['information_density'] if u_metrics['information_density'] > 0 else 0
        structural_ratio = d_metrics['structural_preservation']/u_metrics['structural_preservation'] if u_metrics['structural_preservation'] > 0 else 0
        language_ratio = d_metrics['language_quality']/u_metrics['language_quality'] if u_metrics['language_quality'] > 0 else 0
        continuity_ratio = d_metrics['semantic_continuity']/u_metrics['semantic_continuity'] if u_metrics['semantic_continuity'] > 0 else 0
        
        report.append(f"| Chunk Count | {u_metrics['chunk_count']} | {d_metrics['chunk_count']} | {chunk_count_ratio:.2f} |")
        report.append(f"| Avg Size (words) | {u_metrics['avg_chunk_size_words']:.1f} | {d_metrics['avg_chunk_size_words']:.1f} | {avg_size_ratio:.2f} |")
        report.append(f"| Avg Size (chars) | {u_metrics['avg_chunk_size_chars']:.1f} | {d_metrics['avg_chunk_size_chars']:.1f} | {avg_size_chars_ratio:.2f} |")
        report.append(f"| Size Std Dev | {u_metrics['chunk_size_std']:.1f} | {d_metrics['chunk_size_std']:.1f} | {std_dev_ratio:.2f} |")
        report.append(f"| Readability | {u_metrics['readability_score']:.1f} | {d_metrics['readability_score']:.1f} | {readability_ratio:.2f} |")
        report.append(f"| Coherence | {u_metrics['coherence_score']:.3f} | {d_metrics['coherence_score']:.3f} | {coherence_ratio:.2f} |")
        report.append(f"| Completeness | {u_metrics['completeness_score']:.3f} | {d_metrics['completeness_score']:.3f} | {completeness_ratio:.2f} |")
        report.append(f"| Info Density | {u_metrics['information_density']:.3f} | {d_metrics['information_density']:.3f} | {info_density_ratio:.2f} |")
        report.append(f"| Structural | {u_metrics['structural_preservation']:.3f} | {d_metrics['structural_preservation']:.3f} | {structural_ratio:.2f} |")
        report.append(f"| Language | {u_metrics['language_quality']:.3f} | {d_metrics['language_quality']:.3f} | {language_ratio:.2f} |")
        report.append(f"| Continuity | {u_metrics['semantic_continuity']:.3f} | {d_metrics['semantic_continuity']:.3f} | {continuity_ratio:.2f} |")
        report.append("")
        
        # Quality assessment
        report.append("## 🎯 Quality Assessment")
        report.append("")
        
        # Determine winner for each metric
        metrics = [
            ("Readability", u_metrics['readability_score'], d_metrics['readability_score']),
            ("Coherence", u_metrics['coherence_score'], d_metrics['coherence_score']),
            ("Completeness", u_metrics['completeness_score'], d_metrics['completeness_score']),
            ("Information Density", u_metrics['information_density'], d_metrics['information_density']),
            ("Structural Preservation", u_metrics['structural_preservation'], d_metrics['structural_preservation']),
            ("Language Quality", u_metrics['language_quality'], d_metrics['language_quality']),
            ("Semantic Continuity", u_metrics['semantic_continuity'], d_metrics['semantic_continuity'])
        ]
        
        unstructured_wins = 0
        docling_wins = 0
        
        for metric_name, u_score, d_score in metrics:
            if u_score > d_score:
                winner = "Unstructured"
                unstructured_wins += 1
            elif d_score > u_score:
                winner = "Docling"
                docling_wins += 1
            else:
                winner = "Tie"
            
            report.append(f"- **{metric_name}:** {winner} (U: {u_score:.3f}, D: {d_score:.3f})")
        
        report.append("")
        report.append(f"**Overall Winner:** {'Unstructured' if unstructured_wins > docling_wins else 'Docling' if docling_wins > unstructured_wins else 'Tie'}")
        report.append(f"**Score:** Unstructured {unstructured_wins} - Docling {docling_wins}")
        report.append("")
        
        # Sample chunks comparison
        report.append("## 📝 Sample Chunks Comparison")
        report.append("")
        
        u_chunks = results['unstructured_chunks']
        d_chunks = results['docling_chunks']
        
        report.append("### Unstructured Chunks:")
        for i, chunk in enumerate(u_chunks[:2]):  # Show first 2 chunks
            report.append(f"\n**Chunk {i+1}:** ({len(chunk.split())} words)")
            report.append(f"```\n{chunk[:500]}{'...' if len(chunk) > 500 else ''}\n```")
        
        report.append("\n### Docling Chunks:")
        for i, chunk in enumerate(d_chunks[:2]):  # Show first 2 chunks
            report.append(f"\n**Chunk {i+1}:** ({len(chunk.split())} words)")
            report.append(f"```\n{chunk[:500]}{'...' if len(chunk) > 500 else ''}\n```")
        
        return "\n".join(report)

def main():
    """Main function to run chunk quality comparison"""
    analyzer = ChunkQualityAnalyzer()
    
    # Find a test PDF
    test_pdf = None
    for category in ["short_text", "long_text", "table_heavy", "image_heavy"]:
        category_dir = Path("benchmarks") / category
        if category_dir.exists():
            pdf_files = list(category_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf = pdf_files[0]
                break
    
    if not test_pdf:
        print("❌ No test PDF found")
        return
    
    print(f"🔍 Comparing chunk quality for: {test_pdf.name}")
    
    # Run comparison
    results = analyzer.compare_chunk_quality(test_pdf)
    
    if "error" in results:
        print(f"❌ Comparison failed: {results['error']}")
        return
    
    # Generate and save report
    report = analyzer.generate_quality_report(results)
    
    with open("chunk_quality_comparison_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Chunk quality comparison completed!")
    print("📄 Report saved to: chunk_quality_comparison_report.md")
    
    # Print summary
    summary = results['comparison_summary']
    print(f"\n📊 Summary:")
    print(f"   Chunk Count Ratio: {summary['chunk_count_ratio']:.2f}")
    print(f"   Average Size Ratio: {summary['avg_size_ratio']:.2f}")
    print(f"   Readability Ratio: {summary['readability_ratio']:.2f}")
    print(f"   Content Overlap: {summary['content_overlap']:.2f}")

if __name__ == "__main__":
    main() 
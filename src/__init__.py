"""
Unstructured vs Docling Performance Benchmark Framework
Source Package

This package contains the core benchmarking and analysis modules:
- benchmark_runner: Main benchmarking functionality
- chunk_quality_comparison: Quality analysis framework
- run_category_chunk_comparison: Category-based analysis
- test_advanced_docling: Advanced Docling testing
"""

__version__ = "1.0.0"
__author__ = "Benchmark Framework Team"
__description__ = "Comprehensive benchmarking framework for Unstructured vs Docling comparison"

# Import main classes for easy access
try:
    from .benchmark_runner import UnstructuredBenchmark
    from .chunk_quality_comparison import ChunkQualityAnalyzer
except ImportError:
    # Allow partial imports for development
    pass

__all__ = [
    'UnstructuredBenchmark',
    'ChunkQualityAnalyzer',
] 
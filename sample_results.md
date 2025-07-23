# Sample Benchmark Results

This file shows example output from the Unstructured performance benchmark framework.

## Quick Start Results

After running `python run_benchmark.py` with the Baden-Württemberg budget PDFs:

### 📊 Performance Summary

**Total Documents Processed**: 20
- **Short Text**: 2 documents (Bundesanzeiger notices)
- **Table Heavy**: 18 documents (Baden-Württemberg budget plans)
- **Success Rate**: 100% ✅
- **GPU Status**: CPU only

### 🔍 Performance by Category

#### Short Text Documents
- **Processing Time**: 2.1 seconds average
- **File Size**: 0.43MB average
- **Elements**: 232 total (145 text elements)
- **Chunks**: 232 chunks (199 characters average)
- **Elements/Second**: 76 elements/second

#### Table-Heavy Documents (Budget PDFs)
- **Processing Time**: 17.3 seconds average
- **File Size**: 5.8MB average (range: 0.23MB - 64MB)
- **Elements**: 430,144 total (282,107 text elements)
- **Chunks**: 430,144 chunks (22 characters average)
- **Elements/Second**: 1,535 elements/second

### 📈 Key Insights

1. **Document Complexity Impact**: Table-heavy documents take 8x longer to process
2. **Element Extraction Efficiency**: Table-heavy docs are 20x more efficient per element
3. **Chunk Generation**: Different strategies for different document types
4. **Scalability**: Linear scaling with document complexity

### 📁 Generated Files

The benchmark creates several output files:

- `benchmark_results.json` - Raw performance data
- `benchmark.log` - Processing logs
- `analysis_plots/` - Visualizations (PNG + interactive HTML)
- `advanced_analysis_report.md` - Detailed analysis report

### 🎯 Production Recommendations

- **Short documents**: Expect ~2 seconds processing time
- **Table-heavy documents**: Expect 15-80 seconds depending on size
- **Resource planning**: Large documents require significant processing time
- **Batch processing**: Consider parallel processing for large document sets

## Running Your Own Benchmark

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Add PDFs**: Place German PDFs in `benchmarks/` subdirectories
3. **Run benchmark**: `python run_benchmark.py`
4. **Analyze results**: Check generated reports and visualizations

## Document Categories

- **short_text/**: <5 pages, mostly text
- **long_text/**: >20 pages, mostly text  
- **table_heavy/**: ≥30% tables, financial data
- **image_heavy/**: Many charts, scans, graphics

The framework automatically categorizes documents and provides detailed performance analysis for each type. 
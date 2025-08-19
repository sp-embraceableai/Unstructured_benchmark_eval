# Project Structure

This document describes the organized structure of the Unstructured vs Docling Performance Benchmark Framework.

## 📁 Directory Structure

```
Unstructured_benchmark_eval/
├── README.md                           # Main project documentation
├── PROJECT_STRUCTURE.md                # This file - project structure overview
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
├── main.py                            # Main entry point script
│
├── src/                               # Source code directory
│   ├── __init__.py                    # Package initialization
│   ├── benchmark_runner.py            # Main benchmarking script
│   ├── chunk_quality_comparison.py    # Quality analysis framework
│   ├── run_category_chunk_comparison.py # Category-based analysis
│   └── test_advanced_docling.py       # Advanced Docling testing
│
├── reports/                           # Generated reports
│   ├── comprehensive_benchmark_report.md
│   ├── chunk_quality_comparison_report.md
│   ├── category_chunk_quality_report.md
│   ├── chunk_quality_comparison_summary.md
│   ├── hybrid_chunking_success_report.md
│   └── hybrid_chunking_methods.md
│
├── data/                              # Data and analysis files
│   └── analysis_plots/                # Generated visualizations
│       ├── performance_overview.png
│       ├── element_distribution.png
│       └── interactive_dashboard.html
│
└── benchmarks/                        # Test documents
    ├── short_text/                    # Short text documents
    ├── long_text/                     # Long text documents
    ├── table_heavy/                   # Table-heavy documents
    └── image_heavy/                   # Image-heavy documents
```

## 🚀 Quick Start Commands

### Using the main entry point:
```bash
# Run basic Unstructured benchmark
python main.py benchmark

# Run chunk quality comparison
python main.py quality

# Run category-based analysis
python main.py category

# Test advanced Docling features
python main.py test-docling

# Run all analyses
python main.py all
```

### Using individual scripts:
```bash
# From the src directory
cd src

# Basic benchmark
python benchmark_runner.py

# Quality comparison
python chunk_quality_comparison.py

# Category analysis
python run_category_chunk_comparison.py

# Docling testing
python test_advanced_docling.py
```

## 📊 Key Features

### 1. Main Benchmarking (`benchmark_runner.py`)
- **Unstructured processing** with hi_res strategy
- **Advanced Docling chunking** with 5 strategies
- **Smart chunking** for Unstructured (markdown-based)
- **Hybrid chunking** with adaptive strategy selection
- **Performance measurement** and error handling

### 2. Quality Analysis (`chunk_quality_comparison.py`)
- **11 quality metrics** across multiple dimensions
- **Cross-tool comparison** (Unstructured vs Docling)
- **Statistical analysis** with detailed reporting
- **Sample chunk comparison** with qualitative assessment

### 3. Category Analysis (`run_category_chunk_comparison.py`)
- **Multi-document processing** per category
- **Statistical aggregation** of results
- **Category-specific insights** and recommendations
- **Comprehensive reporting** with detailed tables

### 4. Advanced Testing (`test_advanced_docling.py`)
- **Hybrid chunking strategies** validation
- **Adaptive strategy selection** testing
- **Performance comparison** with Unstructured
- **Error handling** and debugging

## 📈 Generated Reports

### Performance Reports
- `comprehensive_benchmark_report.md` - Detailed Unstructured analysis
- `advanced_analysis_report.md` - Statistical analysis

### Quality Analysis Reports
- `chunk_quality_comparison_report.md` - Detailed quality comparison
- `category_chunk_quality_report.md` - Category-based analysis
- `chunk_quality_comparison_summary.md` - Executive summary

### Implementation Reports
- `hybrid_chunking_success_report.md` - Hybrid chunking implementation
- `hybrid_chunking_methods.md` - Chunking strategies documentation

## 🔧 Configuration

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export UNSTRUCTURED_HIDE_PROGRESS_BAR=false
export UNSTRUCTURED_GPU_ENABLED=true
```

### Customization
- Modify chunking parameters in `src/benchmark_runner.py`
- Adjust quality metrics in `src/chunk_quality_comparison.py`
- Customize analysis parameters in `src/run_category_chunk_comparison.py`

## 📝 Development

### Adding New Features
1. **New chunking strategies**: Add to `src/benchmark_runner.py`
2. **New quality metrics**: Extend `src/chunk_quality_comparison.py`
3. **New analysis types**: Create new modules in `src/`
4. **New reports**: Add to `reports/` directory

### Code Organization
- **Source code**: All Python modules in `src/`
- **Reports**: All generated reports in `reports/`
- **Data**: All data files and visualizations in `data/`
- **Documents**: Test PDFs in `benchmarks/`

## 🎯 Key Achievements

- ✅ **Comprehensive benchmarking** across 4 document categories
- ✅ **Advanced hybrid chunking** with 5 strategies implemented
- ✅ **Quality analysis framework** with 11 metrics
- ✅ **Cross-tool comparison** (Unstructured vs Docling)
- ✅ **Category-based insights** and recommendations
- ✅ **12x performance improvement** with Docling
- ✅ **Superior quality** with Unstructured
- ✅ **Clean, organized codebase** with proper structure

## 📚 Documentation

- **README.md**: Comprehensive project overview and usage guide
- **PROJECT_STRUCTURE.md**: This file - project organization
- **Reports/**: Detailed analysis and implementation reports
- **Code comments**: Inline documentation in all source files

---

**Happy Benchmarking! 🚀** 
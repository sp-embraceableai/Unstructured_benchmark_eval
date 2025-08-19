# Unstructured Performance Benchmark Framework

A comprehensive benchmarking framework to evaluate **Unstructured** performance across different document types, with smart chunking strategies and detailed analysis. Focus on German PDFs with performance metrics and quality assessment.

## 🎯 Purpose

This framework provides comprehensive analysis of Unstructured document processing:

- **Performance Benchmarking:** Processing speed, element extraction, resource usage
- **Smart Chunking:** Markdown-aware text chunking with configurable word limits
- **Quality Analysis:** Readability, coherence, completeness, structural preservation
- **Category Analysis:** Performance across different document types

### Document Categories Analyzed:
- **Short text documents** (<5 pages, mostly text)
- **Long text documents** (>20 pages, mostly text)  
- **Table-heavy documents** (≥30% pages with structured tables)
- **Image-heavy documents** (many charts, scans, graphics)

## 📊 What We Measure

### Performance Metrics
- **Processing time** per document and per page
- **Elements processed per second** (text, tables, images)
- **Chunk generation** patterns and efficiency
- **GPU vs CPU performance** comparison
- **Memory usage** and resource utilization

### Quality Metrics
- **Readability scores** (word length, sentence structure)
- **Completeness assessment** (sentence endings)
- **Chunk size consistency** (variance analysis)
- **Structural preservation** (markdown pattern recognition)
- **Content analysis** (table and image extraction)

## 🏗️ Project Structure

```
Unstructured_benchmark_eval/
├── benchmarks/                    # Document categories
│   ├── short_text/               # <5 pages, mostly text
│   ├── long_text/                # >20 pages, mostly text
│   ├── table_heavy/              # ≥30% tables
│   └── image_heavy/              # Many charts/scans
├── src/                          # Source code
│   ├── unstructured_only_benchmark.py    # Main benchmarking script
│   ├── extract_chunks_unstructured.py    # Single document analysis
│   └── run_category_chunk_comparison.py  # Category-based analysis
├── data/                         # Output data
├── reports/                      # Generated reports
├── requirements_unstructured_only.txt    # Dependencies
├── main.py                       # Main entry point
└── README_UNSTRUCTURED_ONLY.md   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_unstructured_only.txt
```

### 2. Run Basic Benchmark

```bash
python main.py benchmark
```

### 3. Extract Chunks from Single Document

```bash
python main.py extract --file benchmarks/short_text/sample.pdf
```

### 4. Run Category-Based Analysis

```bash
python main.py category
```

### 5. Run All Analyses

```bash
python main.py all
```

## 🔧 Key Features

### Smart Chunking Implementation

**Markdown-aware text chunking** with intelligent strategy:

1. **Pattern Recognition:** Splits at headers, lists, and structural elements
2. **Word Limit Management:** Combines small chunks until reaching limit
3. **Multiple Strategies:** 250, 500, and 1000 word chunk sizes
4. **Quality Assessment:** Completeness, consistency, and readability metrics

### Performance Analysis

**Comprehensive benchmarking** across document types:
- **Processing speed** measurement
- **Element extraction** analysis
- **GPU utilization** detection
- **Memory usage** tracking
- **Error handling** and reporting

### Quality Assessment

**Multi-dimensional quality metrics:**
- **Chunk size analysis** (average, variance)
- **Completeness scoring** (sentence endings)
- **Readability metrics** (word length, structure)
- **Content preservation** (tables, images)

## 📋 Document Categories

### Short Text (<5 pages)
- **Bundesanzeiger Kurzbericht** (safety & clinical performance reports)
- **Bundesanzeiger Bekanntmachung** (official notices)
- **Regulatory summaries** and brief reports

### Long Text (>20 pages)
- **Statistisches Jahrbuch** (statistical yearbook chapters)
- **Statistische Bibliothek Reports** (multi-chapter monographs)
- **Sächsische Längsschnittstudie** (longitudinal studies)

### Table-Heavy (≥30% tables)
- **Baden-Württemberg Budget PDFs** (comprehensive budget documents)
- **Verbraucherpreisindex** (consumer price index with decades of data)
- **Bevölkerungsstand Tabellen** (demographic tables and time series)

### Image-Heavy (many charts/scans)
- **Destatis thematic PDFs** with demographic trend visuals
- **OpenGovData scan-based reports** (environmental impact PDFs)
- **Zensus 2022 reports** with images and graphics

## 📊 Scripts Overview

### `unstructured_only_benchmark.py`
The main benchmarking script with Unstructured-only features:
- **Unstructured processing** with hi_res strategy
- **Smart chunking** with markdown pattern recognition
- **Performance measurement** and error handling
- **Comprehensive logging** and result storage
- **Category-wise analysis** and reporting

**Key Features:**
- GPU detection and utilization
- Smart chunking strategies
- Detailed performance metrics
- Category-wise analysis
- Error handling and recovery

### `extract_chunks_unstructured.py`
Single document analysis and chunk extraction:
- **Element extraction** from PDFs
- **Multiple chunking strategies** comparison
- **Quality analysis** of chunks
- **Sample chunk display** for inspection
- **Table and image extraction** analysis

**Outputs:**
- Detailed chunk analysis
- Strategy comparison
- Sample chunk content
- Quality metrics

### `run_category_chunk_comparison.py`
Category-based analysis across multiple documents:
- **Multi-document processing** per category
- **Statistical aggregation** of results
- **Category-specific insights** and recommendations
- **Comprehensive reporting** with detailed tables
- **Performance patterns** by document type

## 📊 Expected Results

### Performance Patterns
- **Short documents**: Fast processing, few elements
- **Long documents**: Longer processing, many elements
- **Table-heavy**: Moderate processing, high table count
- **Image-heavy**: Variable processing, image descriptions

### Quality Insights
- **Smart chunking**: Better structure preservation
- **Large chunks**: Higher completeness, lower granularity
- **Small chunks**: Lower completeness, higher granularity
- **Table extraction**: Structured data preservation

### GPU Benefits
- **Structural chunking**: Significant speedup with GPU
- **Image processing**: Major improvements for image-heavy docs
- **Table extraction**: Moderate GPU benefits
- **Text processing**: Minimal GPU impact

## 🎛️ Configuration

### Environment Variables
```bash
export UNSTRUCTURED_HIDE_PROGRESS_BAR=false  # Show progress
export UNSTRUCTURED_GPU_ENABLED=true         # Enable GPU
```

### Chunking Configuration
```python
# Smart chunking parameters
max_words_per_chunk = 500
markdown_patterns = [
    r'^#{1,6}\s+',  # Headers
    r'^\*\s+',      # Bullet points
    r'^\d+\.\s+',   # Numbered lists
    r'^\n+',        # Multiple newlines
    r'^---\s*$',    # Horizontal rules
    r'^```',        # Code blocks
]

# Chunking strategies
small_chunk_size = 250
medium_chunk_size = 500
large_chunk_size = 1000
```

## 📊 Output Files

After running the benchmarks, you'll get:

### Performance Reports
- `data/unstructured_benchmark_results.json` - Raw benchmark data
- `reports/unstructured_benchmark_report.md` - Detailed analysis
- `benchmark.log` - Processing logs

### Analysis Reports
- Category-based analysis reports
- Chunk quality assessments
- Performance comparisons

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements_unstructured_only.txt
   ```

2. **GPU Issues**
   - Check CUDA installation
   - Verify torch GPU support
   - Monitor memory usage

3. **Performance Issues**
   - Monitor memory usage for large documents
   - Use appropriate chunk sizes for your use case
   - Consider GPU acceleration for large datasets

### Performance Tips

1. **For Quality-Critical Applications**
   - Use smart chunking with 500-word limit
   - Enable hi_res strategy for better table detection
   - Monitor chunk quality metrics

2. **For Speed-Critical Applications**
   - Use fast strategy for initial processing
   - Implement larger chunk sizes
   - Consider batch processing

3. **For Balanced Requirements**
   - Use hi_res strategy with smart chunking
   - Monitor both performance and quality metrics
   - Adjust chunk sizes based on document type

## 📚 Resources

- [Unstructured Documentation](https://unstructured-io.github.io/unstructured/)
- [Unstructured GitHub Repository](https://github.com/Unstructured-IO/unstructured)
- [German Statistical Office](https://www.destatis.de)
- [Bundesanzeiger](https://www.bundesanzeiger.de)

## 📄 License

This project is open source. Feel free to use and modify for your benchmarking needs.

---

**Key Achievements:**
- ✅ **Comprehensive benchmarking** across 4 document categories
- ✅ **Smart chunking** with markdown pattern recognition
- ✅ **Quality analysis framework** with multiple metrics
- ✅ **Performance optimization** with GPU support
- ✅ **Category-based insights** and recommendations
- ✅ **Detailed reporting** and analysis

**Happy Benchmarking! 🚀** 
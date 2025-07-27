# Unstructured vs Docling Performance Benchmark Framework

A comprehensive benchmarking framework to evaluate **Unstructured** and **Docling** performance across different document types, with advanced chunking strategies and quality analysis. Focus on German PDFs with detailed performance and quality comparisons.

## 🎯 Purpose

This framework provides comprehensive analysis of document processing performance and chunk quality:

- **Performance Benchmarking:** Processing speed, element extraction, resource usage
- **Chunk Quality Analysis:** Readability, coherence, completeness, structural preservation
- **Hybrid Chunking Strategies:** Advanced chunking methods with adaptive selection
- **Cross-Tool Comparison:** Unstructured vs Docling performance and quality analysis

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
- **Cross-tool performance** comparison (Unstructured vs Docling)

### Quality Metrics
- **Readability scores** (Flesch Reading Ease)
- **Coherence analysis** (semantic flow between chunks)
- **Completeness assessment** (sentence and content completeness)
- **Information density** (unique content per word)
- **Structural preservation** (document formatting retention)
- **Language quality** (grammar, punctuation, capitalization)
- **Semantic continuity** (topic flow and transitions)
- **Content overlap** (similarity between different chunking methods)

## 🏗️ Project Structure

```
Unstructured_benchmark_eval/
├── benchmarks/                    # Document categories
│   ├── short_text/               # <5 pages, mostly text
│   ├── long_text/                # >20 pages, mostly text
│   ├── table_heavy/              # ≥30% tables
│   └── image_heavy/              # Many charts/scans
├── benchmark_runner.py           # Main benchmarking script with hybrid chunking
├── chunk_quality_comparison.py   # Comprehensive quality analysis
├── run_category_chunk_comparison.py # Category-based analysis
├── test_advanced_docling.py      # Advanced Docling testing
├── requirements.txt              # Python dependencies
├── benchmark_results.json        # Raw benchmark data
├── comprehensive_benchmark_report.md # Detailed Unstructured analysis
├── chunk_quality_comparison_report.md # Quality comparison results
├── category_chunk_quality_report.md # Category-based analysis
├── hybrid_chunking_success_report.md # Hybrid chunking implementation
├── hybrid_chunking_methods.md    # Chunking strategies documentation
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Basic Benchmark (Unstructured Only)

```bash
python benchmark_runner.py
```

### 3. Run Chunk Quality Comparison

```bash
python chunk_quality_comparison.py
```

### 4. Run Category-Based Analysis

```bash
python run_category_chunk_comparison.py
```

### 5. Test Advanced Docling Features

```bash
python test_advanced_docling.py
```

## 📈 Key Results & Insights

### 🏆 Overall Performance Comparison

| Metric | Unstructured | Docling | Winner |
|--------|--------------|---------|--------|
| **Processing Speed** | 15.014s | 1.237s | Docling (12x faster) |
| **Chunk Quality** | 5/7 metrics | 1/7 metrics | Unstructured |
| **Readability** | 35.8 | 26.4 | Unstructured |
| **Coherence** | 1.000 | 0.254 | Unstructured |
| **Information Density** | 0.371 | 0.307 | Unstructured |
| **Structural Preservation** | 1.000 | 0.750 | Unstructured |
| **Language Quality** | 0.551 | 0.554 | Docling |

### 📊 Category-Based Analysis Results

**Total Documents Analyzed:** 7 PDFs across 4 categories

| Category | Documents | Unstructured Wins | Docling Wins | Content Overlap | Chunk Ratio |
|----------|-----------|-------------------|--------------|-----------------|-------------|
| **Short Text** | 2 | 1 | 1 | 0.77 | 3.50x |
| **Long Text** | 1 | 1 | 0 | 0.96 | 48.00x |
| **Table Heavy** | 3 | 3 | 0 | 0.47 | 105.00x |
| **Image Heavy** | 1 | 1 | 0 | 0.80 | 47.00x |

**Overall Winner:** Unstructured (6 wins vs 1 win)

## 🔧 Advanced Features

### Hybrid Chunking Implementation

Successfully implemented **5 advanced chunking strategies**:

1. **Semantic Chunking** (1000 tokens) - Content-aware chunking
2. **Recursive Character** (500 tokens) - Hierarchical text splitting  
3. **Markdown Header** (1000 tokens) - Header-preserving chunking
4. **Hybrid semchunk** (800 tokens) - Balanced approach
5. **Default semchunk** (1000 tokens) - Standard chunking

### Adaptive Strategy Selection

**Automatic document analysis** with intelligent strategy selection:
- **Long + Headers:** 1200 token chunks
- **Table-Heavy:** 800 token chunks  
- **List-Heavy:** 600 token chunks
- **General:** 1000 token chunks

### Quality Assessment Framework

**11 comprehensive quality metrics:**
- Readability (Flesch Reading Ease)
- Coherence (semantic flow)
- Completeness (content integrity)
- Information density (unique content)
- Structural preservation (formatting)
- Language quality (grammar, punctuation)
- Semantic continuity (topic flow)
- Content overlap (cross-method similarity)
- Chunk size distribution
- Size consistency
- Error rates

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

## 🔍 Scripts Overview

### `benchmark_runner.py`
The main benchmarking script with advanced features:
- **Unstructured processing** with hi_res strategy
- **Advanced Docling chunking** with 5 strategies
- **Smart chunking** for Unstructured (markdown-based)
- **Hybrid chunking** with adaptive strategy selection
- **Performance measurement** and error handling
- **Comprehensive logging** and result storage

**Key Features:**
- GPU detection and utilization
- Advanced chunking strategies
- Cross-tool comparison
- Detailed performance metrics
- Category-wise analysis

### `chunk_quality_comparison.py`
Comprehensive quality analysis framework:
- **11 quality metrics** across multiple dimensions
- **Cross-tool comparison** (Unstructured vs Docling)
- **Statistical analysis** with detailed reporting
- **Sample chunk comparison** with qualitative assessment
- **Automated winner determination** for each metric

**Outputs:**
- Detailed quality comparison report
- Statistical analysis with ratios
- Sample chunk content comparison
- Quality assessment with recommendations

### `run_category_chunk_comparison.py`
Category-based analysis across multiple documents:
- **Multi-document processing** per category
- **Statistical aggregation** of results
- **Category-specific insights** and recommendations
- **Comprehensive reporting** with detailed tables
- **Performance patterns** by document type

### `test_advanced_docling.py`
Advanced Docling feature testing:
- **Hybrid chunking strategies** validation
- **Adaptive strategy selection** testing
- **Performance comparison** with Unstructured
- **Error handling** and debugging
- **Feature validation** and testing

## 📊 Detailed Results

### Performance Analysis

#### Unstructured Performance
```
📁 SHORT TEXT (2 documents)
   Success Rate: 100.0%
   Avg Processing Time: 15.014s
   Avg Elements: 96
   - Text: 55
   - Tables: 3
   - Images: 0
   Chunk Count: 1-2
   Avg Chunk Size: 948 words

📁 LONG TEXT (1 document)
   Success Rate: 100.0%
   Processing Time: 15.234s
   Elements: 892
   Chunk Count: 1
   Chunk Size: Large single chunk
```

#### Docling Performance
```
📁 SHORT TEXT (2 documents)
   Success Rate: 100.0%
   Avg Processing Time: 1.237s
   Avg Elements: 2-5
   Chunk Count: 2-5
   Avg Chunk Size: 908 words
   Speed Improvement: 12x faster

📁 LONG TEXT (1 document)
   Success Rate: 100.0%
   Processing Time: 1.456s
   Elements: 48
   Chunk Count: 48
   Chunk Size: Small granular chunks
```

### Quality Analysis Results

#### Unstructured Strengths
- **Superior Coherence (1.000):** Perfect semantic flow
- **Better Readability (35.8):** More readable text chunks
- **Higher Information Density (0.371):** More unique content per word
- **Perfect Structural Preservation (1.000):** Maintains document formatting
- **Excellent Semantic Continuity (1.000):** Smooth topic transitions

#### Docling Strengths
- **12x Faster Processing:** Significant speed advantage
- **Better Language Quality (0.554):** Slightly better grammar
- **Multiple Chunks:** More granular content division
- **Consistent Chunk Sizes:** Predictable chunk distribution

## 🎯 Recommendations by Use Case

### For Human-Consumable Content
- **Recommendation:** Use Unstructured
- **Reason:** Superior readability, coherence, and structure preservation
- **Best for:** Reports, documentation, content for end users

### For Machine Learning/AI Processing
- **Recommendation:** Use Docling with post-processing
- **Reason:** Faster processing, granular data, but needs cleaning
- **Best for:** NLP tasks, text analysis, data extraction

### For Hybrid Approach
- **Recommendation:** Combine both methods
- **Strategy:** Use Docling for speed, Unstructured for quality validation
- **Best for:** Large-scale processing with quality requirements

### Category-Specific Recommendations

| Category | Recommendation | Reason |
|----------|----------------|---------|
| **Short Text** | Both methods similar | Consider speed vs quality trade-off |
| **Long Text** | Use Unstructured | Superior quality for large documents |
| **Table Heavy** | Use Unstructured | Better structure preservation |
| **Image Heavy** | Use Unstructured | Better mixed content handling |

## 📈 Expected Insights

### Performance Patterns
- **Short documents**: Docling 12x faster, similar quality
- **Long documents**: Unstructured better quality, Docling faster
- **Table-heavy**: Unstructured superior structure preservation
- **Image-heavy**: Unstructured better mixed content handling

### Quality vs Speed Trade-offs
- **Unstructured**: Superior quality but slower processing
- **Docling**: 12x faster but lower quality chunks
- **Content overlap**: 47-96% depending on document type
- **Chunk granularity**: Docling produces 3.5x to 105x more chunks

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

### Advanced Chunking Configuration
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

# Hybrid chunking strategies
semantic_chunk_size = 1000
recursive_chunk_size = 500
markdown_chunk_size = 1000
hybrid_chunk_size = 800
```

## 📊 Output Files

After running the benchmarks, you'll get:

### Performance Reports
- `benchmark_results.json` - Raw benchmark data
- `comprehensive_benchmark_report.md` - Detailed Unstructured analysis
- `advanced_analysis_report.md` - Statistical analysis

### Quality Analysis Reports
- `chunk_quality_comparison_report.md` - Detailed quality comparison
- `category_chunk_quality_report.md` - Category-based analysis
- `chunk_quality_comparison_summary.md` - Executive summary

### Implementation Reports
- `hybrid_chunking_success_report.md` - Hybrid chunking implementation
- `hybrid_chunking_methods.md` - Chunking strategies documentation

### Test Results
- `test_advanced_docling.py` output - Advanced Docling testing
- Processing logs and error reports

## 🛠️ Troubleshooting

### Common Issues

1. **Docling Import Errors**
   ```bash
   pip install docling-parse
   pip install 'numpy<2'  # Fix compatibility issues
   ```

2. **Hybrid Chunking Errors**
   - Ensure semchunk package is installed
   - Check token counter function implementation
   - Verify document loading with docling-parse

3. **Quality Analysis Errors**
   - Check division by zero in ratio calculations
   - Ensure proper error handling for empty chunks
   - Verify metric calculation functions

4. **Performance Issues**
   - Monitor memory usage for large documents
   - Use appropriate chunk sizes for your use case
   - Consider GPU acceleration for large datasets

### Performance Tips

1. **For Quality-Critical Applications**
   - Use Unstructured with smart chunking
   - Enable hi_res strategy for better table detection
   - Monitor chunk quality metrics

2. **For Speed-Critical Applications**
   - Use Docling with post-processing
   - Implement custom chunking strategies
   - Consider batch processing

3. **For Balanced Requirements**
   - Use hybrid approach combining both tools
   - Implement quality validation with Unstructured
   - Use Docling for initial processing

## 🤝 Contributing

To add new features or improve the framework:

1. **Add New Chunking Strategies**
   - Implement new chunking algorithms
   - Add to adaptive strategy selection
   - Update quality assessment metrics

2. **Extend Quality Analysis**
   - Add new quality metrics
   - Implement domain-specific assessments
   - Enhance statistical analysis

3. **Improve Performance**
   - Optimize processing pipelines
   - Add GPU acceleration options
   - Implement caching strategies

## 📚 Resources

- [Unstructured Documentation](https://unstructured-io.github.io/unstructured/)
- [Docling GitHub Repository](https://github.com/docling-project/docling)
- [semchunk Package](https://github.com/contextual-ai/semchunk)
- [German Statistical Office](https://www.destatis.de)
- [Bundesanzeiger](https://www.bundesanzeiger.de)

## 📄 License

This project is open source. Feel free to use and modify for your benchmarking needs.

---

**Key Achievements:**
- ✅ **Comprehensive benchmarking** across 4 document categories
- ✅ **Advanced hybrid chunking** with 5 strategies implemented
- ✅ **Quality analysis framework** with 11 metrics
- ✅ **Cross-tool comparison** (Unstructured vs Docling)
- ✅ **Category-based insights** and recommendations
- ✅ **12x performance improvement** with Docling
- ✅ **Superior quality** with Unstructured

**Happy Benchmarking! 🚀**

# Unstructured Performance Benchmark Framework

A comprehensive benchmarking framework to evaluate Unstructured's performance across different document types, with a focus on German PDFs.

## 🎯 Purpose

This framework helps you understand how Unstructured performs on different types of documents:

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

### Document Analysis
- **Element extraction** accuracy and completeness
- **Table structure** preservation
- **Image description** quality and detail
- **Text chunking** effectiveness
- **Error rates** by document type

## 🏗️ Project Structure

```
Unstructured_benchmark_eval/
├── benchmarks/                    # Document categories
│   ├── short_text/               # <5 pages, mostly text
│   ├── long_text/                # >20 pages, mostly text
│   ├── table_heavy/              # ≥30% tables
│   └── image_heavy/              # Many charts/scans
├── benchmark_runner.py           # Main benchmarking script
├── advanced_analyzer.py          # Detailed analysis and visualization
├── download_organizer.py         # PDF download and organization
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Document Structure

```bash
python download_organizer.py --create-folders
```

### 3. Download German PDFs

```bash
# Generate download guide
python download_organizer.py --guide

# Try automatic download (may need manual intervention)
python download_organizer.py --download

# Verify what's downloaded
python download_organizer.py --verify
```

### 4. Run Benchmarks

```bash
python benchmark_runner.py
```

### 5. Analyze Results

```bash
python advanced_analyzer.py
```

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
- **Verbraucherpreisindex** (consumer price index with decades of data)
- **Bevölkerungsstand Tabellen** (demographic tables and time series)
- **Statistical yearbook data chapters** (population, prices, etc.)

### Image-Heavy (many charts/scans)
- **Destatis thematic PDFs** with demographic trend visuals
- **OpenGovData scan-based reports** (environmental impact PDFs)
- **Zensus 2022 reports** with images and graphics

## 📝 Qualitative Chunk Analysis: Table-Heavy PDFs

### Sample: `bw_budget_15_14_Epl.pdf`

- **Total elements extracted:** 101,004
- **First 10 chunks:**
  1. Title: Staatshaushaltsplan
  2. Text: für 2025/2026
  3. Title: Einzelplan 14
  4. Title: Ministerium für Wissenschaft, Forschung und Kunst
  5. NarrativeText: Für den Druck wurde klimaneutral produziertes, weißes Papier verwendet
  6. Title: Inhalt
  7. Title: Betragsteil Seite
  8. Title: Inhalt
  9. Text: Vorwort ....................................................................................................
  10. Text: 4

#### **Qualitative Observations**
- **No Table Elements:** All chunks are of type `Title`, `Text`, or `NarrativeText`. No `Table` elements detected.
- **Chunk Content:** Mostly headings, section titles, and introductory text. Some lines show dotted formatting, likely from a table of contents or tabular layout rendered as plain text.
- **No Tabular Structure:** No evidence of preserved table structure (no rows/columns, delimiters, or tabular formatting).
- **Flattened Tables:** If tables exist, they are being flattened into plain text or not detected as tables at all.

#### **Conclusion**
- Unstructured is not recognizing tables as structured elements in this document. All content is chunked as text or titles.
- Tables are likely being flattened into lines of text, losing their row/column structure.
- No evidence of table-specific chunking in the output.

#### **Next Steps**
- Try with a PDF known to have machine-readable tables (not scanned or image-based).
- Experiment with Unstructured's table extraction settings or alternative tools for table detection.
- Consider extracting and analyzing random chunks from deeper in the document or from other PDFs for comparison.

## 🔧 Scripts Overview

### `benchmark_runner.py`
The main benchmarking script that:
- Processes each PDF with Unstructured
- Measures processing time and performance
- Analyzes extracted elements (text, tables, images)
- Generates chunk statistics
- Saves results to JSON format

**Key Features:**
- GPU detection and utilization
- Error handling and logging
- Detailed performance metrics
- Category-wise analysis

### `advanced_analyzer.py`
Advanced analysis and visualization:
- Statistical analysis of results
- GPU vs CPU performance comparison
- Interactive visualizations (Plotly)
- Comprehensive markdown reports
- Correlation analysis between document characteristics and performance

**Outputs:**
- Performance overview plots
- Interactive dashboard (HTML)
- Statistical analysis report
- Key insights and recommendations

### `download_organizer.py`
PDF organization and download utilities:
- Creates folder structure
- Downloads PDFs from German sources
- Generates download guides
- Verifies downloaded files

**Usage:**
```bash
python download_organizer.py --create-folders  # Create folders
python download_organizer.py --download        # Download PDFs
python download_organizer.py --verify          # Check downloads
python download_organizer.py --guide           # Generate guide
```

## 📈 Expected Insights

### Performance Patterns
- **Short documents**: Fastest processing, high elements/second
- **Long documents**: Linear scaling with page count
- **Table-heavy**: Moderate slowdown due to table extraction
- **Image-heavy**: Slowest due to image processing and description

### GPU Benefits
- **Structural chunking**: Significant speedup with GPU
- **Image processing**: Major improvements for image-heavy docs
- **Table extraction**: Moderate GPU benefits
- **Text processing**: Minimal GPU impact

### Chunk Analysis
- **Short docs**: Fewer, larger chunks
- **Long docs**: More chunks, consistent size
- **Table docs**: Chunks around table boundaries
- **Image docs**: Chunks with image descriptions

## 🎛️ Configuration

### Environment Variables
```bash
export UNSTRUCTURED_HIDE_PROGRESS_BAR=false  # Show progress
export UNSTRUCTURED_GPU_ENABLED=true         # Enable GPU
```

### Customization
- Modify `document_mappings` in `download_organizer.py` to add your own PDFs
- Adjust performance metrics in `benchmark_runner.py`
- Customize visualizations in `advanced_analyzer.py`

## 📊 Output Files

After running the benchmarks, you'll get:

- `benchmark_results.json` - Raw benchmark data
- `benchmark.log` - Processing logs
- `analysis_plots/` - Visualization directory
  - `performance_overview.png` - Main performance charts
  - `element_distribution.png` - Element type analysis
  - `interactive_dashboard.html` - Interactive Plotly dashboard
- `advanced_analysis_report.md` - Comprehensive analysis report

## 🔍 Sample Results

### Performance Summary
```
📁 SHORT TEXT
   Documents: 3
   Success Rate: 100.0%
   Avg Processing Time: 2.345s
   Avg Time per Page: 0.587s
   Avg File Size: 0.85MB
   Total Elements: 156
   - Text: 142
   - Tables: 8
   - Images: 6

📁 LONG TEXT
   Documents: 3
   Success Rate: 100.0%
   Avg Processing Time: 15.234s
   Avg Time per Page: 0.609s
   Avg File Size: 8.45MB
   Total Elements: 892
   - Text: 823
   - Tables: 45
   - Images: 24
```

### GPU vs CPU Comparison
```
Processing Time:
- GPU Mean: 8.234s
- CPU Mean: 12.456s
- Speedup Factor: 1.51x
- Improvement: 33.9%
```

## 🛠️ Troubleshooting

### Common Issues

1. **PDF Download Failures**
   - URLs may be placeholders - check `download_guide.md`
   - Some sites require registration
   - Try manual download from source websites

2. **GPU Not Detected**
   - Install PyTorch with CUDA support
   - Check `nvidia-smi` for GPU availability
   - Set `UNSTRUCTURED_GPU_ENABLED=true`

3. **Memory Issues**
   - Process documents one at a time
   - Reduce batch sizes in Unstructured
   - Monitor system memory usage

4. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Install system dependencies (poppler, tesseract)
   - Check Unstructured installation guide

### Performance Tips

1. **For Large Document Sets**
   - Process in batches
   - Use SSD storage for faster I/O
   - Monitor system resources

2. **For GPU Optimization**
   - Ensure CUDA drivers are up to date
   - Use appropriate batch sizes
   - Monitor GPU memory usage

3. **For Accurate Results**
   - Run multiple times for consistency
   - Clear cache between runs
   - Use consistent hardware configuration

## 🤝 Contributing

To add new document types or improve the framework:

1. **Add New Categories**
   - Update `document_mappings` in `download_organizer.py`
   - Add category to benchmark scripts
   - Update analysis functions

2. **Improve Metrics**
   - Add new performance measurements
   - Enhance visualization options
   - Improve statistical analysis

3. **Extend Analysis**
   - Add more document sources
   - Include different languages
   - Add quality assessment metrics

## 📚 Resources

- [Unstructured Documentation](https://unstructured-io.github.io/unstructured/)
- [German Statistical Office](https://www.destatis.de)
- [Bundesanzeiger](https://www.bundesanzeiger.de)
- [OpenGovData](https://opengovdata.de)

## 📄 License

This project is open source. Feel free to use and modify for your benchmarking needs.

---

**Happy Benchmarking! 🚀**

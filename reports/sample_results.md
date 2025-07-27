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

## 🚨 CRITICAL FINDINGS & LIMITATIONS

### **Issue 1: Page Counting Problem**
**Problem**: All documents show `page_count: 1`, which is likely incorrect for multi-page budget documents.

**Evidence**:
- Budget PDFs ranging from 0.23MB to 64MB all show single page
- Processing times vary dramatically (0.9s to 77s) suggesting different page counts
- File size vs processing time correlation suggests multi-page documents

**Impact**: Cannot properly analyze "How does the length of the document affect performance?"

### **Issue 2: Table Detection Failure**
**Problem**: All documents show `table_elements: 0`, even budget documents that should contain tables.

**Evidence**:
- 18 "table_heavy" budget documents all show 0 table elements
- Budget documents contain financial data that should have tabular structures
- Only text elements are being detected

**Impact**: Cannot answer "How do tables affect performance?"

**Possible Causes**:
1. Budget PDFs have tables as images rather than structured data
2. Tables are converted to text during PDF creation
3. Unstructured's table detection needs different parameters
4. Table detection requires specific configuration

### **Issue 3: Limited Document Type Coverage**
**Problem**: Missing long_text and image_heavy document categories.

**Evidence**:
- Only short_text (2 docs) and table_heavy (18 docs) categories populated
- No documents with >20 pages of narrative text
- No documents with many charts, scans, or graphics

**Impact**: Incomplete performance analysis across document types.

## 📊 What the Report DOES Answer Well

### **✅ File Size vs Performance Correlation**
- **Linear scaling**: Processing time correlates strongly with file size
- **Range tested**: 0.27MB to 64MB (237x difference)
- **Processing time range**: 0.9s to 77s (85x difference)

### **✅ Element Extraction Efficiency**
- **Short docs**: 76 elements/second
- **Table-heavy docs**: 1,535 elements/second (20x more efficient)
- **Element density**: Complex documents have much higher element counts

### **✅ Chunk Generation Patterns**
- **Short docs**: Fewer, larger chunks (199 characters average)
- **Table-heavy docs**: Many small chunks (22 characters average)
- **Chunk optimization**: Different strategies for different document types

## 🔧 Recommendations to Fix Issues

### **For Document Length Analysis:**
1. **Fix page counting method** in `benchmark_runner.py`
2. **Add true long documents** (>20 pages of narrative text)
3. **Implement page-by-page processing** measurement
4. **Test with known multi-page documents**

### **For Table Analysis:**
1. **Investigate table detection settings** in Unstructured
2. **Test with simple table-heavy PDFs** (e.g., CSV-like data)
3. **Try different Unstructured parameters** for table extraction
4. **Verify table structure** in source PDFs

### **For Complete Coverage:**
1. **Add long_text documents** from German government reports
2. **Add image_heavy documents** with charts and graphics
3. **Test GPU vs CPU performance** if GPU available
4. **Include more diverse document sources**

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

---

**Note**: This benchmark provides valuable insights into file size vs. performance relationships, but cannot fully answer questions about document length and table effects due to the technical limitations identified above. 
# Unstructured Performance Analysis Report

Generated on: 2025-07-23 02:22:16
Total documents analyzed: 20
GPU available: False

## Performance by Document Category

```
              processing_time_seconds                              time_per_page                              elements_per_second                                    chunks_per_second                                    avg_chunk_size                               file_size_mb                           
                                 mean     std    min     max count          mean     std    min     max count                mean      std       min       max count              mean      std       min       max count           mean     std     min     max count         mean     std   min    max count
document_type                                                                                                                                                                                                                                                                                                 
short_text                      2.098   1.320  1.165   3.032     2         2.098   1.320  1.165   3.032     2              76.050   66.039    29.354   122.747     2            76.050   66.039    29.354   122.747     2        199.150  66.454  152.16  246.14     2        0.425   0.219  0.27   0.58     2
table_heavy                    17.310  19.948  0.499  77.118    18        17.310  19.948  0.499  77.118    18            1535.295  232.234  1041.869  1959.385    18          1535.295  232.234  1041.869  1959.385    18         22.432   5.574   14.66   40.42    18        5.799  14.622  0.23  64.00    18
```

## GPU vs CPU Performance Comparison

*No GPU/CPU comparison possible - missing data*

## Image-Heavy Document Analysis

*No image-heavy documents found*

## Table-Heavy Document Analysis

*No table-heavy documents found*

## Chunk Generation Analysis

- Total chunks generated: 430376
- Average chunks per document: 21518.80
- Average chunk size: 40 characters

## Key Insights

- **Fastest document type**: short_text
- **Slowest document type**: table_heavy
- **Most efficient (elements/second)**: table_heavy
- **Most chunks generated**: table_heavy

## 🚨 CRITICAL FINDINGS & LIMITATIONS

### **Issue 1: Page Counting Problem**
**Problem**: All documents show `page_count: 1`, which is likely incorrect for multi-page budget documents.

**Evidence**:
- Budget PDFs ranging from 0.23MB to 64MB all show single page
- Processing times vary dramatically (0.9s to 77s) suggesting different page counts
- File size vs processing time correlation suggests multi-page documents

**Impact**: Cannot properly analyze "How does the length of the document affect performance?"

**Root Cause**: Likely an issue with the PDF page counting method in `benchmark_runner.py`

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

## 📈 Current Performance Insights (Despite Limitations)

### **Document Complexity Impact**
- **Processing time scales with file size**: 0.27MB → 3s vs 64MB → 77s
- **Element extraction efficiency**: Table-heavy docs are 20x more efficient per element
- **Memory usage**: Larger documents require significantly more processing time

### **Production Recommendations**
- **Short documents**: Expect ~2 seconds processing time
- **Complex documents**: Expect 15-80 seconds depending on size
- **Resource planning**: Large documents require significant processing time
- **Batch processing**: Consider parallel processing for large document sets

## 🎯 Next Steps for Complete Analysis

1. **Fix technical issues** (page counting, table detection)
2. **Expand document dataset** with all four categories
3. **Test GPU performance** if available
4. **Re-run comprehensive benchmarks** with corrected methodology
5. **Validate findings** with known document characteristics

---

**Note**: This report provides valuable insights into file size vs. performance relationships, but cannot fully answer questions about document length and table effects due to the technical limitations identified above.

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
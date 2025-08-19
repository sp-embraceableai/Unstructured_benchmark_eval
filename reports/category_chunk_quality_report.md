# Category-Based Chunk Quality Comparison Report

**Analysis Date:** 1753616645.6083786

## 📊 Overall Summary

- **Total Documents Analyzed:** 7
- **Total Unstructured Wins:** 6
- **Total Docling Wins:** 1
- **Total Ties:** 0
- **Overall Winner:** Unstructured

## 📈 Category-by-Category Analysis

### Short Text

- **Documents Processed:** 2
- **Unstructured Wins:** 1
- **Docling Wins:** 1
- **Ties:** 0
- **Category Winner:** Tie
- **Avg Content Overlap:** 0.77
- **Avg Chunk Count Ratio:** 3.50
- **Avg Readability Ratio:** 1.11
- **Avg Coherence Ratio:** 0.19
- **Avg Completeness Ratio:** 1.07

### Long Text

- **Documents Processed:** 1
- **Unstructured Wins:** 1
- **Docling Wins:** 0
- **Ties:** 0
- **Category Winner:** Unstructured
- **Avg Content Overlap:** 0.96
- **Avg Chunk Count Ratio:** 48.00
- **Avg Readability Ratio:** 0.98
- **Avg Coherence Ratio:** 0.17
- **Avg Completeness Ratio:** 0.97

### Table Heavy

- **Documents Processed:** 3
- **Unstructured Wins:** 3
- **Docling Wins:** 0
- **Ties:** 0
- **Category Winner:** Unstructured
- **Avg Content Overlap:** 0.47
- **Avg Chunk Count Ratio:** 105.00
- **Avg Readability Ratio:** 1.10
- **Avg Coherence Ratio:** 0.19
- **Avg Completeness Ratio:** 0.95

### Image Heavy

- **Documents Processed:** 1
- **Unstructured Wins:** 1
- **Docling Wins:** 0
- **Ties:** 0
- **Category Winner:** Unstructured
- **Avg Content Overlap:** 0.80
- **Avg Chunk Count Ratio:** 47.00
- **Avg Readability Ratio:** 0.93
- **Avg Coherence Ratio:** 0.17
- **Avg Completeness Ratio:** 0.97

## 📋 Detailed Results

| Category | Document | File Size (MB) | U Chunks | D Chunks | Content Overlap | Winner |
|----------|----------|----------------|----------|----------|-----------------|--------|
| short_text | BAnz AT 27.05.2022 B4.pdf | 0.27 | 1 | 2 | 0.59 | Unstructured |
| short_text | BAnz AT 02.04.2024 B3.pdf | 0.58 | 1 | 5 | 0.96 | Docling |
| long_text | 20006.pdf | 0.63 | 1 | 48 | 0.96 | Unstructured |
| table_heavy | bw_budget_10_09_Epl.pdf | 2.73 | 1 | 75 | 0.46 | Unstructured |
| table_heavy | bw_budget_09_08_Epl.pdf | 3.92 | 1 | 97 | 0.48 | Unstructured |
| table_heavy | bw_budget_01_Vorheft_Verabschiedet_web.pdf | 3.11 | 1 | 143 | 0.46 | Unstructured |
| image_heavy | 07_2025_cc.pdf | 2.87 | 1 | 47 | 0.80 | Unstructured |

## 🎯 Key Insights

- **Best Category for Unstructured:** table_heavy
- **Best Category for Docling:** short_text
- **Most Content Overlap:** long_text
- **Most Variable Chunking:** table_heavy

## 🚀 Recommendations by Category

### Short Text:
- **Recommendation:** Both methods perform similarly
- **Reason:** Consider speed vs quality trade-off
- **Content Overlap:** 0.77 (similar content extraction)
- **Chunk Granularity:** 3.50x more chunks with Docling

### Long Text:
- **Recommendation:** Use Unstructured for better quality
- **Reason:** Superior performance across quality metrics
- **Content Overlap:** 0.96 (similar content extraction)
- **Chunk Granularity:** 48.00x more chunks with Docling

### Table Heavy:
- **Recommendation:** Use Unstructured for better quality
- **Reason:** Superior performance across quality metrics
- **Content Overlap:** 0.47 (similar content extraction)
- **Chunk Granularity:** 105.00x more chunks with Docling

### Image Heavy:
- **Recommendation:** Use Unstructured for better quality
- **Reason:** Superior performance across quality metrics
- **Content Overlap:** 0.80 (similar content extraction)
- **Chunk Granularity:** 47.00x more chunks with Docling

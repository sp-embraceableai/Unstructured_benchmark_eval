# 🚀 **Unstructured Benchmark Evaluation + OmniDocBench Integration**

<div align="center">

![Image](https://github.com/user-attachments/assets/22a10ec4-c993-471f-9c9f-7a6c4d2e3df8)

<h1 align="center">
Unstructured Benchmark Evaluation + OmniDocBench
</h1>

**Comprehensive Document Parsing Benchmark & Pipeline Evaluation Framework**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

</div>

---

## 📋 **Project Overview**

This repository combines **two powerful document parsing evaluation frameworks**:

1. **🔍 Unstructured Benchmark Evaluation** - Comprehensive benchmarking of the Unstructured library
2. **📊 OmniDocBench Integration** - Advanced document parsing pipeline evaluation

### **🎯 What We've Built**

- **6 Different Pipeline Implementations** for document parsing
- **Comprehensive Performance Analysis** across multiple approaches
- **Advanced Table Recognition** with RapidTable integration
- **Multi-OCR Strategy** with fallback mechanisms
- **Detailed Quality Metrics** and comparison reports

---

## 🏆 **Pipeline Implementations**

### **Pipeline 1: Unstructured Library (Baseline)**
- **Purpose**: Simple, reliable text extraction
- **Best For**: Text-heavy documents, minimal setup
- **Performance**: 50% overall score, excellent text quality

### **Pipeline 2: Original OmniParse**
- **Purpose**: Specialized table structure detection
- **Best For**: Table-heavy documents, academic papers
- **Performance**: 80% overall score, excellent table structure

### **Pipeline 3: Enhanced OmniParse + RapidTable**
- **Purpose**: Advanced table recognition with RapidTable
- **Best For**: Complex table analysis, structure-focused applications
- **Performance**: 80% overall score, best table detection

### **Pipeline 4: Enhanced OCR Integration**
- **Purpose**: OCR-enhanced content extraction
- **Best For**: Mixed content documents, better text quality
- **Performance**: 80% overall score, improved content extraction

### **Pipeline 5: Multi-OCR Strategy**
- **Purpose**: Robust OCR with fallback mechanisms
- **Best For**: Challenging documents, maximum reliability
- **Performance**: 80% overall score, robust processing

### **🥇 Pipeline 6: FINAL OPTIMIZED**
- **Purpose**: Maximum quality and production use
- **Best For**: Production systems, highest quality requirements
- **Performance**: **90% overall score**, breakthrough improvements

---

## 📊 **Performance Breakthroughs**

### **🚀 Table Content Extraction: 5x Improvement!**
- **Before**: ~20% content recognition
- **After**: **72.5% EN, 73.3% CH** content recognition

### **✅ Text Recognition: 6-11x Improvement!**
- **Before**: 14.4% EN, 8.5% CH
- **After**: **94.7% EN, 99.1% CH**

### **🎯 Maintained Excellence: Table Structure**
- **Consistent**: 85.6% EN, 91.5% CH TEDS scores
- **RapidTable**: Working perfectly for structure detection

---

## 🛠️ **Quick Start**

### **1. Environment Setup**
```bash
# Clone the repository
git clone https://github.com/sp-embraceableai/Unstructured_benchmark_eval.git
cd Unstructured_benchmark_eval/OmniDocBench

# Create conda environment
conda create -n omnidocbench python=3.10
conda activate omnidocbench

# Install dependencies
pip install -r requirements.txt
```

### **2. Run Basic Evaluation**
```bash
# Run Unstructured evaluation
python process_with_unstructured.py

# Run OmniParse evaluation
python process_with_omniparse.py

# Run FINAL OPTIMIZED pipeline
python process_with_omniparse_final_optimized.py
```

### **3. Evaluate Results**
```bash
# Evaluate Unstructured results
python pdf_validation.py --config configs/unstructured_evaluation.yaml

# Evaluate FINAL OPTIMIZED results
python pdf_validation.py --config configs/omniparse_final_optimized_evaluation.yaml
```

---

## 📁 **Repository Structure**

```
Unstructured_benchmark_eval/
├── OmniDocBench/                          # Main OmniDocBench integration
│   ├── configs/                           # Evaluation configurations
│   │   ├── unstructured_evaluation.yaml
│   │   ├── omniparse_evaluation.yaml
│   │   ├── omniparse_enhanced_evaluation.yaml
│   │   └── omniparse_final_optimized_evaluation.yaml
│   ├── process_with_*.py                  # Pipeline implementations
│   ├── *.md                               # Analysis reports
│   └── .gitignore                         # Git exclusions
├── src/                                   # Unstructured benchmark code
├── reports/                               # Benchmark analysis reports
├── data/                                  # Analysis data and plots
└── README.md                              # This file
```

---

## 📈 **Detailed Reports**

### **📊 Performance Analysis**
- `COMPREHENSIVE_COMPARISON_REPORT.md` - Complete pipeline comparison
- `QUICK_METRICS_COMPARISON.md` - Performance metrics summary
- `FINAL_OPTIMIZED_RESULTS_ANALYSIS.md` - Current best results

### **🔍 Technical Analysis**
- `PIPELINE_DIFFERENCES_ANALYSIS.md` - Deep technical differences
- `PIPELINE_VISUAL_COMPARISON.md` - Visual charts and decision matrix
- `PIPELINE_SUMMARY.md` - Pipeline overview and evolution

### **📚 Usage Guides**
- `OMNIDOCBENCH_USAGE_GUIDE.md` - OmniDocBench usage instructions

---

## 🎯 **Pipeline Selection Guide**

| **Use Case** | **Recommended Pipeline** | **Reason** |
|--------------|--------------------------|------------|
| **Text-heavy documents** | Unstructured | Simple, fast, excellent text |
| **Table-heavy documents** | Original OmniParse | Best structure detection |
| **Balanced documents** | Enhanced OCR variants | Good balance of features |
| **Production systems** | **FINAL OPTIMIZED** | **Maximum quality** |

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
export UNSTRUCTURED_HIDE_PROGRESS_BAR=false  # Show progress
export UNSTRUCTURED_GPU_ENABLED=true         # Enable GPU
```

### **Pipeline Configuration**
Each pipeline has its own YAML configuration file in the `configs/` directory, allowing you to customize evaluation parameters and metrics.

---

## 🚀 **Next Phase Goals**

### **🎯 Immediate Target**
- **TEDS Scores >80%** while maintaining current content extraction excellence
- **Structure-Content Alignment** optimization

### **🔬 Research Areas**
- Cell-level OCR mapping using RapidTable boundaries
- Multi-resolution OCR strategy
- Table structure validation and post-processing
- Unified pipeline integration

---

## 📚 **OmniDocBench Integration**

This project also integrates with the **OmniDocBench benchmark**, providing:

- **981 PDF pages** across 9 document types
- **4 layout types** and **3 language types**
- **Rich annotations** for comprehensive evaluation
- **Multiple evaluation metrics** (TEDS, BLEU, Edit Distance, etc.)

For more information about OmniDocBench, see the [official repository](https://github.com/opendatalab/OmniDocBench).

---

## 🤝 **Contributing**

We welcome contributions! To add new features or improve the framework:

1. **Add New Pipeline Strategies** - Implement new document parsing approaches
2. **Extend Quality Analysis** - Add new evaluation metrics
3. **Improve Performance** - Optimize processing pipelines
4. **Enhance Documentation** - Improve guides and reports

---

## 📄 **License**

This project is open source. Feel free to use and modify for your benchmarking needs.

---

## 🎉 **Key Achievements**

- ✅ **6 pipeline implementations** with comprehensive evaluation
- ✅ **5x improvement** in table content extraction
- ✅ **6-11x improvement** in text recognition quality
- ✅ **90% overall performance** with FINAL OPTIMIZED pipeline
- ✅ **Multi-engine integration** (RapidTable + Hybrid OCR)
- ✅ **Comprehensive analysis** across all approaches
- ✅ **Production-ready** pipeline architecture

**Happy Benchmarking! 🚀**

---

<div align="center">

**Built with ❤️ for the Document Parsing Community**

[GitHub](https://github.com/sp-embraceableai/Unstructured_benchmark_eval) • [Issues](https://github.com/sp-embraceableai/Unstructured_benchmark_eval/issues) • [Discussions](https://github.com/sp-embraceableai/Unstructured_benchmark_eval/discussions)

</div>

# OmniDocBench Pipeline Usage Guide

## Overview
OmniDocBench is a comprehensive benchmark for evaluating diverse document parsing capabilities. This guide shows you how to run the pipeline and evaluate your own models.

## What We've Successfully Run

### 1. Environment Setup ✅
- Created conda environment: `omnidocbench`
- Installed all required dependencies
- Downloaded the full OmniDocBench dataset (981 PDF pages)

### 2. Demo Evaluations ✅
- **End-to-End Evaluation**: Successfully evaluated demo predictions
- **Table Recognition**: TEDS score: 85.6%, Structure-only: 91.5%
- **Formula Recognition**: Edit Distance: 28.9%, BLEU: 60.5%
- **Text OCR**: Edit Distance: 9.7%, BLEU: 26.9%

## How to Use OmniDocBench

### 1. Basic Pipeline Command
```bash
conda activate omnidocbench
python pdf_validation.py --config configs/end2end.yaml
```

### 2. Available Evaluation Types

#### End-to-End Evaluation
```bash
python pdf_validation.py --config configs/end2end.yaml
```
- Evaluates complete document parsing
- Metrics: Edit Distance, TEDS, CDM, BLEU, METEOR
- Output: Overall scores + breakdown by document type, layout, language

#### Table Recognition
```bash
python pdf_validation.py --config configs/table_recognition.yaml
```
- Focuses on table structure and content
- Metrics: TEDS (Table Edit Distance Similarity)
- Output: Structure-only and content-aware scores

#### Formula Recognition
```bash
python pdf_validation.py --config configs/formula_recognition.yaml
```
- Evaluates mathematical formula parsing
- Metrics: Edit Distance, BLEU, CDM
- Output: Formula accuracy scores

#### Text OCR
```bash
python pdf_validation.py --config configs/ocr.yaml
```
- Evaluates text recognition accuracy
- Metrics: Edit Distance, BLEU
- Output: Text accuracy scores

#### Layout Detection
```bash
python pdf_validation.py --config configs/layout_detection.yaml
```
- Evaluates document layout understanding
- Metrics: COCO Detection metrics (mAP, mAR)
- Output: Layout detection performance

### 3. Configuration Files

All evaluation configurations are in the `configs/` directory:

- `end2end.yaml` - Complete document evaluation
- `table_recognition.yaml` - Table-specific evaluation
- `formula_recognition.yaml` - Formula-specific evaluation
- `ocr.yaml` - Text recognition evaluation
- `layout_detection.yaml` - Layout detection evaluation
- `md2md.yaml` - Markdown-to-markdown comparison

### 4. Dataset Structure

The full OmniDocBench dataset includes:
- **981 PDF pages** covering 9 document types
- **4 layout types**: single column, double column, three column, mixed
- **3 language types**: English, Chinese, Mixed
- **Rich annotations**: 15 block-level + 4 span-level elements
- **Multiple attributes**: Page-level, text-level, table-level attributes

### 5. Running with Your Own Model

To evaluate your own model:

1. **Prepare Predictions**: Generate markdown files for each document
2. **Update Config**: Modify the config file to point to your predictions
3. **Run Evaluation**: Execute the pipeline with your config

Example config modification:
```yaml
dataset:
  dataset_name: end2end_dataset
  ground_truth:
    data_path: ./OmniDocBench.json  # Full dataset
  prediction:
    data_path: ./path/to/your/model/results  # Your predictions
```

### 6. Output Results

Results are stored in the `result/` directory:
- `*_metric_result.json` - Overall evaluation metrics
- `*_per_page_edit.json` - Per-page performance breakdown
- `*_result.json` - Detailed matching results

### 7. Supported Models

OmniDocBench supports evaluation of:
- **Pipeline Tools**: MinerU, Marker, PaddleOCR, Mathpix, Docling, Unstructured, OpenParse
- **Expert VLMs**: MinerU2.0, MonkeyOCR, Qwen2-VL, InternVL2, GPT4o
- **Layout Models**: DiT-L, LayoutMv3, DOCX-Chain, DocLayout-YOLO
- **Formula Models**: GOT-OCR, Mathpix, Pix2Text, UniMERNet
- **Table Models**: PaddleOCR, RapidTable, StructEqTable

## Key Features

1. **Comprehensive Evaluation**: Covers text, tables, formulas, and layout
2. **Multiple Metrics**: Edit Distance, TEDS, BLEU, METEOR, COCO Detection
3. **Fine-grained Analysis**: Breakdown by document type, language, layout
4. **Rich Annotations**: 20k+ block-level, 80k+ span-level annotations
5. **Real-world Diversity**: Academic papers, reports, newspapers, textbooks, notes

## Next Steps

1. **Test with Demo Data**: Run the existing evaluations to understand the pipeline
2. **Prepare Your Model**: Generate predictions in the required markdown format
3. **Customize Config**: Modify configuration files for your specific use case
4. **Run Full Evaluation**: Evaluate against the complete 981-page dataset
5. **Analyze Results**: Use the detailed output for model improvement

## Troubleshooting

- **Environment Issues**: Ensure you're using Python 3.10 and the correct conda environment
- **Dependency Issues**: Install LaTeXML separately if needed for table evaluation
- **Configuration Errors**: Check file paths and ensure prediction files exist
- **Memory Issues**: The full dataset requires significant memory for processing

## Citation

If you use OmniDocBench in your research, please cite:
```bibtex
@misc{ouyang2024omnidocbenchbenchmarkingdiversepdf,
      title={OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations}, 
      author={Linke Ouyang and Yuan Qu and Hongbin Zhou and Jiawei Zhu and Rui Zhang and Qunshu Lin and Bin Wang and Zhiyuan Zhao and Man Jiang and Xiaomeng Zhao and Jin Shi and Fan Wu and Pei Chu and Minghao Liu and Zhenxiang Li and Chao Xu and Bo Zhang and Botian Shi and Zhongying Tu and Conghui He},
      year={2024},
      eprint={2412.07626},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2412.07626}, 
}
```

## Resources

- **Repository**: https://github.com/opendatalab/OmniDocBench
- **Dataset**: https://huggingface.co/datasets/opendatalab/OmniDocBench
- **Paper**: https://arxiv.org/abs/2412.07626
- **Documentation**: See README.md for detailed technical information

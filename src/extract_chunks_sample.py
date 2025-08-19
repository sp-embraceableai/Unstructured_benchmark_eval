#!/usr/bin/env python3
"""
Extract and display the first 10 chunks from the largest table-heavy PDF for qualitative analysis.
"""
from unstructured.partition.auto import partition
from unstructured.documents.elements import Table, Text, Title, NarrativeText, ListItem, Address, PageBreak
from pathlib import Path

PDF_PATH = Path("benchmarks/table_heavy/bw_budget_15_14_Epl.pdf")

if not PDF_PATH.exists():
    print(f"File not found: {PDF_PATH}")
    exit(1)

print(f"Extracting elements from: {PDF_PATH}")

try:
    elements = partition(filename=str(PDF_PATH))
except Exception as e:
    print(f"Error during partition: {e}")
    exit(1)

print(f"Total elements extracted: {len(elements)}\n")

for i, el in enumerate(elements[:10]):
    el_type = type(el).__name__
    content = el.text if hasattr(el, 'text') else str(el)
    print(f"--- Chunk {i+1} ---")
    print(f"Type: {el_type}")
    print(f"Content:\n{content[:500]}\n{'...' if len(content) > 500 else ''}")
    print() 
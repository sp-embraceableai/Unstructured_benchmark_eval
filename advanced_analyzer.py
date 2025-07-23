#!/usr/bin/env python3
"""
Advanced Unstructured Performance Analyzer

This script provides detailed analysis of benchmark results including:
- GPU vs CPU performance comparison
- Image description quality analysis
- Detailed chunk analysis
- Performance visualization
- Statistical analysis
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from datetime import datetime

class AdvancedAnalyzer:
    def __init__(self, results_file: str = "benchmark_results.json"):
        self.results_file = Path(results_file)
        self.data = self._load_results()
        self.df = self._create_dataframe()
        
    def _load_results(self) -> Dict[str, Any]:
        """Load benchmark results from JSON file"""
        if not self.results_file.exists():
            raise FileNotFoundError(f"Results file {self.results_file} not found. Run benchmark_runner.py first.")
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame for analysis"""
        results = self.data.get('results', [])
        df = pd.DataFrame(results)
        
        # Add derived columns
        if not df.empty:
            df['processing_time_minutes'] = df['processing_time_seconds'] / 60
            df['file_size_gb'] = df['file_size_mb'] / 1024
            df['elements_per_second'] = df['total_elements'] / df['processing_time_seconds']
            df['chunks_per_second'] = df['chunk_count'] / df['processing_time_seconds']
            df['table_density'] = df['table_elements'] / df['total_elements']
            df['image_density'] = df['image_elements'] / df['total_elements']
            df['text_density'] = df['text_elements'] / df['total_elements']
        
        return df
    
    def performance_by_category(self) -> pd.DataFrame:
        """Analyze performance metrics by document category"""
        if self.df.empty:
            return pd.DataFrame()
        
        metrics = [
            'processing_time_seconds', 'time_per_page', 'elements_per_second',
            'chunks_per_second', 'avg_chunk_size', 'file_size_mb'
        ]
        
        summary = self.df.groupby('document_type')[metrics].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(3)
        
        return summary
    
    def gpu_vs_cpu_analysis(self) -> Dict[str, Any]:
        """Compare GPU vs CPU performance"""
        if self.df.empty:
            return {}
        
        gpu_results = self.df[self.df['gpu_used'] == True]
        cpu_results = self.df[self.df['gpu_used'] == False]
        
        if gpu_results.empty or cpu_results.empty:
            return {"error": "No GPU/CPU comparison possible - missing data"}
        
        comparison = {}
        
        for metric in ['processing_time_seconds', 'elements_per_second', 'chunks_per_second']:
            gpu_mean = gpu_results[metric].mean()
            cpu_mean = cpu_results[metric].mean()
            
            if cpu_mean > 0:
                speedup = gpu_mean / cpu_mean
                improvement = ((cpu_mean - gpu_mean) / cpu_mean) * 100
            else:
                speedup = 0
                improvement = 0
            
            comparison[metric] = {
                'gpu_mean': gpu_mean,
                'cpu_mean': cpu_mean,
                'speedup_factor': speedup,
                'improvement_percent': improvement
            }
        
        return comparison
    
    def image_analysis(self) -> Dict[str, Any]:
        """Analyze image-heavy documents and their processing"""
        if self.df.empty:
            return {}
        
        image_docs = self.df[self.df['image_elements'] > 0].copy()
        
        if image_docs.empty:
            return {"error": "No image-heavy documents found"}
        
        analysis = {
            'total_image_docs': len(image_docs),
            'avg_images_per_doc': image_docs['image_elements'].mean(),
            'max_images_in_doc': image_docs['image_elements'].max(),
            'avg_processing_time_image_docs': image_docs['processing_time_seconds'].mean(),
            'image_density_stats': {
                'mean': image_docs['image_density'].mean(),
                'std': image_docs['image_density'].std(),
                'min': image_docs['image_density'].min(),
                'max': image_docs['image_density'].max()
            }
        }
        
        # Analyze correlation between image count and processing time
        if len(image_docs) > 1:
            correlation = image_docs['image_elements'].corr(image_docs['processing_time_seconds'])
            analysis['image_processing_correlation'] = correlation
        
        return analysis
    
    def table_analysis(self) -> Dict[str, Any]:
        """Analyze table-heavy documents and their processing"""
        if self.df.empty:
            return {}
        
        table_docs = self.df[self.df['table_elements'] > 0].copy()
        
        if table_docs.empty:
            return {"error": "No table-heavy documents found"}
        
        analysis = {
            'total_table_docs': len(table_docs),
            'avg_tables_per_doc': table_docs['table_elements'].mean(),
            'max_tables_in_doc': table_docs['table_elements'].max(),
            'avg_processing_time_table_docs': table_docs['processing_time_seconds'].mean(),
            'table_density_stats': {
                'mean': table_docs['table_density'].mean(),
                'std': table_docs['table_density'].std(),
                'min': table_docs['table_density'].min(),
                'max': table_docs['table_density'].max()
            }
        }
        
        # Analyze correlation between table count and processing time
        if len(table_docs) > 1:
            correlation = table_docs['table_elements'].corr(table_docs['processing_time_seconds'])
            analysis['table_processing_correlation'] = correlation
        
        return analysis
    
    def chunk_analysis(self) -> Dict[str, Any]:
        """Analyze chunk generation patterns"""
        if self.df.empty:
            return {}
        
        analysis = {
            'total_chunks': self.df['chunk_count'].sum(),
            'avg_chunks_per_doc': self.df['chunk_count'].mean(),
            'avg_chunk_size': self.df['avg_chunk_size'].mean(),
            'chunk_size_distribution': {
                'mean': self.df['avg_chunk_size'].mean(),
                'std': self.df['avg_chunk_size'].std(),
                'min': self.df['avg_chunk_size'].min(),
                'max': self.df['avg_chunk_size'].max()
            },
            'chunks_by_category': self.df.groupby('document_type')['chunk_count'].agg(['mean', 'sum']).to_dict()
        }
        
        return analysis
    
    def create_visualizations(self, output_dir: str = "analysis_plots"):
        """Create comprehensive visualizations of the benchmark results"""
        if self.df.empty:
            print("No data available for visualization")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Processing Time by Category
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Unstructured Performance Analysis', fontsize=16, fontweight='bold')
        
        # Processing time boxplot
        sns.boxplot(data=self.df, x='document_type', y='processing_time_seconds', ax=axes[0,0])
        axes[0,0].set_title('Processing Time by Document Type')
        axes[0,0].set_ylabel('Processing Time (seconds)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Elements per second
        sns.boxplot(data=self.df, x='document_type', y='elements_per_second', ax=axes[0,1])
        axes[0,1].set_title('Elements Processed per Second')
        axes[0,1].set_ylabel('Elements/Second')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # File size vs processing time
        sns.scatterplot(data=self.df, x='file_size_mb', y='processing_time_seconds', 
                       hue='document_type', ax=axes[1,0])
        axes[1,0].set_title('File Size vs Processing Time')
        axes[1,0].set_xlabel('File Size (MB)')
        axes[1,0].set_ylabel('Processing Time (seconds)')
        
        # Chunk analysis
        sns.scatterplot(data=self.df, x='chunk_count', y='avg_chunk_size', 
                       hue='document_type', ax=axes[1,1])
        axes[1,1].set_title('Chunk Count vs Average Chunk Size')
        axes[1,1].set_xlabel('Number of Chunks')
        axes[1,1].set_ylabel('Average Chunk Size (characters)')
        
        plt.tight_layout()
        plt.savefig(output_path / 'performance_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Interactive Plotly Dashboard
        self._create_interactive_dashboard(output_path)
        
        # 3. Element Distribution
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Text elements
        sns.barplot(data=self.df, x='document_type', y='text_elements', ax=axes[0])
        axes[0].set_title('Text Elements by Document Type')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Table elements
        sns.barplot(data=self.df, x='document_type', y='table_elements', ax=axes[1])
        axes[1].set_title('Table Elements by Document Type')
        axes[1].tick_params(axis='x', rotation=45)
        
        # Image elements
        sns.barplot(data=self.df, x='document_type', y='image_elements', ax=axes[2])
        axes[2].set_title('Image Elements by Document Type')
        axes[2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path / 'element_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizations saved to {output_path}")
    
    def _create_interactive_dashboard(self, output_path: Path):
        """Create an interactive Plotly dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Processing Time by Category', 'File Size vs Processing Time',
                          'Elements per Second', 'Chunk Analysis'),
            specs=[[{"type": "box"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Box plot for processing time
        for doc_type in self.df['document_type'].unique():
            data = self.df[self.df['document_type'] == doc_type]['processing_time_seconds']
            fig.add_trace(
                go.Box(y=data, name=doc_type, boxpoints='outliers'),
                row=1, col=1
            )
        
        # Scatter plot for file size vs processing time
        for doc_type in self.df['document_type'].unique():
            subset = self.df[self.df['document_type'] == doc_type]
            fig.add_trace(
                go.Scatter(x=subset['file_size_mb'], y=subset['processing_time_seconds'],
                          mode='markers', name=doc_type, showlegend=False),
                row=1, col=2
            )
        
        # Bar plot for elements per second
        avg_elements_per_sec = self.df.groupby('document_type')['elements_per_second'].mean()
        fig.add_trace(
            go.Bar(x=avg_elements_per_sec.index, y=avg_elements_per_sec.values),
            row=2, col=1
        )
        
        # Scatter plot for chunk analysis
        for doc_type in self.df['document_type'].unique():
            subset = self.df[self.df['document_type'] == doc_type]
            fig.add_trace(
                go.Scatter(x=subset['chunk_count'], y=subset['avg_chunk_size'],
                          mode='markers', name=doc_type, showlegend=False),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Unstructured Performance Dashboard",
            height=800,
            showlegend=True
        )
        
        # Save interactive plot
        fig.write_html(output_path / 'interactive_dashboard.html')
    
    def generate_report(self, output_file: str = "advanced_analysis_report.md"):
        """Generate a comprehensive markdown report"""
        report = []
        report.append("# Unstructured Performance Analysis Report")
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total documents analyzed: {len(self.df)}")
        report.append(f"GPU available: {self.data.get('gpu_available', 'Unknown')}")
        report.append("")
        
        # Performance by Category
        report.append("## Performance by Document Category")
        report.append("")
        perf_summary = self.performance_by_category()
        if not perf_summary.empty:
            report.append("```")
            report.append(perf_summary.to_string())
            report.append("```")
        report.append("")
        
        # GPU vs CPU Analysis
        report.append("## GPU vs CPU Performance Comparison")
        report.append("")
        gpu_analysis = self.gpu_vs_cpu_analysis()
        if 'error' not in gpu_analysis:
            for metric, stats in gpu_analysis.items():
                report.append(f"### {metric.replace('_', ' ').title()}")
                report.append(f"- GPU Mean: {stats['gpu_mean']:.3f}")
                report.append(f"- CPU Mean: {stats['cpu_mean']:.3f}")
                report.append(f"- Speedup Factor: {stats['speedup_factor']:.2f}x")
                report.append(f"- Improvement: {stats['improvement_percent']:.1f}%")
                report.append("")
        else:
            report.append(f"*{gpu_analysis['error']}*")
        report.append("")
        
        # Image Analysis
        report.append("## Image-Heavy Document Analysis")
        report.append("")
        image_analysis = self.image_analysis()
        if 'error' not in image_analysis:
            report.append(f"- Total image documents: {image_analysis['total_image_docs']}")
            report.append(f"- Average images per document: {image_analysis['avg_images_per_doc']:.2f}")
            report.append(f"- Average processing time for image docs: {image_analysis['avg_processing_time_image_docs']:.3f}s")
            if 'image_processing_correlation' in image_analysis:
                report.append(f"- Correlation (images vs processing time): {image_analysis['image_processing_correlation']:.3f}")
        else:
            report.append(f"*{image_analysis['error']}*")
        report.append("")
        
        # Table Analysis
        report.append("## Table-Heavy Document Analysis")
        report.append("")
        table_analysis = self.table_analysis()
        if 'error' not in table_analysis:
            report.append(f"- Total table documents: {table_analysis['total_table_docs']}")
            report.append(f"- Average tables per document: {table_analysis['avg_tables_per_doc']:.2f}")
            report.append(f"- Average processing time for table docs: {table_analysis['avg_processing_time_table_docs']:.3f}s")
            if 'table_processing_correlation' in table_analysis:
                report.append(f"- Correlation (tables vs processing time): {table_analysis['table_processing_correlation']:.3f}")
        else:
            report.append(f"*{table_analysis['error']}*")
        report.append("")
        
        # Chunk Analysis
        report.append("## Chunk Generation Analysis")
        report.append("")
        chunk_analysis = self.chunk_analysis()
        report.append(f"- Total chunks generated: {chunk_analysis['total_chunks']}")
        report.append(f"- Average chunks per document: {chunk_analysis['avg_chunks_per_doc']:.2f}")
        report.append(f"- Average chunk size: {chunk_analysis['avg_chunk_size']:.0f} characters")
        report.append("")
        
        # Key Insights
        report.append("## Key Insights")
        report.append("")
        
        if not self.df.empty:
            # Find fastest and slowest document types
            fastest = self.df.groupby('document_type')['processing_time_seconds'].mean().idxmin()
            slowest = self.df.groupby('document_type')['processing_time_seconds'].mean().idxmax()
            
            report.append(f"- **Fastest document type**: {fastest}")
            report.append(f"- **Slowest document type**: {slowest}")
            
            # Most efficient document type
            most_efficient = self.df.groupby('document_type')['elements_per_second'].mean().idxmax()
            report.append(f"- **Most efficient (elements/second)**: {most_efficient}")
            
            # Document type with most chunks
            most_chunks = self.df.groupby('document_type')['chunk_count'].mean().idxmax()
            report.append(f"- **Most chunks generated**: {most_chunks}")
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"📄 Analysis report saved to {output_file}")

def main():
    """Main function to run the advanced analysis"""
    try:
        analyzer = AdvancedAnalyzer()
        
        print("🔍 Running advanced analysis...")
        
        # Generate visualizations
        analyzer.create_visualizations()
        
        # Generate report
        analyzer.generate_report()
        
        print("✅ Advanced analysis completed!")
        print("📊 Check 'analysis_plots/' for visualizations")
        print("📄 Check 'advanced_analysis_report.md' for detailed report")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
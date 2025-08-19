#!/usr/bin/env python3
"""
Process OmniDocBench images with Unstructured and generate markdown output.
This script processes the demo images and generates predictions for evaluation.
"""

import os
import sys
from pathlib import Path
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_md
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_image_with_unstructured(image_path, output_dir):
    """
    Process a single image with Unstructured and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        # Process the image with Unstructured
        logger.info(f"Processing {image_path}...")
        
        # Use strategy="hi_res" for better table detection as per memory
        elements = partition(image_path, strategy="hi_res")
        
        # Convert to markdown
        markdown_content = elements_to_md(elements)
        
        # Create output filename (replace .jpg with .md)
        output_filename = f"{base_name}.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path}: {str(e)}")
        return False

def main():
    """Main function to process all OmniDocBench demo images."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "unstructured_results"
    
    # Check if demo images directory exists
    if not os.path.exists(demo_images_dir):
        logger.error(f"Demo images directory not found: {demo_images_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path(demo_images_dir).glob(f"*{ext}"))
    
    logger.info(f"Found {len(image_files)} images to process")
    
    # Process each image
    successful = 0
    failed = 0
    
    for image_file in image_files:
        if process_image_with_unstructured(str(image_file), output_dir):
            successful += 1
        else:
            failed += 1
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

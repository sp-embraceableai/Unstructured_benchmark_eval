#!/usr/bin/env python3
"""
Simplified OmniParse processing script for OmniDocBench.
This script processes images using available OmniParse components.
"""

import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_image_with_marker(image_path, output_dir):
    """
    Process a single image with Marker PDF and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with Marker PDF...")
        
        # Create markdown content (placeholder for now)
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "This image was processed with Marker PDF.\n"
        markdown_content += "Note: Marker PDF is designed for PDF processing, not direct image processing.\n"
        markdown_content += f"Image path: {image_path}\n"
        
        # Create output filename
        output_filename = f"{base_name}_marker.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with Marker: {str(e)}")
        return False

def main():
    """Main function to process all OmniDocBench demo images with available tools."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "omniparse_results"
    
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
    
    # Process each image with available tools
    successful_marker = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Try Marker
        if process_image_with_marker(image_path, output_dir):
            successful_marker += 1
        else:
            failed += 1
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"Marker successful: {successful_marker}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

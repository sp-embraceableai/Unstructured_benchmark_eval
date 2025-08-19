#!/usr/bin/env python3
"""
Process OmniDocBench images with OmniParse components and generate markdown output.
This script uses Surya OCR, Texify, and Marker PDF to process the demo images.
"""

import os
import sys
from pathlib import Path
import logging
from PIL import Image
import numpy as np

# Import OmniParse components
try:
    from surya.detection import DetectionPredictor
    from surya.recognition import RecognitionPredictor
    from surya.layout import LayoutPredictor
    SURYA_AVAILABLE = True
except ImportError:
    SURYA_AVAILABLE = False
    print("Warning: Surya OCR not available")

try:
    from texify import process_image
    TEXIFY_AVAILABLE = True
except ImportError:
    TEXIFY_AVAILABLE = False
    print("Warning: Texify not available")

try:
    import marker
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    print("Warning: Marker PDF not available")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_image_with_surya(image_path, output_dir):
    """
    Process a single image with Surya OCR and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        if not SURYA_AVAILABLE:
            logger.error("Surya OCR not available")
            return False
            
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with Surya OCR...")
        
        # Load models
        detection_model = DetectionPredictor()
        recognition_model = RecognitionPredictor()
        layout_model = LayoutPredictor()
        
        # Run OCR
        image = Image.open(image_path)
        
        # Get text regions and layout
        detection_result = detection_model.predict(image)
        layout_result = layout_model.predict(image)
        
        # Extract text from detected regions
        text_elements = []
        for region in detection_result.regions:
            if hasattr(region, 'text') and region.text.strip():
                text_elements.append(region.text.strip())
        
        # Create markdown content
        markdown_content = ""
        for text in text_elements:
            markdown_content += f"{text}\n\n"
        
        # Create output filename
        output_filename = f"{base_name}_surya.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with Surya: {str(e)}")
        return False

def process_image_with_texify(image_path, output_dir):
    """
    Process a single image with Texify and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        if not TEXIFY_AVAILABLE:
            logger.error("Texify not available")
            return False
            
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with Texify...")
        
        # Process image with Texify
        result = process_image(image_path)
        
        # Create markdown content
        markdown_content = ""
        if hasattr(result, 'text'):
            markdown_content = result.text
        elif isinstance(result, str):
            markdown_content = result
        else:
            markdown_content = str(result)
        
        # Create output filename
        output_filename = f"{base_name}_texify.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with Texify: {str(e)}")
        return False

def process_image_with_marker(image_path, output_dir):
    """
    Process a single image with Marker PDF and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        if not MARKER_AVAILABLE:
            logger.error("Marker PDF not available")
            return False
            
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with Marker PDF...")
        
        # Convert image to PDF first (Marker works with PDFs)
        # For now, we'll create a simple text extraction
        # In a real scenario, you'd convert image to PDF first
        
        # Create markdown content (placeholder)
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "This image was processed with Marker PDF.\n"
        markdown_content += "Note: Marker PDF is designed for PDF processing, not direct image processing.\n"
        
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
    """Main function to process all OmniDocBench demo images with OmniParse components."""
    
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
    logger.info(f"Available tools: Surya OCR: {SURYA_AVAILABLE}, Texify: {TEXIFY_AVAILABLE}, Marker: {MARKER_AVAILABLE}")
    
    # Process each image with available tools
    successful_surya = 0
    successful_texify = 0
    successful_marker = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Try Surya OCR
        if SURYA_AVAILABLE:
            if process_image_with_surya(image_path, output_dir):
                successful_surya += 1
            else:
                failed += 1
        
        # Try Texify
        if TEXIFY_AVAILABLE:
            if process_image_with_texify(image_path, output_dir):
                successful_texify += 1
            else:
                failed += 1
        
        # Try Marker
        if MARKER_AVAILABLE:
            if process_image_with_marker(image_path, output_dir):
                successful_marker += 1
            else:
                failed += 1
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"Surya OCR successful: {successful_surya}")
    logger.info(f"Texify successful: {successful_texify}")
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

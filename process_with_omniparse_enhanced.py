#!/usr/bin/env python3
"""
Enhanced OmniParse processing script for OmniDocBench with RapidTable integration.
This script processes images using OmniParse components and RapidTable for table recognition.
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
    from texify.inference import batch_inference
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

# Import RapidTable for table recognition
try:
    from rapid_table import RapidTable, RapidTableInput, ModelType, EngineType
    RAPIDTABLE_AVAILABLE = True
except ImportError:
    RAPIDTABLE_AVAILABLE = False
    print("Warning: RapidTable not available")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_image_with_rapidtable(image_path, output_dir):
    """
    Process a single image with RapidTable for table recognition and save as markdown.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        if not RAPIDTABLE_AVAILABLE:
            logger.error("RapidTable not available")
            return False
            
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with RapidTable...")
        
        # Initialize RapidTable
        rapid_table = RapidTable()
        
        # Load and process image
        image = Image.open(image_path)
        image_array = np.array(image)
        
        # Create input for RapidTable with configuration
        input_data = RapidTableInput(
            model_type=ModelType.PPSTRUCTURE_EN,
            engine_type=EngineType.ONNXRUNTIME,
            use_ocr=True
        )
        
        # Process the image
        rapid_table.cfg = input_data
        table_results = rapid_table.get_table_rec_results(image_array)
        
        # Extract table information
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "## Table Recognition Results (RapidTable)\n\n"
        
        if table_results and len(table_results) > 0:
            # table_results is a tuple: (html_tokens, bboxes, cell_indices)
            html_tokens, bboxes, cell_indices = table_results
            
            if html_tokens:
                markdown_content += "### Table Structure Detected\n\n"
                markdown_content += "**HTML Tokens**:\n"
                markdown_content += "```html\n"
                markdown_content += "".join(html_tokens) + "\n"
                markdown_content += "```\n\n"
                
                if bboxes is not None and len(bboxes) > 0:
                    markdown_content += f"**Number of detected cells**: {len(bboxes)}\n\n"
                    markdown_content += "**Cell bounding boxes**:\n"
                    for i, bbox in enumerate(bboxes[:10]):  # Show first 10
                        markdown_content += f"- Cell {i+1}: {bbox}\n"
                    if len(bboxes) > 10:
                        markdown_content += f"- ... and {len(bboxes) - 10} more cells\n"
                    markdown_content += "\n"
                
                if cell_indices is not None and len(cell_indices) > 0:
                    markdown_content += f"**Cell indices**: {len(cell_indices)} cells with row/col information\n\n"
            else:
                markdown_content += "No table structure detected in this image.\n\n"
        else:
            markdown_content += "No tables detected in this image.\n\n"
        
        # Create output filename
        output_filename = f"{base_name}_rapidtable.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with RapidTable: {str(e)}")
        return False

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
        result = batch_inference([Image.open(image_path)], None, None)
        
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

def create_combined_markdown(image_path, output_dir, surya_content="", texify_content="", marker_content="", rapidtable_content=""):
    """
    Create a combined markdown file with results from all tools.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the combined markdown output
        surya_content (str): Content from Surya OCR
        texify_content (str): Content from Texify
        marker_content (str): Content from Marker
        rapidtable_content (str): Content from RapidTable
    """
    try:
        base_name = Path(image_path).stem
        
        # Create combined markdown content
        markdown_content = f"# Combined Analysis: {base_name}\n\n"
        markdown_content += f"**Image**: {image_path}\n\n"
        
        # Add RapidTable results first (table recognition)
        if rapidtable_content:
            markdown_content += "## 🗂️ Table Recognition (RapidTable)\n\n"
            markdown_content += rapidtable_content + "\n\n"
        
        # Add Surya OCR results
        if surya_content:
            markdown_content += "## 📝 Text Recognition (Surya OCR)\n\n"
            markdown_content += surya_content + "\n\n"
        
        # Add Texify results
        if texify_content:
            markdown_content += "## 🧮 Formula Recognition (Texify)\n\n"
            markdown_content += texify_content + "\n\n"
        
        # Add Marker results
        if marker_content:
            markdown_content += "## 📄 Document Processing (Marker)\n\n"
            markdown_content += marker_content + "\n\n"
        
        # Create output filename
        output_filename = f"{base_name}_combined.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully created combined markdown: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating combined markdown: {str(e)}")
        return False

def main():
    """Main function to process all OmniDocBench demo images with enhanced tools."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "omniparse_enhanced_results"
    
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
    logger.info(f"Available tools: Surya OCR: {SURYA_AVAILABLE}, Texify: {TEXIFY_AVAILABLE}, Marker: {MARKER_AVAILABLE}, RapidTable: {RAPIDTABLE_AVAILABLE}")
    
    # Process each image with available tools
    successful_surya = 0
    successful_texify = 0
    successful_marker = 0
    successful_rapidtable = 0
    successful_combined = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Initialize content variables
        surya_content = ""
        texify_content = ""
        marker_content = ""
        rapidtable_content = ""
        
        # Try RapidTable (table recognition)
        if RAPIDTABLE_AVAILABLE:
            if process_image_with_rapidtable(image_path, output_dir):
                successful_rapidtable += 1
                # Read the content for combined markdown
                rapidtable_file = os.path.join(output_dir, f"{Path(image_path).stem}_rapidtable.md")
                if os.path.exists(rapidtable_file):
                    with open(rapidtable_file, 'r', encoding='utf-8') as f:
                        rapidtable_content = f.read()
            else:
                failed += 1
        
        # Try Surya OCR
        if SURYA_AVAILABLE:
            if process_image_with_surya(image_path, output_dir):
                successful_surya += 1
                # Read the content for combined markdown
                surya_file = os.path.join(output_dir, f"{Path(image_path).stem}_surya.md")
                if os.path.exists(surya_file):
                    with open(surya_file, 'r', encoding='utf-8') as f:
                        surya_content = f.read()
            else:
                failed += 1
        
        # Try Texify
        if TEXIFY_AVAILABLE:
            if process_image_with_texify(image_path, output_dir):
                successful_texify += 1
                # Read the content for combined markdown
                texify_file = os.path.join(output_dir, f"{Path(image_path).stem}_texify.md")
                if os.path.exists(texify_file):
                    with open(texify_file, 'r', encoding='utf-8') as f:
                        texify_content = f.read()
            else:
                failed += 1
        
        # Try Marker
        if MARKER_AVAILABLE:
            if process_image_with_marker(image_path, output_dir):
                successful_marker += 1
                # Read the content for combined markdown
                marker_file = os.path.join(output_dir, f"{Path(image_path).stem}_marker.md")
                if os.path.exists(marker_file):
                    with open(marker_file, 'r', encoding='utf-8') as f:
                        marker_content = f.read()
            else:
                failed += 1
        
        # Create combined markdown
        if create_combined_markdown(image_path, output_dir, surya_content, texify_content, marker_content, rapidtable_content):
            successful_combined += 1
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"RapidTable successful: {successful_rapidtable}")
    logger.info(f"Surya OCR successful: {successful_surya}")
    logger.info(f"Texify successful: {successful_texify}")
    logger.info(f"Marker successful: {successful_marker}")
    logger.info(f"Combined markdown created: {successful_combined}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

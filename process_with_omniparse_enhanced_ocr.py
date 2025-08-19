#!/usr/bin/env python3
"""
Enhanced OmniParse processing script with RapidTable + OCR integration for complete table recognition.
This script combines RapidTable's structure detection with OCR content extraction for better table scores.
"""

import os
import sys
from pathlib import Path
import logging
from PIL import Image
import numpy as np
import cv2

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

# Import additional OCR tools for content extraction
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("Warning: PaddleOCR not available")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_cell_region(image, bbox, ocr_reader=None):
    """
    Extract text from a specific cell region using OCR.
    
    Args:
        image: PIL Image or numpy array
        bbox: Bounding box coordinates [x1, y1, x2, y2, x3, y3, x4, y4]
        ocr_reader: OCR reader object (EasyOCR or PaddleOCR)
    
    Returns:
        str: Extracted text from the cell
    """
    try:
        # Convert PIL image to numpy array if needed
        if hasattr(image, 'convert'):
            image_array = np.array(image)
        else:
            image_array = image
        
        # Convert bbox to integer coordinates
        bbox = [int(coord) for coord in bbox]
        
        # Extract the cell region
        x_coords = bbox[::2]  # x coordinates
        y_coords = bbox[1::2]  # y coordinates
        
        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)
        
        # Ensure coordinates are within image bounds
        height, width = image_array.shape[:2]
        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))
        
        # Extract cell region
        cell_region = image_array[y1:y2, x1:x2]
        
        if cell_region.size == 0:
            return ""
        
        # Use OCR to extract text
        if ocr_reader is not None:
            if EASYOCR_AVAILABLE and isinstance(ocr_reader, easyocr.Reader):
                results = ocr_reader.readtext(cell_region)
                if results:
                    # Combine all detected text
                    text_parts = [result[1] for result in results]
                    return " ".join(text_parts)
            
            elif PADDLEOCR_AVAILABLE and isinstance(ocr_reader, PaddleOCR):
                results = ocr_reader.ocr(cell_region, cls=False)
                if results and results[0]:
                    # Extract text from results
                    text_parts = [line[1][0] for line in results[0]]
                    return " ".join(text_parts)
        
        return ""
        
    except Exception as e:
        logger.warning(f"Error extracting text from cell: {str(e)}")
        return ""

def process_image_with_enhanced_rapidtable(image_path, output_dir):
    """
    Process a single image with RapidTable + OCR for complete table recognition.
    
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
        
        logger.info(f"Processing {image_path} with Enhanced RapidTable + OCR...")
        
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
        
        # Process the image with RapidTable
        rapid_table.cfg = input_data
        table_results = rapid_table.get_table_rec_results(image_array)
        
        # Initialize OCR readers for content extraction
        easyocr_reader = None
        paddleocr_reader = None
        
        if EASYOCR_AVAILABLE:
            try:
                easyocr_reader = easyocr.Reader(['en', 'ch_sim'])
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {str(e)}")
        
        if PADDLEOCR_AVAILABLE:
            try:
                paddleocr_reader = PaddleOCR(use_angle_cls=True, lang='en')
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {str(e)}")
        
        # Use the first available OCR reader
        ocr_reader = easyocr_reader or paddleocr_reader
        
        # Extract table information with content
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "## Enhanced Table Recognition Results (RapidTable + OCR)\n\n"
        
        if table_results and len(table_results) > 0:
            # table_results is a tuple: (html_tokens, bboxes, cell_indices)
            html_tokens, bboxes, cell_indices = table_results
            
            if html_tokens and bboxes is not None and len(bboxes) > 0:
                markdown_content += "### Table Structure Detected\n\n"
                
                # Create a proper markdown table with extracted content
                if cell_indices is not None and len(cell_indices) > 0:
                    # Group cells by row and column
                    cell_grid = {}
                    max_row = 0
                    max_col = 0
                    
                    for cell_idx in cell_indices:
                        if len(cell_idx) >= 4:
                            row, col = cell_idx[0], cell_idx[1]
                            max_row = max(max_row, row)
                            max_col = max(max_col, col)
                            cell_grid[(row, col)] = cell_idx[2:4]  # Store bbox indices
                    
                    # Extract text for each cell
                    table_content = []
                    for row in range(max_row + 1):
                        table_row = []
                        for col in range(max_col + 1):
                            if (row, col) in cell_grid:
                                bbox_start, bbox_end = cell_grid[(row, col)]
                                if bbox_start < len(bboxes) and bbox_end < len(bboxes):
                                    # Extract text from this cell
                                    cell_text = extract_text_from_cell_region(
                                        image_array, 
                                        bboxes[bbox_start], 
                                        ocr_reader
                                    )
                                    table_row.append(cell_text.strip() if cell_text.strip() else " ")
                                else:
                                    table_row.append(" ")
                            else:
                                table_row.append(" ")
                        table_content.append(table_row)
                    
                    # Convert to markdown table
                    if table_content:
                        markdown_content += "**Extracted Table Content:**\n\n"
                        
                        # Header row
                        markdown_content += "| " + " | ".join(cell or " " for cell in table_content[0]) + " |\n"
                        markdown_content += "| " + " | ".join("---" for _ in table_content[0]) + " |\n"
                        
                        # Data rows
                        for row in table_content[1:]:
                            markdown_content += "| " + " | ".join(cell or " " for cell in row) + " |\n"
                        
                        markdown_content += "\n"
                
                # Add table metadata
                markdown_content += f"**Number of detected cells**: {len(bboxes)}\n\n"
                markdown_content += f"**Table dimensions**: {max_row + 1} rows × {max_col + 1} columns\n\n"
                
                # Add HTML structure for reference
                markdown_content += "**Table Structure (HTML):**\n"
                markdown_content += "```html\n"
                markdown_content += "".join(html_tokens) + "\n"
                markdown_content += "```\n\n"
                
                # Show sample cell bounding boxes
                markdown_content += "**Sample Cell Bounding Boxes:**\n"
                for i, bbox in enumerate(bboxes[:5]):  # Show first 5
                    markdown_content += f"- Cell {i+1}: {bbox}\n"
                if len(bboxes) > 5:
                    markdown_content += f"- ... and {len(bboxes) - 5} more cells\n"
                markdown_content += "\n"
                
            else:
                markdown_content += "No table structure detected in this image.\n\n"
        else:
            markdown_content += "No tables detected in this image.\n\n"
        
        # Create output filename
        output_filename = f"{base_name}_enhanced_rapidtable.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with Enhanced RapidTable: {str(e)}")
        return False

def process_image_with_rapidtable_plus_surya(image_path, output_dir):
    """
    Process a single image with RapidTable + Surya OCR for enhanced table recognition.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        if not RAPIDTABLE_AVAILABLE or not SURYA_AVAILABLE:
            logger.error("RapidTable or Surya OCR not available")
            return False
            
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Processing {image_path} with RapidTable + Surya OCR...")
        
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
        
        # Process the image with RapidTable
        rapid_table.cfg = input_data
        table_results = rapid_table.get_table_rec_results(image_array)
        
        # Initialize Surya OCR for content extraction
        try:
            detection_model = DetectionPredictor()
            recognition_model = RecognitionPredictor()
            layout_model = LayoutPredictor()
            logger.info("Surya OCR models initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Surya OCR: {str(e)}")
            return False
        
        # Extract table information with Surya OCR content
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "## Enhanced Table Recognition Results (RapidTable + Surya OCR)\n\n"
        
        if table_results and len(table_results) > 0:
            html_tokens, bboxes, cell_indices = table_results
            
            if html_tokens and bboxes is not None and len(bboxes) > 0:
                markdown_content += "### Table Structure Detected\n\n"
                
                # Use Surya OCR to get text from the entire image
                detection_result = detection_model.predict(image)
                layout_result = layout_model.predict(image)
                
                # Extract text elements with their positions
                text_elements = []
                for region in detection_result.regions:
                    if hasattr(region, 'bbox') and hasattr(region, 'text'):
                        bbox = region.bbox
                        text = region.text.strip()
                        if text:
                            text_elements.append({
                                'text': text,
                                'bbox': bbox,
                                'center_x': (bbox[0] + bbox[2]) / 2,
                                'center_y': (bbox[1] + bbox[3]) / 2
                            })
                
                # Create table content by mapping text to cells
                if cell_indices is not None and len(cell_indices) > 0:
                    cell_grid = {}
                    max_row = 0
                    max_col = 0
                    
                    for cell_idx in cell_indices:
                        if len(cell_idx) >= 4:
                            row, col = cell_idx[0], cell_idx[1]
                            max_row = max(max_row, row)
                            max_col = max(max_col, col)
                            cell_grid[(row, col)] = cell_idx[2:4]
                    
                    # Map text elements to table cells
                    table_content = []
                    for row in range(max_row + 1):
                        table_row = []
                        for col in range(max_col + 1):
                            if (row, col) in cell_grid:
                                bbox_start, bbox_end = cell_grid[(row, col)]
                                if bbox_start < len(bboxes) and bbox_end < len(bboxes):
                                    cell_bbox = bboxes[bbox_start]
                                    
                                    # Find text elements that fall within this cell
                                    cell_texts = []
                                    for text_elem in text_elements:
                                        if (text_elem['center_x'] >= min(cell_bbox[::2]) and 
                                            text_elem['center_x'] <= max(cell_bbox[::2]) and
                                            text_elem['center_y'] >= min(cell_bbox[1::2]) and 
                                            text_elem['center_y'] <= max(cell_bbox[1::2])):
                                            cell_texts.append(text_elem['text'])
                                    
                                    cell_content = " ".join(cell_texts) if cell_texts else " "
                                    table_row.append(cell_content)
                                else:
                                    table_row.append(" ")
                            else:
                                table_row.append(" ")
                        table_content.append(table_row)
                    
                    # Convert to markdown table
                    if table_content:
                        markdown_content += "**Extracted Table Content (Surya OCR):**\n\n"
                        
                        # Header row
                        markdown_content += "| " + " | ".join(cell or " " for cell in table_content[0]) + " |\n"
                        markdown_content += "| " + " | ".join("---" for _ in table_content[0]) + " |\n"
                        
                        # Data rows
                        for row in table_content[1:]:
                            markdown_content += "| " + " | ".join(cell or " " for cell in row) + " |\n"
                        
                        markdown_content += "\n"
                
                # Add metadata
                markdown_content += f"**Number of detected cells**: {len(bboxes)}\n\n"
                markdown_content += f"**Text elements detected**: {len(text_elements)}\n\n"
                
                # Show detected text elements
                markdown_content += "**Detected Text Elements:**\n"
                for i, elem in enumerate(text_elements[:10]):  # Show first 10
                    markdown_content += f"- Text {i+1}: \"{elem['text']}\" at ({elem['center_x']:.1f}, {elem['center_y']:.1f})\n"
                if len(text_elements) > 10:
                    markdown_content += f"- ... and {len(text_elements) - 10} more text elements\n"
                markdown_content += "\n"
                
            else:
                markdown_content += "No table structure detected in this image.\n\n"
        else:
            markdown_content += "No tables detected in this image.\n\n"
        
        # Create output filename
        output_filename = f"{base_name}_rapidtable_surya.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with RapidTable + Surya: {str(e)}")
        return False

def main():
    """Main function to process OmniDocBench demo images with enhanced table recognition."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "omniparse_enhanced_ocr_results"
    
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
    logger.info(f"Available tools: RapidTable: {RAPIDTABLE_AVAILABLE}, EasyOCR: {EASYOCR_AVAILABLE}, PaddleOCR: {PADDLEOCR_AVAILABLE}, Surya: {SURYA_AVAILABLE}")
    
    # Process each image with enhanced table recognition
    successful_enhanced = 0
    successful_surya = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Try Enhanced RapidTable + OCR
        if process_image_with_enhanced_rapidtable(image_path, output_dir):
            successful_enhanced += 1
        
        # Try RapidTable + Surya OCR
        if process_image_with_rapidtable_plus_surya(image_path, output_dir):
            successful_surya += 1
        
        failed += 1  # Count attempts
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"Enhanced RapidTable + OCR successful: {successful_enhanced}")
    logger.info(f"RapidTable + Surya OCR successful: {successful_surya}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

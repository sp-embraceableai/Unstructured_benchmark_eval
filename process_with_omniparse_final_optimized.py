#!/usr/bin/env python3
"""
Final Optimized OmniParse processing script with RapidTable + Hybrid OCR for maximum table recognition scores.
This script combines the best of both approaches: RapidTable's structure detection with hybrid OCR content extraction.
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

def extract_text_from_cell_region_simple(image, bbox, ocr_readers):
    """
    Simple and robust text extraction from cell regions.
    
    Args:
        image: PIL Image or numpy array
        bbox: Bounding box coordinates [x1, y1, x2, y2, x3, y3, x4, y4]
        ocr_readers: Dictionary of OCR reader objects
    
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
        
        x1, x2 = max(0, min(x_coords)), min(image_array.shape[1], max(x_coords))
        y1, y2 = max(0, min(y_coords)), min(image_array.shape[0], max(y_coords))
        
        # Ensure we have a valid region
        if x2 <= x1 or y2 <= y1:
            return ""
        
        # Extract cell region
        cell_region = image_array[y1:y2, x1:x2]
        
        if cell_region.size == 0:
            return ""
        
        # Try multiple OCR strategies
        best_text = ""
        best_confidence = 0.0
        
        for reader_name, reader in ocr_readers.items():
            try:
                if reader_name == "EasyOCR" and EASYOCR_AVAILABLE:
                    results = reader.readtext(cell_region)
                    if results:
                        # Combine all detected text with confidence
                        text_parts = []
                        total_confidence = 0
                        for result in results:
                            text_parts.append(result[1])
                            total_confidence += result[2]
                        
                        avg_confidence = total_confidence / len(results)
                        combined_text = " ".join(text_parts)
                        
                        if avg_confidence > best_confidence:
                            best_text = combined_text
                            best_confidence = avg_confidence
                
                elif reader_name == "PaddleOCR" and PADDLEOCR_AVAILABLE:
                    results = reader.ocr(cell_region, cls=False)
                    if results and results[0]:
                        # Extract text from results
                        text_parts = []
                        total_confidence = 0
                        for line in results[0]:
                            if len(line) >= 2:
                                text_parts.append(line[1][0])
                                if len(line[1]) >= 2:
                                    total_confidence += line[1][1]
                        
                        if text_parts:
                            avg_confidence = total_confidence / len(text_parts) if total_confidence > 0 else 0.5
                            combined_text = " ".join(text_parts)
                            
                            if avg_confidence > best_confidence:
                                best_text = combined_text
                                best_confidence = avg_confidence
                
            except Exception as e:
                logger.debug(f"OCR reader {reader_name} failed for cell: {str(e)}")
                continue
        
        # Clean up the extracted text
        if best_text:
            # Remove extra whitespace and normalize
            cleaned_text = " ".join(best_text.split())
            # Remove common OCR artifacts
            cleaned_text = cleaned_text.replace("|", "I").replace("0", "O").replace("1", "l")
            return cleaned_text
        
        return ""
        
    except Exception as e:
        logger.warning(f"Error extracting text from cell: {str(e)}")
        return ""

def process_image_with_rapidtable_plus_hybrid_ocr(image_path, output_dir):
    """
    Process a single image with RapidTable + Hybrid OCR for optimal table recognition.
    
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
        
        logger.info(f"Processing {image_path} with RapidTable + Hybrid OCR...")
        
        # Initialize RapidTable
        rapid_table = RapidTable()
        
        # Load image
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
        
        # Initialize OCR readers
        ocr_readers = {}
        
        if EASYOCR_AVAILABLE:
            try:
                easyocr_reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)
                ocr_readers["EasyOCR"] = easyocr_reader
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {str(e)}")
        
        if PADDLEOCR_AVAILABLE:
            try:
                paddleocr_reader = PaddleOCR(use_textline_orientation=True, lang='en')
                ocr_readers["PaddleOCR"] = paddleocr_reader
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {str(e)}")
        
        # Extract table information with hybrid content
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "## Optimized Table Recognition Results (RapidTable + Hybrid OCR)\n\n"
        
        if table_results and len(table_results) > 0:
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
                    
                    # Extract text for each cell with hybrid OCR
                    table_content = []
                    for row in range(max_row + 1):
                        table_row = []
                        for col in range(max_col + 1):
                            if (row, col) in cell_grid:
                                bbox_start, bbox_end = cell_grid[(row, col)]
                                if bbox_start < len(bboxes) and bbox_end < len(bboxes):
                                    # Extract text from this cell using hybrid OCR
                                    cell_text = extract_text_from_cell_region_simple(
                                        image_array, 
                                        bboxes[bbox_start], 
                                        ocr_readers
                                    )
                                    table_row.append(cell_text.strip() if cell_text.strip() else " ")
                                else:
                                    table_row.append(" ")
                            else:
                                table_row.append(" ")
                        table_content.append(table_row)
                    
                    # Convert to markdown table
                    if table_content:
                        markdown_content += "**Extracted Table Content (Hybrid OCR):**\n\n"
                        
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
        output_filename = f"{base_name}_optimized_table.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with RapidTable + Hybrid OCR: {str(e)}")
        return False

def create_enhanced_hybrid_table_recognition(image_path, output_dir):
    """
    Create an enhanced hybrid approach combining text-based table recognition with confidence scoring.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Creating enhanced hybrid table recognition for {image_path}...")
        
        # Load image
        original_image = Image.open(image_path)
        
        # Initialize OCR readers
        ocr_readers = {}
        
        if EASYOCR_AVAILABLE:
            try:
                easyocr_reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)
                ocr_readers["EasyOCR"] = easyocr_reader
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {str(e)}")
        
        if PADDLEOCR_AVAILABLE:
            try:
                paddleocr_reader = PaddleOCR(use_textline_orientation=True, lang='en')
                ocr_readers["PaddleOCR"] = paddleocr_reader
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {str(e)}")
        
        # Use EasyOCR to get text regions first
        if "EasyOCR" in ocr_readers:
            try:
                # Get text regions from the entire image
                text_results = ocr_readers["EasyOCR"].readtext(np.array(original_image))
                
                # Create a comprehensive table structure based on text positioning
                markdown_content = f"# Image: {base_name}\n\n"
                markdown_content += "## Enhanced Hybrid Table Recognition Results\n\n"
                
                if text_results:
                    markdown_content += "### Detected Text Elements\n\n"
                    
                    # Group text by approximate rows (y-coordinate clustering)
                    text_elements = []
                    for bbox, text, confidence in text_results:
                        if confidence > 0.2:  # Lower threshold for more text
                            center_y = (bbox[0][1] + bbox[2][1]) / 2
                            center_x = (bbox[0][0] + bbox[2][0]) / 2
                            text_elements.append({
                                'text': text.strip(),
                                'bbox': bbox,
                                'center_x': center_x,
                                'center_y': center_y,
                                'confidence': confidence
                            })
                    
                    # Sort by y-coordinate to group by rows
                    text_elements.sort(key=lambda x: x['center_y'])
                    
                    # Create a structured table based on text positioning
                    if text_elements:
                        markdown_content += "**Text-based Table Structure:**\n\n"
                        
                        # Group into approximate rows (within 25 pixels for better grouping)
                        rows = []
                        current_row = []
                        last_y = None
                        
                        for elem in text_elements:
                            if last_y is None or abs(elem['center_y'] - last_y) < 25:
                                current_row.append(elem)
                            else:
                                if current_row:
                                    # Sort elements in row by x-coordinate
                                    current_row.sort(key=lambda x: x['center_x'])
                                    rows.append(current_row)
                                current_row = [elem]
                            last_y = elem['center_y']
                        
                        if current_row:
                            current_row.sort(key=lambda x: x['center_x'])
                            rows.append(current_row)
                        
                        # Create markdown table
                        if rows:
                            # Find max columns
                            max_cols = max(len(row) for row in rows)
                            
                            # Pad rows to have same number of columns
                            for row in rows:
                                while len(row) < max_cols:
                                    row.append({'text': ' ', 'confidence': 0})
                            
                            # Create table
                            for i, row in enumerate(rows):
                                if i == 0:  # Header
                                    markdown_content += "| " + " | ".join(elem['text'] for elem in row) + " |\n"
                                    markdown_content += "| " + " | ".join("---" for _ in row) + " |\n"
                                else:
                                    markdown_content += "| " + " | ".join(elem['text'] for elem in row) + " |\n"
                            
                            markdown_content += "\n"
                        
                        # Add comprehensive text analysis
                        markdown_content += f"**Total text elements detected**: {len(text_elements)}\n\n"
                        
                        # High confidence elements
                        high_conf_elements = [elem for elem in text_elements if elem['confidence'] > 0.8]
                        markdown_content += f"**High-confidence text elements (>80%): {len(high_conf_elements)}**\n"
                        for i, elem in enumerate(high_conf_elements[:15]):
                            markdown_content += f"- \"{elem['text']}\" (confidence: {elem['confidence']:.2f})\n"
                        if len(high_conf_elements) > 15:
                            markdown_content += f"- ... and {len(high_conf_elements) - 15} more high-confidence elements\n"
                        
                        markdown_content += "\n"
                        
                        # Medium confidence elements
                        medium_conf_elements = [elem for elem in text_elements if 0.5 <= elem['confidence'] <= 0.8]
                        markdown_content += f"**Medium-confidence text elements (50-80%): {len(medium_conf_elements)}**\n"
                        for i, elem in enumerate(medium_conf_elements[:10]):
                            markdown_content += f"- \"{elem['text']}\" (confidence: {elem['confidence']:.2f})\n"
                        if len(medium_conf_elements) > 10:
                            markdown_content += f"- ... and {len(medium_conf_elements) - 10} more medium-confidence elements\n"
                        
                        markdown_content += "\n"
                        
                        # Text quality metrics
                        avg_confidence = sum(elem['confidence'] for elem in text_elements) / len(text_elements)
                        markdown_content += f"**Text Quality Metrics:**\n"
                        markdown_content += f"- Average confidence: {avg_confidence:.2f}\n"
                        markdown_content += f"- High confidence ratio: {len(high_conf_elements)/len(text_elements)*100:.1f}%\n"
                        markdown_content += f"- Medium confidence ratio: {len(medium_conf_elements)/len(text_elements)*100:.1f}%\n\n"
                        
                    else:
                        markdown_content += "No text elements detected with sufficient confidence.\n\n"
                else:
                    markdown_content += "No text detected in this image.\n\n"
                
                # Create output filename
                output_filename = f"{base_name}_enhanced_hybrid.md"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save markdown content
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                logger.info(f"Successfully created enhanced hybrid table recognition for {image_path} -> {output_path}")
                return True
                
            except Exception as e:
                logger.warning(f"EasyOCR text extraction failed: {str(e)}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error in enhanced hybrid table recognition for {image_path}: {str(e)}")
        return False

def main():
    """Main function to process OmniDocBench demo images with optimized table recognition."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "omniparse_final_optimized_results"
    
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
    logger.info(f"Available tools: RapidTable: {RAPIDTABLE_AVAILABLE}, EasyOCR: {EASYOCR_AVAILABLE}, PaddleOCR: {PADDLEOCR_AVAILABLE}")
    
    # Process each image with optimized table recognition
    successful_rapidtable = 0
    successful_enhanced_hybrid = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Try RapidTable + Hybrid OCR
        if process_image_with_rapidtable_plus_hybrid_ocr(image_path, output_dir):
            successful_rapidtable += 1
        
        # Try Enhanced Hybrid approach
        if create_enhanced_hybrid_table_recognition(image_path, output_dir):
            successful_enhanced_hybrid += 1
        
        failed += 1  # Count attempts
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"RapidTable + Hybrid OCR successful: {successful_rapidtable}")
    logger.info(f"Enhanced Hybrid table recognition successful: {successful_enhanced_hybrid}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

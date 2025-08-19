#!/usr/bin/env python3
"""
Enhanced OmniParse processing script with RapidTable + Advanced OCR integration for optimal table recognition.
This script implements multiple strategies to maximize table recognition scores by improving OCR quality and cell mapping.
"""

import os
import sys
from pathlib import Path
import logging
from PIL import Image, ImageEnhance, ImageFilter
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

def preprocess_image_for_ocr(image):
    """
    Apply advanced image preprocessing to improve OCR accuracy.
    
    Args:
        image: PIL Image object
    
    Returns:
        PIL Image: Preprocessed image optimized for OCR
    """
    try:
        # Convert to numpy array for OpenCV operations
        img_array = np.array(image)
        
        # Convert to grayscale if it's RGB
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(cleaned)
        
        # Apply additional PIL enhancements
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(1.5)  # Increase contrast
        
        enhancer = ImageEnhance.Sharpness(processed_image)
        processed_image = enhancer.enhance(1.2)  # Slightly increase sharpness
        
        return processed_image
        
    except Exception as e:
        logger.warning(f"Error in image preprocessing: {str(e)}")
        return image

def extract_text_from_cell_region_advanced(image, bbox, ocr_readers):
    """
    Advanced text extraction from cell regions with multiple OCR strategies.
    
    Args:
        image: PIL Image or numpy array
        bbox: Bounding box coordinates [x1, y1, x2, y2, x3, y3, x4, y4]
        ocr_readers: List of OCR reader objects
    
    Returns:
        str: Best extracted text from the cell
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

def process_image_with_enhanced_rapidtable_v2(image_path, output_dir):
    """
    Process a single image with Enhanced RapidTable + Advanced OCR for optimal table recognition.
    
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
        
        logger.info(f"Processing {image_path} with Enhanced RapidTable + Advanced OCR...")
        
        # Initialize RapidTable
        rapid_table = RapidTable()
        
        # Load and preprocess image
        original_image = Image.open(image_path)
        preprocessed_image = preprocess_image_for_ocr(original_image)
        image_array = np.array(preprocessed_image)
        
        # Create input for RapidTable with configuration
        input_data = RapidTableInput(
            model_type=ModelType.PPSTRUCTURE_EN,
            engine_type=EngineType.ONNXRUNTIME,
            use_ocr=True
        )
        
        # Process the image with RapidTable
        rapid_table.cfg = input_data
        table_results = rapid_table.get_table_rec_results(image_array)
        
        # Initialize multiple OCR readers for redundancy
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
        
        # Extract table information with enhanced content
        markdown_content = f"# Image: {base_name}\n\n"
        markdown_content += "## Enhanced Table Recognition Results (RapidTable + Advanced OCR)\n\n"
        
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
                    
                    # Extract text for each cell with advanced OCR
                    table_content = []
                    for row in range(max_row + 1):
                        table_row = []
                        for col in range(max_col + 1):
                            if (row, col) in cell_grid:
                                bbox_start, bbox_end = cell_grid[(row, col)]
                                if bbox_start < len(bboxes) and bbox_end < len(bboxes):
                                    # Extract text from this cell using advanced OCR
                                    cell_text = extract_text_from_cell_region_advanced(
                                        preprocessed_image, 
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
                        markdown_content += "**Extracted Table Content (Advanced OCR):**\n\n"
                        
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
        output_filename = f"{base_name}_enhanced_rapidtable_v2.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {image_path} with Enhanced RapidTable v2: {str(e)}")
        return False

def create_hybrid_table_recognition(image_path, output_dir):
    """
    Create a hybrid approach combining multiple table recognition strategies.
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save the markdown output
    """
    try:
        # Get the base filename without extension
        base_name = Path(image_path).stem
        
        logger.info(f"Creating hybrid table recognition for {image_path}...")
        
        # Load and preprocess image
        original_image = Image.open(image_path)
        preprocessed_image = preprocess_image_for_ocr(original_image)
        
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
                text_results = ocr_readers["EasyOCR"].readtext(np.array(preprocessed_image))
                
                # Create a simple table structure based on text positioning
                markdown_content = f"# Image: {base_name}\n\n"
                markdown_content += "## Hybrid Table Recognition Results\n\n"
                
                if text_results:
                    markdown_content += "### Detected Text Elements\n\n"
                    
                    # Group text by approximate rows (y-coordinate clustering)
                    text_elements = []
                    for bbox, text, confidence in text_results:
                        if confidence > 0.3:  # Filter low confidence results
                            center_y = (bbox[0][1] + bbox[2][1]) / 2
                            text_elements.append({
                                'text': text.strip(),
                                'bbox': bbox,
                                'center_y': center_y,
                                'confidence': confidence
                            })
                    
                    # Sort by y-coordinate to group by rows
                    text_elements.sort(key=lambda x: x['center_y'])
                    
                    # Create a simple table structure
                    if text_elements:
                        markdown_content += "**Text-based Table Structure:**\n\n"
                        
                        # Group into approximate rows (within 20 pixels)
                        rows = []
                        current_row = []
                        last_y = None
                        
                        for elem in text_elements:
                            if last_y is None or abs(elem['center_y'] - last_y) < 20:
                                current_row.append(elem)
                            else:
                                if current_row:
                                    rows.append(current_row)
                                current_row = [elem]
                            last_y = elem['center_y']
                        
                        if current_row:
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
                        
                        # Add text element details
                        markdown_content += f"**Total text elements detected**: {len(text_elements)}\n\n"
                        markdown_content += "**High-confidence text elements**:\n"
                        high_conf_elements = [elem for elem in text_elements if elem['confidence'] > 0.7]
                        for i, elem in enumerate(high_conf_elements[:10]):
                            markdown_content += f"- \"{elem['text']}\" (confidence: {elem['confidence']:.2f})\n"
                        if len(high_conf_elements) > 10:
                            markdown_content += f"- ... and {len(high_conf_elements) - 10} more high-confidence elements\n"
                        
                        markdown_content += "\n"
                    else:
                        markdown_content += "No text elements detected with sufficient confidence.\n\n"
                else:
                    markdown_content += "No text detected in this image.\n\n"
                
                # Create output filename
                output_filename = f"{base_name}_hybrid_table.md"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save markdown content
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                logger.info(f"Successfully created hybrid table recognition for {image_path} -> {output_path}")
                return True
                
            except Exception as e:
                logger.warning(f"EasyOCR text extraction failed: {str(e)}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error in hybrid table recognition for {image_path}: {str(e)}")
        return False

def main():
    """Main function to process OmniDocBench demo images with enhanced table recognition."""
    
    # Define paths
    demo_images_dir = "demo_data/omnidocbench_demo/images"
    output_dir = "omniparse_enhanced_ocr_v2_results"
    
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
    
    # Process each image with enhanced table recognition
    successful_enhanced = 0
    successful_hybrid = 0
    failed = 0
    
    for image_file in image_files:
        image_path = str(image_file)
        
        # Try Enhanced RapidTable + Advanced OCR
        if process_image_with_enhanced_rapidtable_v2(image_path, output_dir):
            successful_enhanced += 1
        
        # Try Hybrid approach
        if create_hybrid_table_recognition(image_path, output_dir):
            successful_hybrid += 1
        
        failed += 1  # Count attempts
    
    # Summary
    logger.info(f"Processing complete!")
    logger.info(f"Enhanced RapidTable + Advanced OCR successful: {successful_enhanced}")
    logger.info(f"Hybrid table recognition successful: {successful_hybrid}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_dir}")
    
    # List generated files
    generated_files = list(Path(output_dir).glob("*.md"))
    logger.info(f"Generated {len(generated_files)} markdown files:")
    for file in generated_files:
        logger.info(f"  - {file.name}")

if __name__ == "__main__":
    main()

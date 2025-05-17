import torch
from PIL import Image, ImageEnhance, ImageFilter
import io
from pdf2image import convert_from_bytes
import logging
import pytesseract
from typing import Dict, Tuple, List, Optional
import json
from datetime import datetime
import re
import numpy as np
import os
import platform
from pathlib import Path
import fitz  # PyMuPDF
import cv2
from ..utils.ai import get_gpt_classification, get_gpt_extraction
from math import degrees
from skimage.filters import threshold_sauvola

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self._setup_tesseract()
        self._setup_templates()
        
    def _setup_tesseract(self):
        """Configure Tesseract based on the operating system"""
        system = platform.system().lower()
        if system == 'windows':
            tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            else:
                logger.warning("Tesseract not found in default Windows location. Please ensure it's installed and in PATH")
        elif system == 'linux':
            # On Linux, Tesseract is usually in PATH
            if not self._check_tesseract_installed():
                logger.warning("Tesseract not found. Please install tesseract-ocr package")
                
    def _check_tesseract_installed(self) -> bool:
        """Check if Tesseract is installed and accessible"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.error(f"Error checking Tesseract installation: {e}")
            return False

    def _setup_templates(self):
        """Setup field templates for different document types"""
        self.field_templates = {
            'drivers_license': [
                'license_number',
                'name',
                'date_of_birth',
                'expiration_date',
                'address',
                'sex',
                'height',
                'eyes',
                'restrictions',
                'endorsements'
            ],
            'passport': [
                'passport_number',
                'surname',
                'given_names',
                'nationality',
                'date_of_birth',
                'place_of_birth',
                'date_of_issue',
                'date_of_expiry'
            ],
            'ead': [
                'card_number',
                'name',
                'date_of_birth',
                'category',
                'valid_from',
                'expires',
                'alien_number'
            ]
        }

    def _convert_pdf_to_image(self, pdf_bytes):
        """Convert first page of PDF to image"""
        try:
            logger.debug("Converting PDF to image...")
            try:
                images = convert_from_bytes(
                    pdf_bytes,
                    dpi=300,  # Higher DPI for better quality
                    fmt='PNG',  # Use PNG format for better quality
                    grayscale=False,  # Keep color for better OCR
                    size=(2000, None)  # Set width to 2000px, maintain aspect ratio
                )
                if images:
                    logger.debug(f"Successfully converted PDF to {len(images)} images")
                    return images[0]
                else:
                    logger.error("PDF conversion produced no images")
                    raise ValueError("PDF conversion produced no images")
            except Exception as pdf_error:
                logger.error(f"PDF conversion failed: {str(pdf_error)}")
                raise ValueError(f"Failed to convert PDF: {str(pdf_error)}")
        except Exception as e:
            logger.error(f"Error converting PDF to image: {str(e)}")
            raise ValueError("The PDF file appears to be malformed or corrupted. Please try uploading a different file.")

    def _detect_dpi(self, image: np.ndarray) -> int:
        """Detect optimal DPI based on image size and content"""
        # Calculate average text height using edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            heights = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                heights.append(abs(y2 - y1))
            avg_height = np.mean(heights) if heights else 20
            
            # Estimate DPI based on average text height
            # Assuming ideal text height is ~20 pixels at 300 DPI
            estimated_dpi = int((300 * avg_height) / 20)
            return max(min(estimated_dpi, 600), 200)  # Clamp between 200 and 600
        return 300  # Default DPI if no lines detected

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Deskew image using Hough Line Transform"""
        try:
            # Convert to grayscale if needed
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Get edges
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Use probabilistic Hough Transform
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return image
            
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 != 0:  # Avoid division by zero
                    angle = degrees(np.arctan2(y2 - y1, x2 - x1))
                    # Only consider angles that are almost horizontal
                    if abs(angle) < 20:
                        angles.append(angle)
            
            if not angles:
                return image
            
            # Get median angle to avoid outliers
            median_angle = np.median(angles)
            
            # Rotate image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return rotated
        except Exception as e:
            logger.error(f"Error in deskewing: {str(e)}")
            return image

    def _enhance_image(self, image: Image.Image) -> List[Image.Image]:
        """Enhance image for better OCR results"""
        try:
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL to OpenCV format
            cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect DPI and resize if needed
            detected_dpi = self._detect_dpi(cv_img)
            scale_factor = detected_dpi / 300.0  # Normalize to 300 DPI
            if scale_factor != 1.0:
                cv_img = cv2.resize(cv_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            
            # Deskew image
            cv_img = self._deskew_image(cv_img)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            
            # Apply multiple preprocessing techniques
            preprocessed_images = []
            
            # Technique 1: CLAHE + Denoising
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            clahe_img = clahe.apply(gray)
            denoised1 = cv2.fastNlMeansDenoising(clahe_img, None, 10, 7, 21)
            preprocessed_images.append(Image.fromarray(denoised1))
            
            # Technique 2: Bilateral Filter + Sharpening
            bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(bilateral, -1, kernel)
            preprocessed_images.append(Image.fromarray(sharpened))
            
            # Technique 3: Adaptive Thresholding
            blurred = cv2.GaussianBlur(gray, (3,3), 0)
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 15, 8
            )
            preprocessed_images.append(Image.fromarray(thresh))
            
            # Process each enhanced image
            enhanced_images = []
            for idx, proc_img in enumerate(preprocessed_images):
                # Convert to RGB for consistency
                if proc_img.mode != 'RGB':
                    proc_img = proc_img.convert('RGB')
                
                # Additional PIL enhancements for non-binary images
                if idx != 2:  # Skip for binary threshold images
                    enhancer = ImageEnhance.Contrast(proc_img)
                    proc_img = enhancer.enhance(1.5)
                    
                    enhancer = ImageEnhance.Sharpness(proc_img)
                    proc_img = enhancer.enhance(1.5)
                
                enhanced_images.append(proc_img)
            
            # Add the original image as a fallback
            if image.mode != 'RGB':
                image = image.convert('RGB')
            enhanced_images.append(image)
            
            return enhanced_images
            
        except Exception as e:
            logger.error(f"Error enhancing image: {str(e)}")
            # Return original image in RGB mode as fallback
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return [image]

    def _extract_text(self, image: Image.Image) -> str:
        """Extract text from image using OCR with improved accuracy"""
        try:
            logger.debug("Extracting text using OCR...")
            
            # Get enhanced versions of the image
            enhanced_images = self._enhance_image(image)
            
            best_text = ""
            best_confidence = 0
            
            # Try different Tesseract configurations
            configs = [
                r'--oem 3 --psm 6 -l eng --dpi 300 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-./\' ',
                r'--oem 3 --psm 11 -l eng --dpi 300',  # Sparse text with OEM 3
                r'--oem 1 --psm 6 -l eng --dpi 300'    # Legacy engine with PSM 6
            ]
            
            for enhanced_img in enhanced_images:
                # Ensure we're working with a PIL Image
                if isinstance(enhanced_img, np.ndarray):
                    enhanced_img = Image.fromarray(enhanced_img)
                
                # Convert to RGB if not already
                if enhanced_img.mode != 'RGB':
                    enhanced_img = enhanced_img.convert('RGB')
                
                for config in configs:
                    try:
                        # Get both regular text and data with confidence scores
                        text = pytesseract.image_to_string(enhanced_img, config=config)
                        data = pytesseract.image_to_data(enhanced_img, config=config, output_type=pytesseract.Output.DICT)
                        
                        # Process structured data with improved confidence handling
                        conf_threshold = 40  # Increased confidence threshold
                        word_positions = []
                        
                        # First pass: collect high-confidence words
                        for i in range(len(data['text'])):
                            if int(data['conf'][i]) > conf_threshold:
                                word = data['text'][i].strip()
                                if word:
                                    # Keep more special characters that are important for fields
                                    word = re.sub(r'[^\w\s\-\.,/#\'"]', '', word)
                                    
                                    # Store word with its position and confidence
                                    word_positions.append({
                                        'text': word,
                                        'left': data['left'][i],
                                        'top': data['top'][i],
                                        'width': data['width'][i],
                                        'height': data['height'][i],
                                        'conf': data['conf'][i]
                                    })
                        
                        if not word_positions:
                            continue
                            
                        # Sort words by vertical position (top to bottom)
                        word_positions.sort(key=lambda x: x['top'])
                        
                        # Group words into lines with improved positioning logic
                        current_line = []
                        current_top = None
                        lines = []
                        line_height_threshold = 12  # Adjusted for typical ID card text
                        
                        for pos in word_positions:
                            if current_top is None:
                                current_top = pos['top']
                            
                            # If word is on the same line (using dynamic threshold based on text height)
                            if abs(pos['top'] - current_top) <= max(line_height_threshold, pos['height'] * 0.5):
                                current_line.append(pos)
                            else:
                                if current_line:
                                    # Sort words in current line by horizontal position
                                    current_line.sort(key=lambda x: x['left'])
                                    
                                    # Join words with appropriate spacing
                                    line_text = ''
                                    prev_end = 0
                                    for w in current_line:
                                        # Add space if there's a gap
                                        if prev_end > 0 and (w['left'] - prev_end) > w['height']:
                                            line_text += ' '
                                        line_text += w['text']
                                        prev_end = w['left'] + w['width']
                                    
                                    lines.append(line_text)
                                
                                current_line = [pos]
                                current_top = pos['top']
                        
                        # Add last line
                        if current_line:
                            current_line.sort(key=lambda x: x['left'])
                            line_text = ' '.join(w['text'] for w in current_line)
                            lines.append(line_text)
                        
                        # Combine lines with newlines to preserve layout
                        current_text = '\n'.join(lines)
                        
                        # Clean up the text while preserving important patterns
                        current_text = re.sub(r'\s+', ' ', current_text)  # Normalize whitespace
                        current_text = re.sub(r'[^\w\s\-\.,/#\'"]', '', current_text)  # Remove special chars but keep important ones
                        
                        # Calculate confidence score
                        current_confidence = self._calculate_text_confidence(current_text)
                        
                        if current_confidence > best_confidence:
                            best_confidence = current_confidence
                            best_text = current_text
                            
                    except Exception as e:
                        logger.warning(f"OCR attempt failed with config {config}: {str(e)}")
                        continue
            
            if not best_text:
                raise ValueError("Could not extract readable text from any preprocessing method")
            
            logger.debug(f"Best OCR confidence score: {best_confidence}")
            logger.debug(f"Extracted text sample: {best_text[:200]}")
            
            return best_text
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            raise

    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate a confidence score for the extracted text based on expected patterns"""
        confidence = 0.0
        
        # Check for expected document patterns (any state)
        if any(pattern in text.upper() for pattern in ['LICENSE', 'DRIVER', 'IDENTIFICATION', 'ID CARD']):
            confidence += 0.3
            
        # Check for date patterns (MM/DD/YYYY or similar)
        if len(re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)) >= 2:  # At least 2 dates (DOB and EXP)
            confidence += 0.2
            
        # Check for name patterns (uppercase words)
        if re.search(r'[A-Z]{2,}(\s+[A-Z]{1,2}\.?\s+)?[A-Z]{2,}', text):  # Matches names with optional middle initial
            confidence += 0.2
            
        # Check for address patterns (numbers followed by text and state code)
        if re.search(r'\d+\s+[A-Za-z\s]+(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)', text):
            confidence += 0.2
            
        # Check for ID number patterns (mix of letters and numbers)
        if re.search(r'[A-Z0-9]{6,}', text):
            confidence += 0.1
            
        # Check for physical descriptors (height, weight, eyes)
        if re.search(r'(HGT|HEIGHT|WT|WEIGHT|EYES|EYE)', text.upper()):
            confidence += 0.1
            
        return min(confidence, 1.0)

    def process_image(self, file_contents: bytes):
        """Process either a PDF or image file"""
        try:
            # Try to open as image first
            try:
                logger.debug("Attempting to open file as image...")
                image = Image.open(io.BytesIO(file_contents))
                logger.debug("Successfully opened as image")
            except Exception as e:
                logger.debug(f"Could not open as image: {str(e)}")
                # If not an image, try as PDF
                logger.debug("Attempting to convert PDF to image...")
                try:
                    image = self._convert_pdf_to_image(file_contents)
                    if not image:
                        raise ValueError("Failed to process document")
                except Exception as pdf_error:
                    logger.error(f"PDF processing failed: {str(pdf_error)}")
                    raise ValueError("Failed to process document. Please ensure it's a valid PDF or image file.")

            # Validate image size and quality
            min_width = 400  # Reduced from 800
            min_height = 300  # Reduced from 600
            
            if image.size[0] < min_width or image.size[1] < min_height:
                logger.warning(f"Image resolution is low ({image.size[0]}x{image.size[1]}). Attempting to upscale...")
                # Calculate scaling factor to reach minimum dimensions
                scale_x = min_width / image.size[0]
                scale_y = min_height / image.size[1]
                scale = max(scale_x, scale_y)
                
                # Convert to OpenCV format for better upscaling
                cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Use LANCZOS4 for better quality upscaling
                new_width = int(image.size[0] * scale)
                new_height = int(image.size[1] * scale)
                cv_img = cv2.resize(cv_img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                
                # Convert back to PIL
                image = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                logger.info(f"Image upscaled to {new_width}x{new_height}")

            # Extract text using OCR with multiple attempts if needed
            text = None
            best_confidence = 0
            best_text = None

            # Try different preprocessing combinations
            preprocessing_configs = [
                {'contrast': 1.5, 'sharpen': 1.5, 'denoise': True},
                {'contrast': 2.0, 'sharpen': 1.2, 'denoise': True},
                {'contrast': 1.2, 'sharpen': 1.8, 'denoise': False}
            ]

            for config in preprocessing_configs:
                try:
                    # Apply current preprocessing config
                    processed_image = self._enhance_image(image)
                    
                    # Extract text
                    current_text = self._extract_text(processed_image)
                    
                    # Calculate confidence score based on key patterns
                    confidence = self._calculate_text_confidence(current_text)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_text = current_text
                        
                except Exception as e:
                    logger.warning(f"OCR attempt failed with config {config}: {str(e)}")
                    continue

            if not best_text:
                raise ValueError("Failed to extract readable text from the document")

            text = best_text
            
            # Validate OCR quality
            if len(text.strip()) < 50:  # Arbitrary minimum length for a valid ID
                raise ValueError("Not enough text was extracted. Please provide a clearer image.")

            # Check for key patterns that should be present in any ID
            if not any(pattern in text.upper() for pattern in ['LICENSE', 'ID', 'CARD', 'PASSPORT']):
                logger.warning("No standard ID document patterns found in text")

            # Classify document
            doc_type, confidence = get_gpt_classification(text)
            logger.debug(f"Classified as: {doc_type} with confidence: {confidence}")

            # Validate classification confidence
            if confidence < 0.7:  # Minimum confidence threshold
                logger.warning(f"Low classification confidence: {confidence}")
                # Continue but log the warning

            # Get fields for document type
            fields = self.field_templates.get(doc_type, [])
            if not fields:
                raise ValueError(f"Unsupported document type: {doc_type}")

            # Extract fields
            extracted_dict = get_gpt_extraction(text, doc_type, fields)
            
            # Validate extraction results
            not_found_count = sum(1 for v in extracted_dict.values() if v == "NOT_FOUND")
            if not_found_count > len(fields) * 0.7:  # If more than 70% of fields are NOT_FOUND
                logger.error("Too many fields could not be extracted")
                raise ValueError("Could not extract most fields. Please provide a clearer image.")

            # Convert dictionary to list of Field objects with validation
            extracted_fields = []
            for field_name in fields:
                field_value = extracted_dict.get(field_name, "NOT_FOUND")
                
                # Remove any prefix if present
                if field_name.startswith("- "):
                    field_name = field_name[2:]
                
                # Validate specific fields
                if field_value != "NOT_FOUND":
                    field_value = self._validate_field(field_name, field_value)
                
                extracted_fields.append({
                    "field_name": field_name,
                    "field_value": field_value,
                    "corrected": False
                })

            return doc_type, extracted_fields

        except Exception as e:
            logger.error(f"Error in process_image: {str(e)}", exc_info=True)
            raise ValueError(str(e))

    def _validate_field(self, field_name: str, value: str) -> str:
        """Validate and clean specific field values"""
        field_name = field_name.lower()
        
        if 'date' in field_name:
            # Validate date format
            try:
                # Try to parse the date
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', value)
                if date_match:
                    month, day, year = map(int, date_match.groups())
                    # Add century if needed
                    if year < 100:
                        year += 2000 if year < 30 else 1900
                    # Format consistently
                    return f"{month:02d}/{day:02d}/{year}"
                return "NOT_FOUND"
            except:
                return "NOT_FOUND"
                
        elif 'name' in field_name:
            # Validate name format
            if not re.match(r'^[A-Z\s]+$', value):
                return "NOT_FOUND"
            return value
            
        elif field_name == 'sex':
            # Validate sex field
            value = value.upper()
            if value not in ['M', 'F']:
                return "NOT_FOUND"
            return value
            
        elif 'height' in field_name:
            # Validate height format
            if not re.match(r"^\d'?\d{1,2}\"?$", value):
                return "NOT_FOUND"
            return value
            
        elif 'eyes' in field_name:
            # Validate eye color code
            if not re.match(r'^(BLU|BRO|GRN|HAZ|BLK)$', value.upper()):
                return "NOT_FOUND"
            return value.upper()
            
        elif 'license' in field_name and 'number' in field_name:
            # Validate license number format
            if not re.match(r'^[A-Z]{1,5}\d{5,8}[A-Z]{1,2}$', value):
                return "NOT_FOUND"
            return value
            
        return value 
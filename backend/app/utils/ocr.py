import pytesseract
from PIL import Image
import pdf2image
import os
from typing import List, Union, Dict, Tuple, Optional
import tempfile
from io import BytesIO
import logging
import re
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using OCR with improved accuracy"""
    try:
        # Read image
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for OpenCV
        img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Resize if too large
        max_width = 2000
        if img_array.shape[1] > max_width:
            scale = max_width / img_array.shape[1]
            img_array = cv2.resize(img_array, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        
        # Create multiple preprocessed versions
        preprocessed_images = []
        
        # Version 1: Basic preprocessing
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        preprocessed_images.append(gray)
        
        # Version 2: Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        preprocessed_images.append(thresh)
        
        # Version 3: Otsu's thresholding
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed_images.append(otsu)
        
        # Version 4: Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        preprocessed_images.append(enhanced)
        
        # Try different OCR configurations
        best_text = ""
        best_confidence = 0
        
        configs = [
            '--oem 3 --psm 6 -l eng',  # Default
            '--oem 3 --psm 3 -l eng',  # Full page
            '--oem 3 --psm 11 -l eng', # Sparse text
            '--oem 3 --psm 4 -l eng'   # Assume single column of text
        ]
        
        for img in preprocessed_images:
            # Convert back to PIL Image
            pil_img = Image.fromarray(img)
            
            for config in configs:
                try:
                    # Get OCR data
                    data = pytesseract.image_to_data(
                        pil_img, config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Calculate confidence
                    conf_values = [c for c in data['conf'] if c > 0]
                    avg_conf = sum(conf_values) / len(conf_values) if conf_values else 0
                    
                    # Get text
                    text = pytesseract.image_to_string(pil_img, config=config)
                    
                    # Keep best result
                    if avg_conf > best_confidence:
                        best_confidence = avg_conf
                        best_text = text
                except Exception as e:
                    logger.warning(f"OCR attempt failed: {e}")
                    continue
        
        logger.debug(f"Best OCR confidence: {best_confidence}")
        return best_text.strip()
        
    except Exception as e:
        logger.error(f"Error in OCR text extraction: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extract text from each page of a PDF file"""
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # Extract text from each page
        texts = []
        for image in images:
            text = pytesseract.image_to_string(image)
            texts.append(text)
            
        return texts
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text(file_path: str) -> Union[str, List[str]]:
    """Extract text from either an image or PDF file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    elif file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

def save_upload_file(file_data: bytes, filename: str) -> str:
    """Save an uploaded file to a temporary location"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
        
    return file_path

def clean_ocr_text(text: str) -> str:
    """Clean up OCR output text"""
    if not text:
        return text
        
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove common OCR artifacts
    text = text.replace('|', 'I')
    text = text.replace('¢', 'C')
    text = text.replace('°', '0')
    text = text.replace('®', 'R')
    text = text.replace('§', 'S')
    text = text.replace('¥', 'Y')
    text = text.replace('€', 'E')
    text = text.replace('£', 'E')
    text = text.replace('¢', 'c')
    
    # Fix common OCR errors
    text = text.replace('l.', 'I.')
    text = text.replace('l,', 'I,')
    text = text.replace('l:', 'I:')
    text = text.replace('l;', 'I;')
    text = text.replace('l-', 'I-')
    text = text.replace('l/', 'I/')
    
    # Remove non-alphanumeric characters except common punctuation
    text = re.sub(r'[^A-Za-z0-9\s\-\.,/#\'"]', '', text)
    
    return text

def validate_ocr_output(text: str, confidence: float, doc_type: Optional[str] = None) -> Optional[str]:
    """
    Validate OCR output with enhanced checks and return error message if invalid
    """
    if not text or len(text.strip()) < 50:
        return "OCR output too short, please upload a clearer scan"
        
    if confidence < 30:  # 30% confidence threshold
        return "OCR confidence too low, please upload a clearer scan"
        
    # Document type specific validation
    if doc_type == "drivers_license":
        key_terms = ['LICENSE', 'DL', 'DRIVER', 'CLASS', 'REST', 'END', 'EXP']
        required_count = 2  # Must find at least 2 key terms
    elif doc_type == "passport":
        key_terms = ['PASSPORT', 'NATIONALITY', 'BIRTH', 'EXPIRY', 'AUTHORITY']
        required_count = 2
    elif doc_type == "ead":
        key_terms = ['EMPLOYMENT', 'AUTHORIZATION', 'USCIS', 'CARD', 'VALID']
        required_count = 2
    else:
        # Generic ID document validation
        key_terms = ['DOB', 'LIC', 'ID', 'DL', 'LICENSE', 'CARD', 'PASSPORT', 'EAD']
        required_count = 1
        
    found_terms = sum(1 for term in key_terms if term in text.upper())
    if found_terms < required_count:
        return f"Could not detect enough document markers (found {found_terms}/{required_count}), please upload a valid ID document"
        
    # Check for common error patterns
    error_patterns = [
        (r'[^A-Za-z0-9\s\-\.,/#\'"\(\)]+', 'Contains too many special characters'),
        (r'(.)\1{5,}', 'Contains repeated character patterns'),
        (r'\d{10,}', 'Contains unusually long number sequences')
    ]
    
    for pattern, message in error_patterns:
        if re.search(pattern, text):
            return f"OCR quality issue: {message}"
            
    return None  # Validation passed 
import pytesseract
from PIL import Image
import pdf2image
import os
from typing import List, Union
import tempfile

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")

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
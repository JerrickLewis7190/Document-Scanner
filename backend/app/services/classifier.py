from typing import Tuple
import pytesseract
from PIL import Image
import os
from ..utils.ai import get_gpt_classification

class DocumentClassifier:
    SUPPORTED_TYPES = ["passport", "drivers_license", "ead_card"]
    
    @staticmethod
    def classify_document(image_path: str) -> Tuple[str, float]:
        """
        Classify the document type using OCR and GPT-4.
        Returns tuple of (document_type, confidence)
        """
        # Extract text using OCR
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")

        # Use GPT to classify the document
        doc_type, confidence = get_gpt_classification(text)
        
        if doc_type.lower() not in DocumentClassifier.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported document type: {doc_type}")
            
        return doc_type.lower(), confidence

    @staticmethod
    def validate_document_type(doc_type: str) -> bool:
        """Validate if the document type is supported"""
        return doc_type.lower() in DocumentClassifier.SUPPORTED_TYPES 
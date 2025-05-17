import io
import tempfile
import os
import logging
import re
from typing import Dict, Tuple, List, Optional
from PIL import Image
from pdf2image import convert_from_bytes
from ..utils.ai import get_gpt_classification, get_gpt_extraction
from ..preprocess_image import preprocess_image
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self._setup_templates()
        
    def _setup_templates(self):
        """Setup field templates for different document types"""
        self.field_templates = {
            'drivers_license': {
                'fields': [
                    'license_number',
                    'first_name',
                    'middle_initial',
                    'last_name',
                    'date_of_birth',
                    'issue_date',
                    'expiration_date',
                    'address',
                    'sex',
                    'height',
                    'weight',
                    'eyes',
                    'restrictions',
                    'endorsements',
                    'donor',
                    'document_type',
                    'revision_date'
                ]
            },
            'passport': {
                'fields': [
                    'passport_number',
                    'surname',
                    'given_names',
                    'nationality',
                    'date_of_birth',
                    'place_of_birth',
                    'date_of_issue',
                    'date_of_expiry',
                    'authority',
                    'sex',
                    'document_type'
                ]
            },
            'ead': {
                'fields': [
                    'card_number',
                    'first_name',
                    'last_name',
                    'date_of_birth',
                    'category',
                    'valid_from',
                    'expires',
                    'alien_number',
                    'document_type'
                ]
            }
        }

    @staticmethod
    def normalize_date(date_str):
        # Try to match formats like 15JAN1985, 01FEB2020, etc.
        match = re.match(r'^(\d{2})([A-Z]{3})(\d{4})$', date_str)
        if match:
            day, month_abbr, year = match.groups()
            try:
                # Convert month abbreviation to title case for strptime
                date_obj = datetime.strptime(f'{day} {month_abbr.title()} {year}', '%d %b %Y')
                return date_obj.strftime('%d %b %Y')
            except Exception:
                pass
        # If already in a good format or can't parse, return as is
        return date_str

    def _convert_pdf_to_image(self, pdf_bytes: bytes) -> Tuple[bytes, Optional[str]]:
        """Convert first page of PDF to image bytes"""
        try:
            logger.debug("Converting PDF to image...")
            try:
                # Use higher DPI for better quality
                images = convert_from_bytes(
                    pdf_bytes,
                    dpi=300,
                    fmt='PNG',
                    grayscale=False,
                    size=(2000, None)  # Set width to 2000px, maintain aspect ratio
                )
                if images:
                    logger.debug(f"Successfully converted PDF to {len(images)} images")
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    images[0].save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue(), None
                else:
                    error_msg = "PDF conversion produced no images"
                    logger.error(error_msg)
                    return None, error_msg
            except Exception as pdf_error:
                error_msg = f"Failed to convert PDF: {str(pdf_error)}"
                logger.error(error_msg)
                return None, error_msg
        except Exception as e:
            error_msg = "The PDF file appears to be malformed or corrupted."
            logger.error(f"Error converting PDF to image: {str(e)}")
            return None, error_msg

    def process_image(self, file_contents: bytes) -> Tuple[str, List[Dict[str, str]], Optional[str]]:
        """
        Process either a PDF or image file using GPT-4 Vision.
        Returns (doc_type, extracted_fields, error_message)
        """
        temp_file_path = None
        preprocessed_path = None
        try:
            # Save bytes to temporary file for GPT Vision
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(file_contents)
                temp_file_path = temp_file.name

            # Preprocess the image (skip if PDF)
            # Check if the file is a PDF by magic number
            is_pdf = file_contents.startswith(b'%PDF')
            image_path_to_use = temp_file_path
            if not is_pdf:
                preprocessed_path = preprocess_image(temp_file_path)
                image_path_to_use = preprocessed_path

            # Define fields to extract based on document type
            common_fields = [
                "document_type",
                "first_name",
                "last_name",
                "date_of_birth",
                "expiration_date",
                "address",
                "sex",
                "document_number",
                "nationality"
            ]

            # Extract fields using GPT-4 Vision
            extracted_data = get_gpt_extraction(image_path_to_use, "UNKNOWN", common_fields)
            
            if not extracted_data:
                return "unknown", [], "Failed to extract data from document"

            # Determine document type from extracted data
            doc_type = extracted_data.get("document_type", "UNKNOWN").upper()
            if "LICENSE" in doc_type:
                doc_type = "drivers_license"
            elif "PASSPORT" in doc_type:
                doc_type = "passport"
            elif "EAD" in doc_type or "AUTHORIZATION" in doc_type:
                doc_type = "ead_card"
            else:
                doc_type = "unknown"

            # Format extracted fields for database
            formatted_fields = []
            critical_fields_missing = False
            date_fields = [
                "date_of_birth", "expiration_date", "issue_date", "date_of_issue", "date_of_expiry", "valid_from", "expires"
            ]
            for field_name, field_value in extracted_data.items():
                # Check if critical fields are missing
                if field_name in ["first_name", "last_name", "date_of_birth", "document_number"]:
                    if field_value == "NOT_FOUND":
                        critical_fields_missing = True
                # Only normalize date fields, never document_number or its aliases
                if field_name in date_fields and field_value not in ("NOT_FOUND", None, ""):
                    field_value = self.normalize_date(field_value)
                formatted_fields.append({
                    "field_name": field_name,
                    "field_value": field_value if field_value else "NOT_FOUND"
                })

            error_msg = "Critical fields missing - manual review required" if critical_fields_missing else None
            return doc_type, formatted_fields, error_msg

        except Exception as e:
            logger.error(f"Error in process_image: {str(e)}", exc_info=True)
            return "unknown", [], str(e)
        finally:
            # Clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")
            if preprocessed_path and os.path.exists(preprocessed_path):
                try:
                    os.unlink(preprocessed_path)
                except Exception as e:
                    logger.warning(f"Failed to delete preprocessed file {preprocessed_path}: {str(e)}")

    def _is_pdf(self, file_contents: bytes) -> bool:
        """Check if file contents are PDF"""
        return file_contents.startswith(b'%PDF') 
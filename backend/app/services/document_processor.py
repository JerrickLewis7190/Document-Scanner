import io
import tempfile
import os
import logging
import re
from typing import Dict, Tuple, List, Optional
from PIL import Image
from ..utils.pdf_processor import convert_pdf_bytes_to_image
from ..utils.ai import get_gpt_classification, get_gpt_extraction, check_image_quality
from ..utils.field_mapping import standardize_field_names, validate_required_fields, get_essential_fields, REQUIRED_FIELDS
from ..preprocess_image import preprocess_image
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self._setup_templates()
        
    def _setup_templates(self):
        """Setup field templates for different document types"""
        # Define comprehensive field lists for each document type
        self.field_templates = {
            'drivers_license': {
                'fields': [
                    'license_number',
                    'first_name',
                    'last_name',
                    'date_of_birth',
                    'issue_date',
                    'expiration_date',
                    'document_type'
                ]
            },
            'passport': {
                'fields': [
                    'document_number',
                    'passport_number',
                    'full_name', 
                    'surname',
                    'given_names',
                    'nationality',
                    'country',
                    'date_of_birth',
                    'place_of_birth',
                    'date_of_issue',
                    'issue_date',
                    'date_of_expiry',
                    'expiration_date',
                    'authority',
                    'sex',
                    'document_type'
                ]
            },
            'ead_card': {
                'fields': [
                    'card_number',
                    'first_name',
                    'last_name',
                    'category',
                    'card_expires_date',
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
        """Convert first page of PDF to image bytes using pikepdf"""
        try:
            logger.debug("Converting PDF to image with pikepdf...")
            return convert_pdf_bytes_to_image(pdf_bytes)
        except Exception as e:
            error_msg = f"Error converting PDF to image: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def process_image(self, file_contents: bytes) -> Tuple[str, List[Dict[str, str]], Optional[str]]:
        """
        Process either a PDF or image file using GPT-4 Vision.
        Returns (doc_type, extracted_fields, error_message)
        """
        temp_file_path = None
        preprocessed_path = None
        try:
            # Check if file is a PDF and convert if needed
            is_pdf = self._is_pdf(file_contents)
            if is_pdf:
                logger.debug("Detected PDF file, converting to image")
                file_contents, error = self._convert_pdf_to_image(file_contents)
                if error:
                    logger.error(f"Failed to convert PDF: {error}")
                    return "unknown", [], f"Failed to convert PDF: {error}"
                if not file_contents:
                    logger.error("PDF conversion returned empty result")
                    return "unknown", [], "PDF conversion failed"

            # Save bytes to temporary file for GPT Vision
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(file_contents)
                temp_file_path = temp_file.name

            # Preprocess the image (only needed for non-PDF original images)
            image_path_to_use = temp_file_path
            if not is_pdf:
                preprocessed_path = preprocess_image(temp_file_path)
                image_path_to_use = preprocessed_path

            # Check image quality before processing
            is_valid, quality_error = check_image_quality(image_path_to_use)
            if not is_valid:
                logger.error(f"Image quality check failed: {quality_error}")
                return "unknown", [], quality_error

            # Define base fields to extract for initial document type detection
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

            # First pass: Extract basic fields to determine document type
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
                
            # Get the essential fields for this document type
            essential_fields = get_essential_fields(doc_type)
            
            # If we have a known document type, perform a second pass with document-specific fields
            if doc_type != "unknown" and doc_type in self.field_templates:
                # Get all potential fields for this document type
                all_doc_fields = self.field_templates[doc_type]['fields']
                
                # Second pass: Extract with document-specific prompt and fields
                second_pass_data = get_gpt_extraction(image_path_to_use, doc_type, all_doc_fields)
                
                if second_pass_data:
                    # Merge the two extraction results, preferring second_pass_data
                    for field, value in second_pass_data.items():
                        extracted_data[field] = value
            
            # Standardize field names based on aliases
            standardized_data = standardize_field_names(extracted_data, doc_type)
            
            # Validate required fields
            is_valid, missing_fields = validate_required_fields(standardized_data, doc_type)
            critical_fields_missing = not is_valid
            
            # Format extracted fields for database
            formatted_fields = []
            date_fields = [
                "date_of_birth", "expiration_date", "issue_date", "date_of_issue", 
                "date_of_expiry", "valid_from", "expires", "card_expires_date"
            ]
            
            # Process all fields from standardized data
            for field_name, field_value in standardized_data.items():
                # Skip empty values
                if field_value is None:
                    field_value = "NOT_FOUND"
                
                # Normalize date fields only
                if field_name in date_fields and field_value not in ("NOT_FOUND", None, ""):
                    field_value = self.normalize_date(field_value)
                
                # Determine if this is a required field for the document type
                is_required = False
                if doc_type in REQUIRED_FIELDS:
                    is_required = field_name in REQUIRED_FIELDS[doc_type]
                
                formatted_fields.append({
                    "field_name": field_name,
                    "field_value": field_value if field_value else "NOT_FOUND",
                    "needs_correction": field_value == "NOT_FOUND" and is_required,
                    "confidence_score": 0.8 if field_value != "NOT_FOUND" else 0.0,
                    "error_message": "Field is required" if field_value == "NOT_FOUND" and is_required else None
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
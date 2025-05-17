from typing import List, Dict, Tuple
from ..models.schemas import ExtractedFieldBase
from ..utils.ai import get_gpt_extraction
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FieldExtractor:
    FIELD_MAPPINGS = {
        "passport": [
            "passport_number",
            "full_name",
            "date_of_birth",
            "nationality",
            "expiration_date",
            "issue_date"
        ],
        "drivers_license": [
            "license_number",
            "full_name",
            "date_of_birth",
            "address",
            "expiration_date",
            "issue_date",
            "class"
        ],
        "ead_card": [
            "uscis_number",
            "full_name",
            "date_of_birth",
            "category",
            "expiration_date",
            "card_number"
        ]
    }

    FIELD_VALIDATION_RULES = {
        "passport_number": {
            "pattern": r"^[A-Z0-9]{6,9}$",
            "description": "6-9 alphanumeric characters"
        },
        "license_number": {
            "pattern": r"^[A-Z0-9-]{1,20}$",
            "description": "Alphanumeric with optional hyphens"
        },
        "full_name": {
            "pattern": r"^[A-Za-z\s\-'\.]{2,50}$",
            "description": "2-50 characters, letters and basic punctuation"
        },
        "date_of_birth": {
            "pattern": r"^\d{2}[/-]\d{2}[/-]\d{4}$",
            "description": "MM/DD/YYYY or MM-DD-YYYY format"
        },
        "expiration_date": {
            "pattern": r"^\d{2}[/-]\d{2}[/-]\d{4}$",
            "description": "MM/DD/YYYY or MM-DD-YYYY format"
        },
        "issue_date": {
            "pattern": r"^\d{2}[/-]\d{2}[/-]\d{4}$",
            "description": "MM/DD/YYYY or MM-DD-YYYY format"
        },
        "address": {
            "pattern": r"^[A-Za-z0-9\s\-\.,#]{5,100}$",
            "description": "5-100 characters, alphanumeric with basic punctuation"
        },
        "nationality": {
            "pattern": r"^[A-Z]{2,3}$",
            "description": "2-3 letter country code"
        },
        "class": {
            "pattern": r"^[A-Z0-9-]{1,5}$",
            "description": "1-5 characters, letters and numbers"
        },
        "uscis_number": {
            "pattern": r"^[A-Z0-9]{8,9}$",
            "description": "8-9 alphanumeric characters"
        },
        "category": {
            "pattern": r"^[A-Z]\d{2}$",
            "description": "One letter followed by two digits"
        },
        "card_number": {
            "pattern": r"^[A-Z0-9]{13}$",
            "description": "13 alphanumeric characters"
        }
    }

    @staticmethod
    def _validate_date(date_str: str) -> bool:
        """Validate if a string is a valid date"""
        try:
            # Try both date formats
            for fmt in ['%m/%d/%Y', '%m-%d-%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    # Check if date is reasonable (not in future, not too old)
                    now = datetime.now()
                    hundred_years_ago = now.replace(year=now.year - 100)
                    return hundred_years_ago <= date_obj <= now
                except ValueError:
                    continue
            return False
        except Exception:
            return False

    @staticmethod
    def _validate_field_value(field_name: str, value: str) -> Tuple[bool, float]:
        """Validate a field value and return validation status and confidence score"""
        if not value or value.strip() == "":
            return False, 0.0

        # Get validation rule
        rule = FieldExtractor.FIELD_VALIDATION_RULES.get(field_name)
        if not rule:
            return True, 0.5  # No validation rule, medium confidence

        # Basic pattern matching
        pattern_match = bool(re.match(rule["pattern"], value))
        
        # Additional validation for dates
        if field_name in ["date_of_birth", "expiration_date", "issue_date"]:
            date_valid = FieldExtractor._validate_date(value)
            if not date_valid:
                return False, 0.0

        # Calculate confidence score (0.0 to 1.0)
        confidence = 0.0
        if pattern_match:
            # Start with 0.7 for pattern match
            confidence = 0.7
            
            # Add confidence based on field-specific criteria
            if field_name == "full_name":
                # Higher confidence for names with multiple parts
                parts = value.split()
                confidence += min(len(parts) * 0.1, 0.3)
            elif field_name in ["date_of_birth", "expiration_date", "issue_date"]:
                # Higher confidence for valid dates
                confidence += 0.3 if FieldExtractor._validate_date(value) else 0.0
            elif field_name in ["passport_number", "license_number", "uscis_number"]:
                # Higher confidence for proper length
                expected_length = 9 if field_name == "passport_number" else 8
                confidence += 0.3 if len(value) == expected_length else 0.15
            else:
                # Default additional confidence
                confidence += 0.2

        return pattern_match, min(confidence, 1.0)

    @staticmethod
    def extract_fields(text: str, document_type: str) -> List[ExtractedFieldBase]:
        """
        Extract fields from document text based on document type using GPT-4.
        """
        if document_type not in FieldExtractor.FIELD_MAPPINGS:
            raise ValueError(f"Unsupported document type: {document_type}")

        # Get expected fields for this document type
        expected_fields = FieldExtractor.FIELD_MAPPINGS[document_type]
        
        # Use GPT to extract fields
        extracted_data = get_gpt_extraction(text, document_type, expected_fields)
        
        # Convert to ExtractedFieldBase objects with validation
        fields = []
        for field_name, value in extracted_data.items():
            # Validate field and get confidence score
            is_valid, confidence = FieldExtractor._validate_field_value(field_name, value)
            
            # If validation fails, mark as needing correction
            needs_correction = not is_valid
            
            # Get validation rule description for error message
            rule = FieldExtractor.FIELD_VALIDATION_RULES.get(field_name, {})
            error_message = None if is_valid else f"Invalid format. Expected: {rule.get('description', 'valid value')}"
            
            fields.append(
                ExtractedFieldBase(
                    field_name=field_name,
                    field_value=value,
                    confidence_score=confidence,
                    needs_correction=needs_correction,
                    error_message=error_message
                )
            )
        
        return fields

    @staticmethod
    def validate_fields(fields: List[Dict], document_type: str) -> bool:
        """Validate if all required fields are present and valid"""
        if document_type not in FieldExtractor.FIELD_MAPPINGS:
            return False
            
        expected_fields = set(FieldExtractor.FIELD_MAPPINGS[document_type])
        
        # Check if all required fields are present
        provided_fields = {field["field_name"] for field in fields}
        if not expected_fields.issubset(provided_fields):
            return False
            
        # Validate each field
        for field in fields:
            is_valid, _ = FieldExtractor._validate_field_value(
                field["field_name"], 
                field["field_value"]
            )
            if not is_valid:
                return False
                
        return True 
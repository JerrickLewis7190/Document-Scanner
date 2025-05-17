"""
Field mapping and validation utility for document extraction.
Provides standardization of field names and validation of required fields.
"""

import logging
from typing import Dict, List, Tuple, Set, Optional

logger = logging.getLogger(__name__)

# Define required fields for each document type
REQUIRED_FIELDS = {
    'passport': {
        'full_name', 'date_of_birth', 'country', 'issue_date', 'expiration_date'
    },
    'drivers_license': {
        'license_number', 'date_of_birth', 'issue_date', 'expiration_date', 'first_name', 'last_name'
    },
    'ead_card': {
        'card_number', 'category', 'first_name', 'last_name', 'card_expires_date'
    }
}

# Field name standardization mappings
FIELD_ALIASES = {
    # Passport field aliases
    'passport_number': 'document_number',
    'passport_no': 'document_number',
    'passportno': 'document_number',
    'surname': 'last_name',
    'given_names': 'first_name',
    'given_name': 'first_name',
    'name': 'full_name',
    # Keep 'country' as its own field, separate from 'nationality'
    'country_of_issuance': 'nationality',
    'date_of_expiry': 'expiration_date',
    'expires': 'expiration_date',
    'date_of_issue': 'issue_date',
    'birthdate': 'date_of_birth',
    'birth_date': 'date_of_birth',
    'dob': 'date_of_birth',
    
    # Driver's license field aliases
    'license_no': 'license_number',
    'dl_number': 'license_number',
    'dl': 'license_number',
    'driver_license_number': 'license_number',
    'drivers_license_number': 'license_number',
    'operator_license': 'license_number',
    'document_number': 'license_number',
    'fname': 'first_name',
    'lname': 'last_name',
    'issue': 'issue_date',
    'expiry': 'expiration_date',
    'expiration': 'expiration_date',
    'expires_on': 'expiration_date',
    'expires_date': 'expiration_date',
    'card_expires_date': 'expiration_date',
    'issued_on': 'issue_date',
    
    # EAD card field aliases
    'ead_number': 'card_number',
    'card#': 'card_number',
    'card_#': 'card_number',
    'authorization_number': 'card_number',
    'employment_authorization_number': 'card_number',
    'valid_until': 'card_expires_date',
    # For EAD cards, 'expiration_date' should map to 'card_expires_date'
    # For other document types, 'expiration_date' should remain as is
    # This mapping is causing conflicts with drivers_license processing
    # 'expiration_date': 'card_expires_date',
    'first': 'first_name',
    'last': 'last_name',
    'ead_category': 'category',
    'class': 'category'
}

def standardize_field_names(extracted_fields: Dict[str, str], doc_type: str) -> Dict[str, str]:
    """
    Standardize field names based on aliases and document type.
    Args:
        extracted_fields: Dictionary of fields extracted from document
        doc_type: Type of document (passport, drivers_license, ead_card)
    Returns:
        Dictionary with standardized field names
    """
    standardized = {}
    
    # Convert doc_type to standard format - be more permissive with matching
    if doc_type.lower() in ['driver', 'drivers_license', 'driver_license', 'dl', 'driver license']:
        doc_type = 'drivers_license'
    elif doc_type.lower() in ['passport', 'pasport', 'p']:
        doc_type = 'passport'
    elif doc_type.lower() in ['ead', 'employment_authorization', 'ead_card']:
        doc_type = 'ead_card'
    
    # Ensure document_type field is standardized
    # Always convert 'P' to 'Passport' regardless of where it appears
    if 'document_type' in extracted_fields:
        if extracted_fields['document_type'] == 'P':
            standardized['document_type'] = 'Passport'
        elif doc_type == 'passport':
            standardized['document_type'] = 'Passport'
        elif doc_type == 'drivers_license':
            standardized['document_type'] = 'Driver\'s License'
        elif doc_type == 'ead_card':
            standardized['document_type'] = 'EAD Card'
        else:
            standardized['document_type'] = extracted_fields['document_type']
    else:
        # If document_type is not in the fields, set it based on doc_type
        if doc_type == 'passport':
            standardized['document_type'] = 'Passport'
        elif doc_type == 'drivers_license':
            standardized['document_type'] = 'Driver\'s License'
        elif doc_type == 'ead_card':
            standardized['document_type'] = 'EAD Card'
        else:
            standardized['document_type'] = doc_type
    
    # Process all extracted fields
    for field_name, value in extracted_fields.items():
        # Skip document_type as we've already handled it
        if field_name == 'document_type':
            continue
            
        # Convert field name to lowercase
        field_name_lower = field_name.lower()
        
        # Special handling for expiration_date based on document type
        if field_name_lower == 'expiration_date':
            if doc_type == 'ead_card':
                std_field_name = 'card_expires_date'
            else:
                std_field_name = 'expiration_date'
        # For passports, make sure both country and nationality are preserved
        elif field_name_lower == 'country' and doc_type == 'passport':
            std_field_name = 'country'
            # If nationality is not set, also use this value for nationality
            if 'nationality' not in standardized:
                standardized['nationality'] = value
        else:
            # Check if field is in aliases, otherwise keep original
            std_field_name = FIELD_ALIASES.get(field_name_lower, field_name_lower)
        
        standardized[std_field_name] = value
        
        # Special case: full_name can be split into first_name and last_name
        if std_field_name == 'full_name' and ' ' in value and value != 'NOT_FOUND':
            parts = value.strip().split(' ', 1)
            if len(parts) >= 2:
                if 'first_name' not in standardized:
                    standardized['first_name'] = parts[0]
                if 'last_name' not in standardized:
                    standardized['last_name'] = parts[1]
    
    # Special case for passport documents: Always include issue_date even if not found
    if doc_type == 'passport' and ('issue_date' not in standardized or standardized['issue_date'] == 'NOT_FOUND'):
        # If date_of_issue is available but issue_date is not, use date_of_issue
        if 'date_of_issue' in standardized and standardized['date_of_issue'] != 'NOT_FOUND':
            standardized['issue_date'] = standardized['date_of_issue']
        else:
            # Just set a default value for issue_date
            standardized['issue_date'] = 'Unknown'
    
    # Log what was standardized
    logger.debug(f"Standardized fields: {standardized}")
    
    return standardized

def validate_required_fields(fields: Dict[str, str], doc_type: str) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields for the document type are present and not 'NOT_FOUND'.
    Args:
        fields: Dictionary of extracted fields
        doc_type: Document type (passport, drivers_license, ead_card)
    Returns:
        Tuple: (is_valid, missing_fields)
    """
    # Standardize doc_type
    if doc_type.lower() in ['driver', 'drivers_license', 'driver_license', 'dl', 'driver license']:
        doc_type = 'drivers_license'
    elif doc_type.lower() in ['passport', 'pasport', 'p']:
        doc_type = 'passport'
    elif doc_type.lower() in ['ead', 'employment_authorization', 'ead_card']:
        doc_type = 'ead_card'
    else:
        # Unknown document type - can't validate required fields
        return False, ["Unknown document type - cannot validate required fields"]
    
    # Get required fields for document type
    required = REQUIRED_FIELDS.get(doc_type, set())
    
    # Log the required fields for debugging
    logger.debug(f"Required fields for {doc_type}: {required}")
    logger.debug(f"Provided fields: {fields}")
    
    # Check for missing fields
    missing = []
    for field in required:
        # For passports, we're more lenient with issue_date - if it's 'Unknown', that's ok
        if field == 'issue_date' and doc_type == 'passport' and fields.get(field) == 'Unknown':
            continue
            
        if field not in fields or fields[field] == "NOT_FOUND":
            missing.append(field)
            logger.error(f"Missing required field: {field}")
    
    if missing:
        logger.error(f"Critical fields missing: {missing}")
    
    return len(missing) == 0, missing

def get_essential_fields(doc_type: str) -> List[str]:
    """
    Get the list of essential fields for a specific document type.
    Args:
        doc_type: Document type
    Returns:
        List of essential field names
    """
    # Standardize doc_type
    if doc_type.lower() in ['driver', 'drivers_license', 'driver_license', 'dl']:
        doc_type = 'drivers_license'
    elif doc_type.lower() in ['passport', 'pasport', 'p']:
        doc_type = 'passport'
    elif doc_type.lower() in ['ead', 'employment_authorization', 'ead_card']:
        doc_type = 'ead_card'
    
    return list(REQUIRED_FIELDS.get(doc_type, [])) 
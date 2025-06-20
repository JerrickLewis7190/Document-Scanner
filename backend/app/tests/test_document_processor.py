import os
import pytest
from PIL import Image
import json
import numpy as np
from pathlib import Path
from app.services.document_processor import DocumentProcessor
import re

class TestDocumentProcessor:
    @pytest.fixture
    def document_processor(self):
        return DocumentProcessor()
        
    @pytest.fixture
    def wa_license_image_path(self):
        # Get the absolute path to the test image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        return os.path.join(workspace_root, 'Images', 'test_driver_license.png')
        
    @pytest.fixture
    def wa_license_expected_fields(self):
        return {
            'license_number': 'WDLJK00580GF',
            'first_name': 'JANE',
            'last_name': 'SAMPLE',
            'date_of_birth': '01/06/1978',
            'issue_date': '09/04/2018',
            'expiration_date': '09/04/2024',
            'address': '123 STREET ADDRESS YOUR CITY WA 99999-0000',
            'sex': 'F',
        }

    def test_wa_license_field_extraction(self, document_processor, wa_license_image_path, wa_license_expected_fields):
        """Test extraction of all fields from Washington driver's license"""
        
        # Read the test image
        with open(wa_license_image_path, 'rb') as f:
            image_bytes = f.read()
            
        # Process the image
        doc_type, extracted_fields, error_msg = document_processor.process_image(image_bytes)
        
        # Check document type
        assert doc_type == 'drivers_license', f"Expected document type 'drivers_license', got '{doc_type}'"
        assert error_msg is None, f"Expected no error, got: {error_msg}"
        
        # Convert extracted fields list to dictionary for easier comparison
        extracted_dict = {field['field_name']: field['field_value'] for field in extracted_fields}
        
        # Print extracted fields for debugging
        print("Extracted fields:", extracted_dict)
        
        # Check each expected field
        for field_name, expected_value in wa_license_expected_fields.items():
            assert field_name in extracted_dict, f"Missing field: {field_name}"
            actual_value = extracted_dict[field_name]
            assert actual_value == expected_value, f"Field {field_name} mismatch: expected '{expected_value}', got '{actual_value}'"
        
        # Additional verification - make sure key fields are present
        assert 'first_name' in extracted_dict, "Missing first_name field"
        assert 'last_name' in extracted_dict, "Missing last_name field"
        assert 'date_of_birth' in extracted_dict, "Missing date_of_birth field"
        assert 'license_number' in extracted_dict, "Missing license_number field"

    def test_document_classification(self, document_processor):
        """Test document type classification"""
        # Test drivers license classification
        doc_type, extracted_fields, error_msg = document_processor.process_image(b"dummy_image_data")
        assert doc_type == "unknown"
        assert error_msg is not None  # Should have error due to invalid image

    def test_wa_license_error_handling(self, document_processor):
        """Test error handling for invalid inputs"""
        # Test with empty image data
        doc_type, extracted_fields, error_msg = document_processor.process_image(b"")
        assert doc_type == "unknown"
        assert error_msg is not None
        # Update assertion to match actual error message format
        assert "image file" in error_msg.lower() or "cannot identify" in error_msg.lower()

        # Test with corrupted image data
        doc_type, extracted_fields, error_msg = document_processor.process_image(b"corrupted_data")
        assert doc_type == "unknown"
        assert error_msg is not None
        # Update assertion to match actual error message format
        assert "image file" in error_msg.lower() or "cannot identify" in error_msg.lower() 
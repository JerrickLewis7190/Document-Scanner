import pytest
from datetime import datetime
from app.services.document_processor import DocumentProcessor
from PIL import Image
import numpy as np
import os
import io

class TestDocumentProcessor:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()

    @pytest.fixture
    def test_images_dir(self):
        """Create synthetic test images with known content"""
        base_dir = "tests/test_data"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def create_synthetic_image(self, text, path):
        """Create a test image with specific text content"""
        img = Image.new('RGB', (800, 600), color='white')
        # Add text to image...
        img.save(path)
        return path

    def test_name_parsing(self, processor):
        """Test various name formats"""
        test_cases = [
            ("John Smith", {"first_name": "John", "last_name": "Smith"}),
            ("Smith John", {"first_name": "John", "last_name": "Smith"}),  # Asian format
            ("John A. Smith", {"first_name": "John", "last_name": "Smith", "middle_name": "A."}),
            ("van der Berg Hans", {"first_name": "Hans", "last_name": "van der Berg"}),
            ("Maria Garcia-Lopez", {"first_name": "Maria", "last_name": "Garcia-Lopez"}),
        ]
        
        for input_name, expected in test_cases:
            result = processor._parse_name(input_name)
            assert result == expected, f"Failed to parse name: {input_name}"

    def test_date_standardization(self, processor):
        """Test various date formats"""
        test_cases = [
            # US format
            ("01/15/2024", "2024-01-15"),
            # European format
            ("15/01/2024", "2024-01-15"),
            # ISO format
            ("2024-01-15", "2024-01-15"),
            # Various separators
            ("01-15-2024", "2024-01-15"),
            ("2024/01/15", "2024-01-15"),
            # Invalid dates should return original
            ("13/13/2024", "13/13/2024"),
            # Future dates for expiration
            ("01/15/2026", "2026-01-15"),
        ]
        
        for input_date, expected in test_cases:
            result = processor._standardize_date(input_date)
            assert result == expected, f"Failed to standardize date: {input_date}"

    def test_document_classification(self, processor, test_images_dir):
        """Test document type classification"""
        # Create test images with known content
        dl_text = "DRIVER LICENSE CLASS D"
        pp_text = "PASSPORT UNITED STATES OF AMERICA"
        ead_text = "EMPLOYMENT AUTHORIZATION DOCUMENT"
        
        dl_path = self.create_synthetic_image(dl_text, f"{test_images_dir}/dl_test.png")
        pp_path = self.create_synthetic_image(pp_text, f"{test_images_dir}/pp_test.png")
        ead_path = self.create_synthetic_image(ead_text, f"{test_images_dir}/ead_test.png")
        
        # Test classification
        assert processor._classify_document(dl_text.lower()) == "drivers_license"
        assert processor._classify_document(pp_text.lower()) == "passport"
        assert processor._classify_document(ead_text.lower()) == "ead"

    def test_field_extraction(self, processor, test_images_dir):
        """Test field extraction from documents"""
        # Test driver's license fields
        dl_content = """
        DRIVER LICENSE
        DL A1234567
        DOB 01/15/1990
        EXP 01/15/2025
        NAME JOHN A SMITH
        123 MAIN ST
        ANYTOWN, CA 12345
        """
        
        dl_path = self.create_synthetic_image(dl_content, f"{test_images_dir}/dl_fields.png")
        
        # Process the image
        with open(dl_path, 'rb') as f:
            doc_type, fields = processor.process_image(f.read())
            
        assert doc_type == "drivers_license"
        assert fields["license_number"] == "A1234567"
        assert fields["date_of_birth"] == "1990-01-15"
        assert fields["expiration_date"] == "2025-01-15"
        assert fields["name"]["first_name"] == "John"
        assert fields["name"]["last_name"] == "Smith"

    def test_error_handling(self, processor):
        """Test error handling for various scenarios"""
        # Test invalid image
        with pytest.raises(ValueError):
            processor.process_image(b"invalid image data")
            
        # Test empty text
        assert processor._classify_document("") is None
        
        # Test invalid date
        assert processor._standardize_date("invalid date") == "invalid date"

    def test_drivers_license_extraction(self, processor):
        """Test extraction of driver's license fields"""
        test_text = """
        DRIVER LICENSE
        1. NAME: JOHN A SMITH
        2. ADDRESS: 123 MAIN STREET
        ANYTOWN, WA 98101
        3. DOB: 01/15/1990
        4. EXP: 01/15/2025
        DL: A1234567
        """
        
        results = processor._extract_with_template(test_text, 'drivers_license')
        
        assert results['license_number'] == 'A1234567'
        assert results['name']['first_name'] == 'JOHN'
        assert results['name']['last_name'] == 'SMITH'
        assert results['dob'] == '1990-01-15'
        assert results['expiration'] == '2025-01-15'
        assert '123 MAIN STREET' in results['address']

    def test_passport_extraction(self, processor):
        """Test extraction of passport fields"""
        test_text = """
        PASSPORT
        TYPE P USA
        PASSPORT NO: 123456789
        SURNAME: JOHNSON
        GIVEN NAMES: MARY JANE
        NATIONALITY: UNITED STATES OF AMERICA
        DATE OF BIRTH: 03/21/1985
        """
        
        results = processor._extract_with_template(test_text, 'passport')
        
        assert results['passport_number'] == '123456789'
        assert results['name']['last_name'] == 'JOHNSON'
        assert results['name']['first_name'] == 'MARY JANE'
        assert results['nationality'] == 'UNITED STATES OF AMERICA'
        assert results['dob'] == '1985-03-21'

    def test_ead_extraction(self, processor):
        """Test extraction of EAD fields"""
        test_text = """
        EMPLOYMENT AUTHORIZATION DOCUMENT
        CARD#: ABC1234567890
        NAME: MARIA GARCIA
        DATE OF BIRTH: 05/10/1992
        CATEGORY: C09
        """
        
        results = processor._extract_with_template(test_text, 'ead')
        
        assert results['card_number'] == 'ABC1234567890'
        assert results['name']['first_name'] == 'MARIA'
        assert results['name']['last_name'] == 'GARCIA'
        assert results['dob'] == '1992-05-10'
        assert results['category'] == 'C09'

    def test_image_enhancement(self, processor):
        """Test image enhancement"""
        # Create a test image
        image = Image.new('RGB', (800, 600), color='white')
        enhanced = processor._enhance_image(image)
        
        assert enhanced.mode == 'L'  # Should be grayscale
        assert max(enhanced.size) <= 4000  # Should respect max size

    def test_error_handling(self, processor):
        """Test error handling"""
        # Test invalid document type
        with pytest.raises(ValueError):
            processor._extract_with_template("test", "invalid_type")
            
        # Test empty text
        with pytest.raises(ValueError):
            processor._classify_document("")
            
        # Test invalid image
        with pytest.raises(ValueError):
            processor.process_document(b"invalid image data") 
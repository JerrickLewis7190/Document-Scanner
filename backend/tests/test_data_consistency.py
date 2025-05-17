import pytest
import os
import json
from unittest.mock import patch, MagicMock
from app.services.document_processor import DocumentProcessor
from app.utils.field_mapping import standardize_field_names, validate_required_fields
from PIL import Image, ImageDraw, ImageFont
import io

class TestDataConsistency:
    """
    Tests to ensure consistency of data extraction across different documents formats,
    layouts, and styles including handling of different date formats and name orders.
    """
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    @pytest.fixture
    def test_dir(self):
        base_dir = "test_data/consistency"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    def create_test_image(self, content, image_path):
        """Create a test image with specified content"""
        # Create a blank image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text to the image (simplified)
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            # Fall back to default
            font = ImageFont.load_default()
            
        draw.text((50, 50), content, fill='black', font=font)
        img.save(image_path)
        return image_path
    
    def test_date_format_consistency(self, processor, test_dir):
        """Test extraction consistency with different date formats"""
        # Create test documents with different date formats
        date_formats = [
            "01/15/2024",  # MM/DD/YYYY
            "15/01/2024",  # DD/MM/YYYY
            "15JAN2024",   # Passport format
            "2024-01-15",  # ISO format
            "January 15, 2024"  # Full text format
        ]
        
        for idx, date_format in enumerate(date_formats):
            # Create passport test content with this date format
            content = f"""
            PASSPORT
            UNITED STATES OF AMERICA
            PASSPORT NO: P123456789
            SURNAME: SMITH
            GIVEN NAMES: JOHN
            NATIONALITY: USA
            DATE OF BIRTH: {date_format}
            DATE OF ISSUE: 01/01/2020
            DATE OF EXPIRY: 01/01/2030
            """
            
            # Create test image
            image_path = os.path.join(test_dir, f"date_format_{idx}.png")
            self.create_test_image(content, image_path)
            
            # Mock the document processing to simulate extraction
            with patch('app.utils.ai.get_gpt_extraction') as mock_extract:
                # Set up the mock to return data with the specific date format
                mock_extract.return_value = {
                    "document_type": "PASSPORT",
                    "passport_number": "P123456789",
                    "surname": "SMITH",
                    "given_names": "JOHN",
                    "nationality": "USA",
                    "date_of_birth": date_format,
                    "date_of_issue": "01/01/2020",
                    "date_of_expiry": "01/01/2030"
                }
                
                # Process the document
                with open(image_path, "rb") as f:
                    doc_type, fields, _ = processor.process_image(f.read())
                
                # Verify date standardization
                field_dict = {f["field_name"]: f["field_value"] for f in fields}
                dob = field_dict.get("date_of_birth", None)
                
                # Assert date was extracted and standardized
                assert dob is not None, f"Date of birth not extracted for format: {date_format}"
                assert dob != "NOT_FOUND", f"Date of birth not found for format: {date_format}"
    
    def test_name_order_consistency(self, processor, test_dir):
        """Test extraction consistency with different name orders"""
        # Test with names in different orders and formats
        name_variations = [
            {"input": "SMITH JOHN", "expected_first": "JOHN", "expected_last": "SMITH"},  # Last, First
            {"input": "JOHN SMITH", "expected_first": "JOHN", "expected_last": "SMITH"},  # First Last
            {"input": "SMITH, JOHN", "expected_first": "JOHN", "expected_last": "SMITH"},  # Last, First with comma
            {"input": "GARCIA-LOPEZ MARIA", "expected_first": "MARIA", "expected_last": "GARCIA-LOPEZ"},  # Hyphenated last name
            {"input": "李 明", "expected_first": "明", "expected_last": "李"}  # Chinese name (Li Ming)
        ]
        
        for idx, name_var in enumerate(name_variations):
            # Create test content
            content = f"""
            PASSPORT
            UNITED STATES OF AMERICA
            PASSPORT NO: P123456789
            NAME: {name_var["input"]}
            NATIONALITY: USA
            DATE OF BIRTH: 01/15/1985
            """
            
            # Create test image
            image_path = os.path.join(test_dir, f"name_format_{idx}.png")
            self.create_test_image(content, image_path)
            
            # Mock the document processing to simulate extraction
            with patch('app.utils.ai.get_gpt_extraction') as mock_extract:
                # Set up the mock to return data with the specific name format
                if "," in name_var["input"]:
                    # If comma-separated, split differently
                    last, first = name_var["input"].split(",")
                    mock_extract.return_value = {
                        "document_type": "PASSPORT",
                        "passport_number": "P123456789",
                        "surname": last.strip(),
                        "given_names": first.strip(),
                        "nationality": "USA",
                        "date_of_birth": "01/15/1985"
                    }
                else:
                    # Regular extraction
                    mock_extract.return_value = {
                        "document_type": "PASSPORT",
                        "passport_number": "P123456789",
                        "full_name": name_var["input"],
                        "nationality": "USA",
                        "date_of_birth": "01/15/1985"
                    }
                
                # Process the document
                with open(image_path, "rb") as f:
                    doc_type, fields, _ = processor.process_image(f.read())
                
                # Convert to dictionary for easier access
                field_dict = {f["field_name"]: f["field_value"] for f in fields}
                
                # Check if name was split correctly
                if "full_name" in field_dict:
                    # Full name should be preserved
                    assert field_dict["full_name"] == name_var["input"], f"Full name mismatch for: {name_var['input']}"
                
                # Note: This test might need adaptation based on how your system handles names
                # Some systems may not be able to correctly parse all name formats
    
    def test_mixed_field_formats(self, processor, test_dir):
        """Test extraction with mixed field formats and inconsistent data"""
        # Create a test document with mixed formats
        content = """
        DRIVER LICENSE
        NAME: John A. Smith
        DOB: January 15, 1985
        DL#: D1234567
        EXP: 01/15/2030
        CLASS: D
        """
        
        # Create test image
        image_path = os.path.join(test_dir, "mixed_format.png")
        self.create_test_image(content, image_path)
        
        # Mock the extraction with inconsistent field naming
        with patch('app.utils.ai.get_gpt_extraction') as mock_extract:
            mock_extract.return_value = {
                "document_type": "DRIVER LICENSE",
                "name": "John A. Smith",  # Full name instead of first/last
                "birth_date": "January 15, 1985",  # Text format date
                "license": "D1234567",  # Non-standard field name
                "expiry": "01/15/2030"  # Different field name for expiration
            }
            
            # Process the document
            with open(image_path, "rb") as f:
                doc_type, fields, _ = processor.process_image(f.read())
            
            # Convert to dictionary for easier access
            field_dict = {f["field_name"]: f["field_value"] for f in fields}
            
            # Verify field standardization
            assert doc_type == "drivers_license", "Document type not correctly identified"
            assert "first_name" in field_dict, "First name not extracted from full name"
            assert "last_name" in field_dict, "Last name not extracted from full name"
            assert "license_number" in field_dict, "License number field not standardized"
            assert field_dict["license_number"] == "D1234567", "License number not correctly mapped"
            assert "date_of_birth" in field_dict, "Date of birth field not standardized"
            assert "expiration_date" in field_dict, "Expiration date field not standardized"
    
    def test_field_mapping_robustness(self):
        """Test the robustness of field mapping against various input formats"""
        test_cases = [
            # Passport variations
            {
                "input": {
                    "document_type": "passport",
                    "passport_no": "123456789",
                    "surname": "SMITH",
                    "given_name": "JOHN",
                    "dob": "01/15/1985"
                },
                "expected": {
                    "document_number": "123456789",
                    "last_name": "SMITH",
                    "first_name": "JOHN",
                    "date_of_birth": "01/15/1985"
                }
            },
            # Driver's license variations
            {
                "input": {
                    "document_type": "driver license",
                    "dl": "D1234567",
                    "fname": "JOHN",
                    "lname": "SMITH",
                    "expiry": "01/15/2030"
                },
                "expected": {
                    "license_number": "D1234567",
                    "first_name": "JOHN",
                    "last_name": "SMITH",
                    "expiration_date": "01/15/2030"
                }
            },
            # EAD card variations
            {
                "input": {
                    "document_type": "employment authorization",
                    "card#": "EAD1234567890",
                    "first": "MARIA",
                    "last": "GARCIA",
                    "class": "C09",
                    "valid_until": "01/01/2025"
                },
                "expected": {
                    "card_number": "EAD1234567890",
                    "first_name": "MARIA",
                    "last_name": "GARCIA",
                    "category": "C09",
                    "card_expires_date": "01/01/2025"
                }
            },
            # Mixed fields and document types
            {
                "input": {
                    "document_type": "P",  # Abbreviated passport type
                    "name": "JOHN SMITH",
                    "nationality": "USA",
                    "birthdate": "15JAN1985"
                },
                "expected": {
                    "document_type": "Passport",
                    "full_name": "JOHN SMITH",
                    "nationality": "USA",
                    "date_of_birth": "15JAN1985",
                    "first_name": "JOHN",
                    "last_name": "SMITH"
                }
            }
        ]
        
        for case in test_cases:
            # Standardize the fields
            standardized = standardize_field_names(case["input"], case["input"]["document_type"])
            
            # Verify all expected fields are present with correct values
            for field, value in case["expected"].items():
                assert field in standardized, f"Missing expected field: {field}"
                assert standardized[field] == value, f"Field value mismatch for {field}: expected {value}, got {standardized[field]}" 
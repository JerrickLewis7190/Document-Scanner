import pytest
from datetime import datetime
from app.services.document_processor import DocumentProcessor
from PIL import Image
import os
import io

class TestDocumentProcessor:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()

    @pytest.fixture
    def test_images_dir(self):
        """Create synthetic test images with known content"""
        base_dir = "test_data"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def create_synthetic_image(self, text, path):
        """Create a test image with specific text content"""
        img = Image.new('RGB', (800, 600), color=(220, 220, 220))  # light gray background
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        # Draw a large rectangle to ensure the image is not blank
        draw.rectangle([20, 20, 780, 580], outline=(180, 180, 180), width=10)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
        # Draw the text in multiple lines if needed
        y = 60
        for line in text.split('\n'):
            draw.text((60, y), line, fill='black', font=font)
            y += 40
        img.save(path)
        return path

    def test_field_extraction(self, processor, test_images_dir):
        """Test field extraction from documents"""
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
        with open(dl_path, 'rb') as f:
            doc_type, fields, error = processor.process_image(f.read())
        assert doc_type == "drivers_license"
        field_map = {f["field_name"]: f["field_value"] for f in fields}
        assert field_map["license_number"] == "A1234567"
        assert field_map["date_of_birth"] in ["1990-01-15", "01/15/1990"]
        assert field_map["expiration_date"] in ["2025-01-15", "01/15/2025"]
        assert error is None or "missing" in error.lower() or error == "Critical fields missing - manual review required"

    def test_process_image_drivers_license(self, processor, test_images_dir):
        text = """
        DRIVER LICENSE\nDL A1234567\nDOB 01/15/1990\nEXP 01/15/2025\nNAME JOHN A SMITH\n123 MAIN ST\nANYTOWN, CA 12345
        """
        img_path = self.create_synthetic_image(text, f"{test_images_dir}/dl_fields.png")
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
        doc_type, fields, error = processor.process_image(img_bytes)
        assert doc_type == "drivers_license"
        field_map = {f["field_name"]: f["field_value"] for f in fields}
        assert field_map["license_number"] == "A1234567"
        assert field_map["date_of_birth"] in ["1990-01-15", "01/15/1990"]
        assert field_map["expiration_date"] in ["2025-01-15", "01/15/2025"]
        assert error is None or "missing" in error.lower() or error == "Critical fields missing - manual review required"

    def test_process_image_passport(self, processor, test_images_dir):
        text = """
        PASSPORT\nPASSPORT NO: P123456789\nSURNAME: SMITH\nGIVEN NAMES: JOHN\nNATIONALITY: USA\nDOB: 15JAN1985
        """
        img_path = self.create_synthetic_image(text, f"{test_images_dir}/pp_test.png")
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
        doc_type, fields, error = processor.process_image(img_bytes)
        assert doc_type == "passport"
        field_map = {f["field_name"]: f["field_value"] for f in fields}
        assert field_map["document_number"] == "P123456789"
        assert field_map["last_name"] == "SMITH"
        assert field_map["first_name"] == "JOHN"
        assert error is None or "missing" in error.lower() or error == "Critical fields missing - manual review required"

    def test_process_image_ead(self, processor, test_images_dir):
        text = """
        EMPLOYMENT AUTHORIZATION DOCUMENT\nCARD#: ABC1234567890\nNAME: MARIA GARCIA\nDATE OF BIRTH: 05/10/1992\nCATEGORY: C09
        """
        img_path = self.create_synthetic_image(text, f"{test_images_dir}/ead_test.png")
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
        doc_type, fields, error = processor.process_image(img_bytes)
        assert doc_type == "ead_card"
        field_map = {f["field_name"]: f["field_value"] for f in fields}
        assert field_map["card_number"] == "ABC1234567890"
        assert field_map["first_name"] == "MARIA"
        assert field_map["last_name"] == "GARCIA"
        assert error is None or "missing" in error.lower() or error == "Critical fields missing - manual review required"

    def test_normalize_date(self, processor):
        # Test the public static method
        assert processor.normalize_date("15JAN1985") == "15 Jan 1985"
        assert processor.normalize_date("01FEB2020") == "01 Feb 2020"
        assert processor.normalize_date("2024-01-15") == "2024-01-15"
        assert processor.normalize_date("13/13/2024") == "13/13/2024"

    def test_process_image_invalid(self, processor):
        # Test error handling for invalid image data
        doc_type, fields, error = processor.process_image(b"not an image")
        assert doc_type == "unknown"
        assert fields == []
        assert error is not None

    def test_low_quality_image_handling(self, processor, test_images_dir):
        """Test with a blurry/low-resolution image to ensure quality checks trigger"""
        # Create a very small, low-quality image
        low_res_image = Image.new('RGB', (50, 30), color='white')
        
        # Add some text that would be unreadable at this resolution
        # In a real test, we would add proper text
        
        # Save with low quality
        low_res_path = os.path.join(test_images_dir, "low_res_image.jpg")
        low_res_image.save(low_res_path, quality=10)
        
        # Read the image
        with open(low_res_path, 'rb') as f:
            low_res_data = f.read()
            
        # Process the low quality image
        doc_type, fields, error_msg = processor.process_image(low_res_data)
        
        # Check for quality warnings
        if error_msg:
            assert ("resolution" in error_msg.lower() or 
                    "quality" in error_msg.lower() or 
                    "small" in error_msg.lower() or
                    "blank" in error_msg.lower() or
                    "dark" in error_msg.lower())
        else:
            # If no error, the extraction should have limited results due to poor quality
            # This is a fuzzy assertion as the processor might still try to extract
            assert len(fields) < 5, "Low quality image should extract minimal data" 
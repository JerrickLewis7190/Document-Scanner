import pytest
import os
import json
from unittest.mock import patch, MagicMock
from app.utils.ai import get_gpt_extraction, get_gpt_classification
from app.services.document_processor import DocumentProcessor

class TestAIModelIntegration:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    @pytest.fixture
    def test_dir(self):
        base_dir = "tests/test_data/ai_integration"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    @patch('app.utils.ai.openai')
    def test_gpt_extraction_passport(self, mock_openai, processor):
        """Test GPT-4 Vision extraction for passport data"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "document_type": "PASSPORT",
            "passport_number": "123456789",
            "full_name": "JOHN SMITH",
            "nationality": "UNITED STATES OF AMERICA",
            "date_of_birth": "15JAN1985",
            "date_of_issue": "01JAN2020",
            "date_of_expiry": "01JAN2030"
        })
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Call the extraction function
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "pp_test.png")
        fields = get_gpt_extraction(image_path, "passport", ["document_type", "passport_number", "full_name", "nationality", "date_of_birth", "date_of_issue", "date_of_expiry"])
        
        # Validate the extracted fields
        assert fields["document_type"] == "PASSPORT"
        assert fields["passport_number"] == "123456789"
        assert fields["full_name"] == "JOHN SMITH"
        assert fields["date_of_birth"] == "15JAN1985"
    
    @patch('app.utils.ai.openai')
    def test_gpt_extraction_drivers_license(self, mock_openai, processor):
        """Test GPT-4 Vision extraction for driver's license data"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "document_type": "DRIVER LICENSE",
            "license_number": "D1234567",
            "first_name": "JOHN",
            "last_name": "SMITH",
            "date_of_birth": "05/15/1990",
            "issue_date": "01/01/2020",
            "expiration_date": "05/15/2025"
        })
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Call the extraction function
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "dl_test.png")
        fields = get_gpt_extraction(image_path, "drivers_license", ["document_type", "license_number", "first_name", "last_name", "date_of_birth", "issue_date", "expiration_date"])
        
        # Validate the extracted fields
        assert fields["document_type"] == "DRIVER LICENSE"
        assert fields["license_number"] == "D1234567"
        assert fields["first_name"] == "JOHN"
        assert fields["last_name"] == "SMITH"
        assert fields["date_of_birth"] == "05/15/1990"
    
    @patch('app.utils.ai.openai')
    def test_gpt_extraction_ead_card(self, mock_openai, processor):
        """Test GPT-4 Vision extraction for EAD card data"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "document_type": "EMPLOYMENT AUTHORIZATION",
            "card_number": "EAD1234567890",
            "first_name": "MARIA",
            "last_name": "GARCIA",
            "category": "C09",
            "card_expires_date": "01/01/2025"
        })
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Call the extraction function
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "ead_test.png")
        fields = get_gpt_extraction(image_path, "ead_card", ["document_type", "card_number", "first_name", "last_name", "category", "card_expires_date"])
        
        # Validate the extracted fields
        assert fields["document_type"] == "EMPLOYMENT AUTHORIZATION"
        assert fields["card_number"] == "EAD1234567890"
        assert fields["first_name"] == "MARIA"
        assert fields["last_name"] == "GARCIA"
        assert fields["category"] == "C09"
    
    @patch('app.utils.ai.openai')
    def test_error_handling(self, mock_openai, processor):
        """Test error handling when GPT API fails"""
        # Mock an error in the OpenAI API
        mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
        
        # Call the extraction function and verify it returns None on error
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "pp_test.png")
        fields = get_gpt_extraction(image_path, "passport", ["document_type"])
        
        assert fields is None
    
    @patch('app.utils.ai.openai')
    def test_malformed_response(self, mock_openai, processor):
        """Test handling of malformed responses from GPT API"""
        # Mock a non-JSON response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is not a JSON response"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Call the extraction function and verify it handles the error
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "pp_test.png")
        fields = get_gpt_extraction(image_path, "passport", ["document_type"])
        
        # Should either return None or an empty dict (depending on implementation)
        assert fields is None or fields == {}
    
    @patch('app.utils.ai.openai')
    def test_partial_fields(self, mock_openai, processor):
        """Test handling of partial field extraction"""
        # Mock a response with only some fields
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "document_type": "PASSPORT",
            # Missing other fields
        })
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Call the extraction function
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "pp_test.png")
        fields = get_gpt_extraction(image_path, "passport", ["document_type", "passport_number", "full_name"])
        
        # Validate that we got the fields that were provided
        assert fields["document_type"] == "PASSPORT"
        assert "passport_number" not in fields or fields["passport_number"] is None
    
    def test_end_to_end_document_processing(self, processor):
        """
        Test the entire document processing pipeline
        This test requires an actual OpenAI API key to run
        """
        # Skip if no API key is available
        import os
        if "OPENAI_API_KEY" not in os.environ:
            pytest.skip("No OpenAI API key available")
        
        # Test with a sample image
        image_path = os.path.join(os.path.dirname(__file__), "test_data", "pp_test.png")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Process the document
        doc_type, fields, error = processor.process_image(image_bytes)
        
        # Verify we got valid results
        assert error is None, f"Processing error: {error}"
        assert doc_type in ["passport", "drivers_license", "ead_card", "unknown"]
        assert len(fields) > 0, "No fields extracted"
        
        # Verify required fields based on document type
        if doc_type == "passport":
            required_fields = ["full_name", "date_of_birth", "nationality", "expiration_date"]
        elif doc_type == "drivers_license":
            required_fields = ["license_number", "first_name", "last_name", "expiration_date"]
        elif doc_type == "ead_card":
            required_fields = ["card_number", "first_name", "last_name", "category", "card_expires_date"]
        else:
            required_fields = []
        
        # Convert fields list to a map for easier checking
        field_map = {f["field_name"]: f["field_value"] for f in fields}
        
        # Check that required fields are present
        for field in required_fields:
            assert field in field_map, f"Missing required field: {field}"
            assert field_map[field] != "NOT_FOUND", f"Required field not found: {field}" 
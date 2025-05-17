import os
import re
from typing import Tuple, Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import json
import logging
import base64
from PIL import Image
from io import BytesIO
import httpx

load_dotenv()

# Configure OpenAI with optional proxy
client_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}

# Only add proxy if FIDDLER_PROXY is enabled
if os.getenv("FIDDLER_PROXY", "").lower() == "true":
    transport = httpx.HTTPTransport(
        proxy="http://127.0.0.1:8888",  # Fiddler default port
        verify=False  # Required for Fiddler HTTPS inspection
    )
    client_kwargs["http_client"] = httpx.Client(transport=transport)

client = OpenAI(**client_kwargs)

# Configure logger
logger = logging.getLogger(__name__)

def check_image_quality(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Check basic image quality before sending to GPT-4 Vision.
    Returns (is_valid, error_message)
    """
    try:
        with Image.open(image_path) as img:
            # Check image resolution
            width, height = img.size
            if width < 500 or height < 300:
                return False, f"Image resolution too low ({width}x{height}). Minimum required is 500x300 for accurate processing."
                
            # Check if image is empty or solid color
            if img.mode == 'RGB':
                # Convert to grayscale for histogram analysis
                img = img.convert('L')
            
            # Get image histogram
            hist = img.histogram()
            
            # Check if image is mostly empty (>90% white or black)
            total_pixels = width * height
            white_threshold = int(total_pixels * 0.9)
            black_threshold = int(total_pixels * 0.9)
            
            if hist[0] > black_threshold or hist[255] > white_threshold:
                return False, "Image appears to be blank or too dark. Please provide a clearer scan."
            
            # Check file size
            img.seek(0)
            file_size = os.path.getsize(image_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False, "File size too large. Please compress the image."
            
            return True, None
            
    except Exception as e:
        logger.error(f"Error checking image quality: {e}")
        return False, f"Invalid image file: {str(e)}"

def validate_gpt_response(response_text: str, doc_type: str, fields: List[str]) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Parse GPT's response and extract JSON.
    Returns (is_valid, error_message, extracted_fields)
    """
    try:
        # Log the raw response for debugging
        logger.debug(f"Raw GPT response: {response_text}")
        
        # First try direct JSON parsing
        try:
            extracted_fields = json.loads(response_text)
            logger.debug("Direct JSON parsing successful")
        except json.JSONDecodeError:
            # If direct parsing fails, try to find JSON object in the response
            logger.debug("Direct JSON parsing failed, trying to extract JSON from response")
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                logger.error("No JSON object found in response")
                return False, "No valid JSON found in GPT response", None
            
            # Clean up the JSON string
            json_str = json_match.group(0)
            json_str = re.sub(r'[\n\r\t]', '', json_str)  # Remove newlines and tabs
            json_str = re.sub(r',\s*}', '}', json_str)    # Remove trailing commas
            
            try:
                extracted_fields = json.loads(json_str)
                logger.debug("JSON extraction and parsing successful")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extracted JSON: {str(e)}\nJSON string: {json_str}")
                return False, f"Invalid JSON format: {str(e)}", None
        
        # Log extracted fields
        logger.debug(f"Extracted fields: {extracted_fields}")
        
        # Validate required fields
        missing_fields = [field for field in fields if field not in extracted_fields]
        if missing_fields:
            logger.warning(f"Missing fields in response: {missing_fields}")
            extracted_fields.update({field: "NOT_FOUND" for field in missing_fields})
            
        # Validate field formats
        invalid_fields = []
        for field, value in extracted_fields.items():
            if not value or value.strip() == "":
                extracted_fields[field] = "NOT_FOUND"
                invalid_fields.append(field)
            elif isinstance(value, str):
                extracted_fields[field] = value.strip().upper()
                
        if invalid_fields:
            logger.warning(f"Fields with invalid values: {invalid_fields}")
            
        # Check if all fields are NOT_FOUND
        all_not_found = all(value == "NOT_FOUND" for value in extracted_fields.values())
        if all_not_found:
            logger.error("All fields are NOT_FOUND")
            return False, "Critical fields missing - manual review required", None
            
        return True, None, extracted_fields
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}\nResponse text: {response_text}")
        return False, f"Invalid JSON in GPT response: {str(e)}", None
    except Exception as e:
        logger.error(f"Validation error: {str(e)}\nResponse text: {response_text}")
        return False, f"Error parsing GPT response: {str(e)}", None

def encode_image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_gpt_classification(text: str) -> Tuple[str, float]:
    """Classify document type using GPT"""
    text_lower = text.lower()
    
    # Define classification rules
    rules = {
        'drivers_license': ['driver license', 'driver\'s license', 'dl', 'operator license', 'drivers license'],
        'passport': ['passport', 'united states of america', 'type p', 'passport no'],
        'ead': ['employment authorization', 'ead', 'authorization document', 'card#']
    }
    
    # Check each document type
    max_confidence = 0.0
    best_doc_type = None
    
    for doc_type, keywords in rules.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > 0:
            confidence = matches / len(keywords)
            if confidence > max_confidence:
                max_confidence = confidence
                best_doc_type = doc_type
            
    return best_doc_type, max_confidence

def validate_field_format(field_name: str, value: str) -> bool:
    """Validate field format based on expected patterns"""
    if value == "NOT_FOUND":
        return True
        
    patterns = {
        'license_number': r'^[A-Z0-9]{8,}$',
        'first_name': r'^[A-Z][A-Z\s\-\'\.]+$',
        'middle_initial': r'^[A-Z]$',
        'last_name': r'^[A-Z][A-Z\s\-\'\.]+$',
        'date_of_birth': r'^\d{2}/\d{2}/\d{4}$',
        'issue_date': r'^\d{2}/\d{2}/\d{4}$',
        'expiration_date': r'^\d{2}/\d{2}/\d{4}$',
        'address': r'^.+$',  # Any non-empty string
        'sex': r'^[MF]$',
        'height': r'^\d-\d{2}$',
        'weight': r'^\d{2,3}\s?lb$',
        'eyes': r'^[A-Z]{3}$',
        'restrictions': r'^[A-Z0-9\s]+$',
        'endorsements': r'^[A-Z0-9\s]+$',
        'donor': r'^(YES|NO)$',
        'document_type': r'^.+$',  # Any non-empty string
        'revision_date': r'^REV\s+\d{2}/\d{2}/\d{4}$'
    }
    
    if field_name not in patterns:
        return True
        
    return bool(re.match(patterns[field_name], value))

def get_gpt_extraction(image_path: str, doc_type: str, fields: List[str]) -> Dict[str, str]:
    """Extract fields from image using GPT-4 Vision"""
    try:
        # First check image quality
        is_valid, error_msg = check_image_quality(image_path)
        if not is_valid:
            logger.error(f"Image quality check failed: {error_msg}")
            return {field: "NOT_FOUND" for field in fields}

        # Validate image file exists and is readable
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {field: "NOT_FOUND" for field in fields}

        try:
            # Try to open and validate the image
            with Image.open(image_path) as img:
                # Check if image is too large
                if os.path.getsize(image_path) > 20 * 1024 * 1024:  # 20MB limit
                    logger.error("Image file too large for GPT Vision API")
                    return {field: "NOT_FOUND" for field in fields}
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                # Save as JPEG if not already
                if not image_path.lower().endswith('.jpg'):
                    temp_path = image_path + '.jpg'
                    img.save(temp_path, 'JPEG', quality=95)  # Increased JPEG quality
                    image_path = temp_path
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            return {field: "NOT_FOUND" for field in fields}

        # Fields string for the prompt
        fields_str = ', '.join(fields)
        
        # Create document-type specific prompts
        if doc_type.lower() == 'passport':
            prompt = (
                f"Extract the following fields from this passport document and return them as a JSON object with exactly these keys: {fields_str}. "
                "Focus on these critical passport fields: full_name, date_of_birth, country, issue_date, expiration_date, nationality, document_number. "
                "For document_number, look for 'Passport Number' or similar. "
                "For country and nationality, look for 'Nationality' or country of issuance. "
                'If a field is missing or unreadable, use "NOT_FOUND". Return only a JSON object without explanation.'
            )
        elif doc_type.lower() in ['drivers_license', 'driver license', 'dl']:
            prompt = (
                f"Extract the following fields from this driver's license document and return them as a JSON object with exactly these keys: {fields_str}. "
                "Focus ONLY on these critical driver's license fields: license_number, date_of_birth, issue_date, expiration_date, first_name, last_name. "
                "For license_number, look for 'Driver License Number', 'DL Number', or similar. "
                "The license_number field is the most important field to extract correctly. "
                'If a field is missing or unreadable, use "NOT_FOUND". Return only a JSON object without explanation.'
            )
        elif doc_type.lower() in ['ead', 'employment authorization']:
            prompt = (
                f"Extract the following fields from this Employment Authorization Document (EAD) and return them as a JSON object with exactly these keys: {fields_str}. "
                "Focus on these critical EAD fields: card_number, category, card_expires_date, last_name, first_name. "
                "For card_number, look for 'Card#', 'EAD Number', or similar. "
                "For card_expires_date, look for 'Expires' or 'Valid Until'. "
                'If a field is missing or unreadable, use "NOT_FOUND". Return only a JSON object without explanation.'
            )
        else:
            # Generic prompt for unknown document types
            prompt = (
                f"Extract the following fields from this document image and return them as a JSON object with exactly these keys: {fields_str}. "
                "For the field 'document_number', extract the value labeled as 'Number', 'Document Number', 'ID Number', or similar. "
                'If a field is missing or unreadable, use "NOT_FOUND". Return only a JSON object without explanation.'
            )
        
        # --- LOGGING ---
        logger.info(f"Sending image to GPT-4 Vision: {image_path}")
        logger.info(f"Prompt sent to GPT-4 Vision:\n{prompt}")
        # --- END LOGGING ---

        try:
            # Convert image to base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as b64_error:
            logger.error(f"Error converting image to base64: {str(b64_error)}")
            return {field: "NOT_FOUND" for field in fields}

        try:
            # Make API call to GPT-4 Vision
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document field extraction expert. Extract information precisely as it appears on the document."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0
            )
        except Exception as api_error:
            logger.error(f"Error calling GPT Vision API: {str(api_error)}")
            return {field: "NOT_FOUND" for field in fields}

        # Get response text
        response_text = response.choices[0].message.content
        
        # Log the raw response
        logger.debug(f"Raw GPT response for {doc_type}: {response_text}")
        
        # Validate GPT response
        is_valid, error_msg, extracted_fields = validate_gpt_response(response_text, doc_type, fields)
        
        if not is_valid:
            logger.error(f"GPT response validation failed: {error_msg}")
            # Instead of returning all NOT_FOUND, try to use partial results
            if extracted_fields:
                return extracted_fields
            return {field: "NOT_FOUND" for field in fields}
        
        # Map aliases to document_number if present
        doc_number_aliases = [
            "document_number", "passport_number", "passport no", "document no", "passportno", "documentno", "id_number", "id no", "idno"
        ]
        doc_number = None
        for alias in doc_number_aliases:
            value = extracted_fields.get(alias)
            if value and value != "NOT_FOUND":
                doc_number = value
                break
        if doc_number:
            extracted_fields["document_number"] = doc_number
        else:
            extracted_fields["document_number"] = "NOT_FOUND"
        
        return extracted_fields

    except Exception as e:
        logger.error(f"Error in GPT-4 extraction: {e}")
        return {field: "NOT_FOUND" for field in fields} 
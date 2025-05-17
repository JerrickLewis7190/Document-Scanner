import os
import re
from typing import Tuple, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gpt_classification(text: str) -> Tuple[str, float]:
    """
    Use GPT to classify the document type.
    Returns tuple of (document_type, confidence)
    """
    prompt = f"""
    You are a document classification expert. Analyze this OCR-extracted text and classify the document.
    The text may be noisy or contain errors. Look for key identifying features:

    Drivers License indicators:
    - Format: Portrait ID card with photo
    - Fields: DL Number, DOB, EXP, Height, Eyes, Sex
    - Headers: "DRIVER LICENSE" or "DRIVER'S LICENSE"
    - State name prominently displayed
    
    Passport indicators:
    - Format: Booklet page with MRZ code
    - Fields: Passport No, Nationality, DOB, Sex
    - Headers: "PASSPORT" or "PASSEPORT"
    - Machine Readable Zone starting with "P<"
    
    EAD Card indicators:
    - Format: Card with USCIS branding
    - Fields: A-Number, Category, Valid From/To
    - Headers: "EMPLOYMENT AUTHORIZATION" or "EAD"
    - Category codes like "C08" or "C09"

    Text to analyze:
    {text}
    
    Respond ONLY in format: TYPE|CONFIDENCE
    Where TYPE is one of: drivers_license, passport, ead_card
    And CONFIDENCE is 0.0-1.0
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a document classification expert. You must ONLY respond with TYPE|CONFIDENCE where TYPE is exactly one of: drivers_license, passport, ead_card"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10  # Very short response needed
        )
        
        result = response.choices[0].message.content.strip()
        doc_type, confidence = result.split("|")
        doc_type = doc_type.strip().lower()
        
        # Validate the document type
        valid_types = ['drivers_license', 'passport', 'ead_card']
        if doc_type not in valid_types:
            doc_type = 'drivers_license'  # Default to most common type if uncertain
            confidence = 0.5
            
        return doc_type, float(confidence)
        
    except Exception as e:
        raise Exception(f"GPT classification failed: {str(e)}")

def get_gpt_extraction(text: str, document_type: str, fields: List[str]) -> Dict[str, str]:
    """
    Use GPT to extract specified fields from document text.
    Returns dictionary of field names and values.
    """
    fields_str = "\n".join([f"- {field}" for field in fields])
    
    prompt = f"""
    You are extracting fields from a {document_type}. The text is OCR-generated and contains potential errors.
    Use context clues and correct common OCR misreads. Pay special attention to field patterns and locations.

    Required fields to extract:
    {fields_str}

    CRITICAL FIELD PATTERNS AND LOCATIONS:

    1. License Number:
       - Format: LETTER{{1-5}}NUMBER{{5-8}}LETTER{{1-2}} (e.g., WDLJK00580GF)
       - Usually near top or bottom of document
       - Common errors: O→0, I→1, S→5
       - ALWAYS verify the last 1-2 characters are letters

    2. Full Name:
       - ALL UPPERCASE, typically near top
       - Format: FIRST [MIDDLE] LAST (include middle initial if present)
       - Example: "JANE A SAMPLE"
       - Look for text after "NAME:" or near photo area
       - Common errors: O→0 (e.g., "JOHN" not "J0HN")

    3. Dates (DOB and Expiration):
       - U.S. Format: MM/DD/YYYY
       - DOB near physical descriptors
       - EXP/Expiration near top or bottom
       - Example: "01/08/1978"
       - Verify against document context

    4. Sex:
       - Single letter: F or M
       - Located near physical descriptors (height, eyes)
       - Verify against photo and name context
       - Common error: Confusing F/P or M/N

    5. Height:
       - Format: X-YY or X'YY" (e.g., "5-04" or "5'4"")
       - Near other physical descriptors
       - Common error: Confusing - with '

    6. Eyes:
       - Three-letter codes: BLU, BRO, GRN, HAZ
       - Near height and sex
       - Must match standard codes exactly

    7. Address:
       - Street number + name + state abbrev.
       - Multiple lines, typically center of document
       - Verify state abbreviation is valid (e.g., WA, CA)

    COMMON OCR ERRORS TO CORRECT:
    - "0" (zero) misread as "O" (letter)
    - "1" misread as "I" or "l"
    - "5" misread as "S"
    - "8" misread as "B"
    - Extra spaces or missing spaces
    - Merged characters (e.g., "rn" as "m")

    Text from document:
    {text}

    EXTRACTION RULES:
    1. Return "NOT_FOUND" if field is truly not present
    2. Do not guess or make up values
    3. Use surrounding context to verify each field
    4. Clean up common OCR errors in values
    5. Double-check critical fields (name, license, dates)

    Respond in exact format:
    field_name1: value1
    field_name2: value2
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a document field extraction expert specializing in U.S. ID documents.
                You excel at finding patterns in noisy OCR text and correcting common OCR errors.
                You understand document layout and field relationships.
                You NEVER guess values - use NOT_FOUND if uncertain."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse response into dictionary
        extracted = {}
        for line in result.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
                
            field, value = [part.strip() for part in line.split(":", 1)]
            field = field.lstrip("- ")
            
            # Clean up common OCR errors in values
            if value != "NOT_FOUND":
                # Handle common OCR substitutions
                value = re.sub(r'(?<![A-Z])O(?![A-Z])', '0', value)  # O → 0 except in names
                value = re.sub(r'(?<![A-Z])I(?![A-Z])', '1', value)  # I → 1 except in names
                value = re.sub(r'(?<![A-Z])S(?=\d)', '5', value)     # S → 5 when before numbers
                value = re.sub(r'(?<=\d)B(?=\d)', '8', value)        # B → 8 between numbers
                value = re.sub(r'\s+', ' ', value)                    # Normalize whitespace
                
                # Special handling for dates
                if any(f in field.lower() for f in ['date', 'dob', 'exp']):
                    # Ensure date format is MM/DD/YYYY
                    date_parts = re.findall(r'\d+', value)
                    if len(date_parts) == 3:
                        month, day, year = date_parts
                        value = f"{int(month):02d}/{int(day):02d}/{year}"
                
                # Special handling for license numbers
                if 'license' in field.lower() and value != "NOT_FOUND":
                    # Ensure last characters are letters if pattern matches
                    if re.match(r'^[A-Z]{1,5}\d{5,8}[A-Z]{0,2}$', value):
                        value = re.sub(r'O(?=[A-Z]*$)', '0', value)  # Fix O→0 except in final letters
                
            value = value.strip()
            extracted[field] = value
                
        # Ensure all requested fields are present
        for field in fields:
            clean_field = field.lstrip("- ")
            if clean_field not in extracted:
                extracted[clean_field] = "NOT_FOUND"
                
        return extracted
        
    except Exception as e:
        raise Exception(f"GPT extraction failed: {str(e)}") 
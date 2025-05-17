# 🚀 Document Scanner Backend

The backend component of the Document Scanner application, built with FastAPI and Python to provide API endpoints for document processing, classification, and information extraction.

## 📋 Features

- **Document Processing**: Upload and process passport, driver's license, and EAD card images
- **AI-powered Classification**: Automatically identify document types
- **Information Extraction**: Extract relevant fields based on document type
- **Data Persistence**: Store document data and extracted fields in SQLite database
- **REST API**: Clean API endpoints with FastAPI
- **File Storage**: Store uploaded documents for reference

## 🔧 Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **OpenAI**: AI-powered document analysis and field extraction
- **PDF2Image/PyMuPDF**: PDF handling and conversion
- **Pillow**: Image processing
- **SQLite**: Lightweight database

## 🗂️ Directory Structure

```
backend/
├── app/                     # Main application code
│   ├── api/                 # API endpoint definitions
│   │   └── endpoints.py     # Route handlers
│   ├── models/              # Database models
│   │   └── db_models.py     # SQLAlchemy models
│   ├── services/            # Business logic
│   │   └── document_processor.py  # Document processing service
│   └── utils/               # Helper utilities
│       ├── ai.py            # AI integration
│       └── field_mapping.py # Field standardization
├── logs/                    # Application logs
├── uploads/                 # Uploaded document storage
├── sample_documents/        # Sample documents for testing
├── tests/                   # Unit and integration tests
├── main.py                  # Application entry point
└── requirements.txt         # Project dependencies
```

## 🛠️ Setup & Installation

### System Requirements

Before setting up the backend, ensure you have the following installed:

- **Python**: Version 3.8 or higher
  - [Download Python](https://www.python.org/downloads/)
  - Verify installation: `python --version`

- **Poppler**: Required for PDF processing
  - Windows: Install via [poppler for Windows](https://github.com/oschwartz10612/poppler-windows)
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`
  - Add to PATH environment variable

- **Tesseract OCR** (if using OCR features)
  - Windows: Can be installed via [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`
  - Add to PATH environment variable

- **OpenAI API Key**
  - Create an account at [OpenAI](https://openai.com/)
  - Generate API key from the OpenAI dashboard

### Installation Steps

1. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```sh
   python main.py
   ```

5. Access the API at http://localhost:8000 and the API docs at http://localhost:8000/docs

## 📚 API Documentation

### Document Management

#### Upload and Process Document
- **Endpoint**: `POST /api/documents`
- **Request**: Multipart form with file upload
- **Response**: Document details with extracted fields
- **Example**:
  ```json
  {
    "id": 1,
    "filename": "passport.jpg",
    "document_type": "passport",
    "created_at": "2025-05-16T23:15:23.346Z",
    "document_content": {
      "document_number": "1234567890USA8501154M2806199",
      "full_name": "JOHN MICHAEL",
      "date_of_birth": "15JAN1985",
      "expiration_date": "20JUN2028"
    },
    "image_url": "/uploads/passport.jpg"
  }
  ```

#### Get All Documents
- **Endpoint**: `GET /api/documents`
- **Response**: List of all processed documents

#### Get Document by ID
- **Endpoint**: `GET /api/documents/{document_id}`
- **Response**: Document details with extracted fields

#### Update Document Fields
- **Endpoint**: `PATCH /api/documents/{document_id}`
- **Request**: 
  ```json
  {
    "fields": [
      {"field_name": "full_name", "field_value": "JOHN SMITH"}
    ]
  }
  ```
- **Response**: Updated document details

#### Delete Document
- **Endpoint**: `DELETE /api/documents/{document_id}`
- **Response**: Success confirmation

#### Delete All Documents
- **Endpoint**: `DELETE /api/documents`
- **Response**: Success confirmation

### Health Check
- **Endpoint**: `GET /health`
- **Response**: API health status

## 🧪 Testing

Run the automated test suite:
```sh
pytest
```

Run specific tests:
```sh
pytest tests/test_endpoints.py
```

## 🔍 Debugging

Application logs are stored in the `logs/` directory. The logging level can be adjusted in `main.py`.

## 📘 Implementation Details

### Document Processing Flow
1. User uploads a document image
2. Image preprocessing (resize, enhance)
3. AI model classifies document type
4. Based on classification, specific fields are extracted
5. Data is stored in the database
6. Response returned with document ID and extracted fields

### Field Extraction
The system extracts different fields based on document type:
- **Passport**: document number, full name, nationality, date of birth, expiration date
- **Driver's License**: license number, name, address, date of birth, expiration date
- **EAD Card**: alien number, name, country of birth, expiration date, category

### Database Schema
- `Document`: Stores document metadata and binary content
- `ExtractedField`: Stores individual extracted fields with correction history 
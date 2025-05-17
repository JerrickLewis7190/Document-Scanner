# 🚀 Document Scanner Backend

[📄 Backend Design](./Backend%20Design.md)

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
- **OpenAI**: AI-powered document classification and field extraction
- **Pillow**: Image processing
- **Pikepdf**: PDF parsing and conversion (without external dependencies)
- **PyMuPDF (fitz)**: Fallback PDF processing when needed

## 🔨 Prerequisites

- **Python 3.8+**: Required for the application
- **Git**: For version control
- **pip**: For package management

## 🚀 Setup and Running

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/document-scanner.git
   cd document-scanner/backend
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   
   Create a `.env` file in the backend directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./document_scanner.db
   UPLOAD_FOLDER=./uploads
   ```

5. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be available at: http://localhost:8000

6. **Access API Documentation**
   
   FastAPI automatically generates documentation at:
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/redoc (ReDoc)

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

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
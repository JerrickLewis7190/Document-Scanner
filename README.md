# 📄 Casium Immigration Document Scanner (Backend)

This is the backend component of a full-stack application designed for Casium's take-home project. The system processes immigration documents using AI-powered classification and extraction techniques.

## 🚀 Features (Step 1 Complete)

- 📷 Upload document image or PDF
- 🧠 Classifies document type: `passport`, `driver_license`, or `ead_card`
- 🔍 Uses OCR (pytesseract) for initial classification
- 🔧 FastAPI backend with an extensible structure

Future Steps:
- Field extraction using AI
- Verification UI with React + TypeScript
- SQLite persistence of extractions and corrections

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **OCR**: Tesseract (via pytesseract)
- **Frontend**: React + TypeScript *(not included yet)*
- **Database**: SQLite (planned)
- **AI Tools**: GPT-4 Vision or other OCR/LLMs *(planned)*

---

## 🧪 How to Run (Backend)

### 1. Clone the Repo

```bash
git clone https://github.com/JerrickLewis7190/Document-Scanner.git
cd casium-doc-scanner/backend
```

## 3. Create & Activate Virtual Environment (optional but recommended)

```bash
python -m venv venv

source venv/bin/activate  # macOS/Linux
venv\Scripts\activate # Windows


## 4. Install Depdencies
pip install -r requirements.txt

```

## 1. Project Structure

A good starting structure:

```
casium-doc-scanner/
  backend/
    main.py
    requirements.txt
    utils.py
    models.py
    (other modules as needed)
```

## 2. requirements.txt

You'll need at least:

```
fastapi
uvicorn
pytesseract
Pillow
python-multipart
```

## 3. main.py (FastAPI app)

This will:
- Accept file uploads (image or PDF)
- Run OCR using pytesseract
- Classify the document type (simple heuristic for now)

## 4. Example Implementation

Would you like me to scaffold out the code for `main.py` and `requirements.txt` so you can get started right away?  
Or do you want a more detailed breakdown of each step (file upload, OCR, classification, etc.)?

Let me know your preference, and I'll generate the code for you!

---

## Backend Setup (Step 1)

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```
4. The API will be available at http://127.0.0.1:8000

### Test the API
- Use a tool like Postman or curl to POST an image or PDF to `/classify`.
- You should receive a response like `{ "document_type": "passport" }` (placeholder).

---

## 🧪 Running Backend Tests

1. From the backend directory, run:
   ```sh
   pytest
   ```
2. All tests in the `tests/` folder will be executed.

---

# Document Scanner Project

A web application for scanning and extracting information from immigration documents (passports, driver's licenses, and EAD cards) using computer vision and machine learning.

## Features

- Upload and process immigration documents
- Extract key information automatically
- View and verify extracted information
- Edit and correct extracted fields
- Store document history
- Support for multiple document types:
  - Passports
  - Driver's Licenses
  - Employment Authorization Documents (EAD)

## Project Structure

```
Document-Scanner/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── sample_documents/   # Sample document generators
│   ├── tests/             # Backend tests
│   ├── uploads/           # Document storage
│   └── main.py           # FastAPI application
├── frontend/              # React/TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── types/       # TypeScript types
│   │   └── App.tsx      # Main application
│   └── package.json
└── README.md
```

## Technology Stack

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy (SQLite database)
- PyTorch & Transformers for document processing
- Pillow for image handling

### Frontend
- React 18
- TypeScript
- Material-UI (MUI)
- Axios for API calls

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python main.py
   ```
   The server will run at http://localhost:8000

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```
   The application will be available at http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Click "Extract New Document" to upload a document
3. The system will automatically:
   - Process the document
   - Extract relevant information
   - Display the original document
   - Show extracted fields for verification
4. Review and edit extracted information if needed
5. View document history in the left panel

## API Endpoints

- `POST /api/documents/process`: Upload and process a new document
- `GET /api/documents`: Get list of processed documents
- `PUT /api/documents/{document_id}/correct`: Update extracted fields

## Development

### Generate Sample Documents

The project includes a script to generate sample documents for testing:

```bash
cd backend/sample_documents
python generate_sample_images.py
```

This will create sample passport, driver's license, and EAD card images in the `sample_images` directory.

### Running Tests

```bash
cd backend
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# Document Scanner

A full-stack application for scanning, classifying, and extracting information from immigration documents using OCR and AI-assisted processing.

## Features

- Upload and process PDF and image documents
- Automatic document type classification (Passport, Driver's License, EAD Card)
- Field extraction based on document type
- Manual field correction with persistence
- Document history management
- Modern, responsive UI

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite Database
- Tesseract OCR
- GPT-4 for classification and extraction
- PDF2Image for PDF processing

### Frontend
- React with TypeScript
- Material-UI (MUI) components
- Axios for API communication
- React Dropzone for file uploads

## Prerequisites

- Python 3.8+
- Node.js 16+
- Tesseract OCR
- OpenAI API key
- Poppler (for PDF processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/document-scanner.git
cd document-scanner
```

2. Set up the backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_api_key_here
```

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Open http://localhost:3000 in your browser

## API Endpoints

- `POST /api/classify` - Classify a document
- `POST /api/extract` - Extract fields from a document
- `POST /api/documents` - Process and store a new document
- `GET /api/documents` - Get list of processed documents
- `GET /api/documents/{id}` - Get a specific document
- `DELETE /api/documents/{id}` - Delete a specific document
- `DELETE /api/documents` - Delete all documents

## Development

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── db/
│   │   ├── crud.py
│   │   └── session.py
│   ├── models/
│   │   ├── db_models.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── classifier.py
│   │   └── extractor.py
│   └── utils/
│       ├── ai.py
│       └── ocr.py
└── main.py
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── DocumentViewer.tsx
│   │   ├── FieldEditor.tsx
│   │   ├── HistorySidebar.tsx
│   │   └── UploadForm.tsx
│   ├── services/
│   │   └── api.ts
│   └── App.tsx
```

## Testing

1. Backend tests:
```bash
cd backend
pytest
```

2. Frontend tests:
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

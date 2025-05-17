[📄 **Design Document**](./docs/Document%20Scanner%20Design.md)

> For in-depth technical and architectural details, see:
> - [Backend Design](./docs/Backend%20Design.md): Developer-focused documentation for backend architecture, modules, and implementation.
> - [Frontend Design](./docs/Frontend%20Design.md): Developer-focused documentation for frontend architecture, components, and implementation.

# 📄 Document Scanner for Immigration Documents

A full-stack application designed to scan, classify, and extract information from immigration documents using OCR and AI-assisted processing.

## 🚀 Features

- 📷 Upload document images and PDFs
- 🧠 Classifies document types: `passport`, `driver_license`, or `ead_card`
- 🔍 Extracts key information using AI
- 📝 Allows manual correction of extracted fields
- 🗄️ Stores document history with SQLite
- 🖥️ Modern UI with React + TypeScript
- 🖼️ Image validation for proper resolution (minimum 500x300 pixels)

## 🛠️ Tech Stack

### Backend
- **Framework**: Python, FastAPI
- **Database**: SQLAlchemy with SQLite
- **Document Processing**: OpenAI, Pikepdf, PyMuPDF
- **File Handling**: Pillow

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Components**: Material-UI (MUI)
- **HTTP Client**: Axios
- **File Upload**: React Dropzone

## 🧰 Prerequisites

To run this project, you'll need:

- **Git**: For cloning the repository
  - [Download Git](https://git-scm.com/downloads)
- **Node.js**: v16.0.0 or later and npm
  - [Download Node.js](https://nodejs.org/en/download/)
- **Python**: 3.8 or later
  - [Download Python](https://www.python.org/downloads/)
- **OpenAI API Key**: For document processing
  - [Get API Key](https://platform.openai.com/account/api-keys)

## 📦 Getting Started

### Clone the Repository

```bash
git clone https://github.com/yourusername/document-scanner.git
cd document-scanner
```

### Environment Setup

Set up your environment variables:

1. Create a `.env` file in the `backend` directory:
```
OPENAI_API_KEY=your_openai_api_key
```

2. Create a `.env` file in the `frontend` directory:
```
REACT_APP_API_URL=http://localhost:8000
```

## 🚀 Running the Application

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The backend API will be available at http://localhost:8000

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:3000

## 📱 Using the Application

1. Navigate to http://localhost:3000 in your browser
2. Use the document upload area to upload an image or PDF
3. The system will process and classify the document
4. Review and correct the extracted information if needed
5. Save the document to view it in your document history

## 🧪 Testing

This project includes comprehensive automated tests for both the backend (FastAPI) and frontend (React/TypeScript) to ensure reliability and maintainability.

### Testing Overview
- **Backend:** Uses `pytest` for unit, integration, and API endpoint tests.
- **Frontend:** Uses [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) and [Jest](https://jestjs.io/) for component and integration tests.

---

### Backend Testing Details

**Run all backend tests:**
```bash
cd backend
pytest
```

**Run a specific test file:**
```bash
pytest tests/test_document_processing.py
```

- **Test location:** All backend tests are in `backend/tests/`.
- **Coverage:**
  - Document classification (passport, driver license, EAD card)
  - Field extraction and validation
  - PDF/image upload handling (including edge cases: large files, low-res images)
  - Field correction and persistence
  - Full API endpoint integration
- **Environment:**
  - Uses a test SQLite database (see `test.db` or in-memory)
  - Requires a valid or dummy `OPENAI_API_KEY` in `.env` (can use a mock for local testing)
- **Test coverage report (optional):**
  ```bash
  pytest --cov=.
  ```

---

### Frontend Testing Details

**Run all frontend tests:**
```bash
cd frontend
npm test
```

**Run a specific test file:**
```bash
npm test -- src/components/DocumentFields.test.tsx
```

- **Test location:** Tests are colocated with components (e.g., `src/components/ComponentName.test.tsx`) or in `src/__tests__/`.
- **Coverage:**
  - UI interaction (upload, edit, delete, select)
  - Field validation and correction
  - Error handling and empty states
  - Integration: simulates user flows (upload, edit, save, delete)
- **Debugging:**
  - Use `npm test -- --watch` to run tests interactively
  - Use `npm test -- --coverage` for a coverage report

---

### Troubleshooting
- **Backend:**
  - Ensure the test database is clean before running tests (`test.db` or in-memory)
  - If you see OpenAI API errors, use a dummy key or mock the API in tests
- **Frontend:**
  - If tests fail due to module mocks, check that all required modules are mocked correctly
  - Ensure environment variables (e.g., `REACT_APP_API_URL`) are set for test runs

---

### Contribution Tips
- **Backend:**
  - Add new tests in `backend/tests/` for new endpoints or features
  - Use fixtures for test data and database setup/teardown
- **Frontend:**
  - Add or update tests alongside new or modified components
  - Prefer [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) queries for resilient tests
- **General:**
  - Run all tests before submitting a pull request
  - Follow existing code style and linting rules

---

### Additional Resources
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [React Testing Library docs](https://testing-library.com/docs/)
- [Jest documentation](https://jestjs.io/docs/getting-started)

---

## 📚 API Documentation

FastAPI provides automatic API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 🎯 API Endpoints

### Document Processing

- `POST /api/documents` - Upload and process a document
- `GET /api/documents` - List all documents
- `GET /api/documents/{document_id}` - Get document details
- `PUT /api/documents/{document_id}`
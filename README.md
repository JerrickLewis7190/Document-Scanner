<!-- Badges -->
![GitHub repo size](https://img.shields.io/github/repo-size/JerrickLewis7190/document-scanner)
![GitHub last commit](https://img.shields.io/github/last-commit/JerrickLewis7190/document-scanner)
![GitHub issues](https://img.shields.io/github/issues/JerrickLewis7190/document-scanner)
![GitHub pull requests](https://img.shields.io/github/issues-pr/JerrickLewis7190/document-scanner)
![License](https://img.shields.io/github/license/JerrickLewis7190/document-scanner)
<!-- Uncomment and update these if you set up CI or coverage -->
<!-- ![Build Status](https://github.com/JerrickLewis7190/document-scanner/actions/workflows/ci.yml/badge.svg) -->
<!-- ![Coverage Status](https://coveralls.io/repos/github/JerrickLewis7190/document-scanner/badge.svg?branch=main) -->

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
git clone https://github.com/JerrickLewis7190/document-scanner.git
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
   .venv\Scripts\activate
   
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

## 📁 Sample Images and PDFs

Sample test files are provided in [test_data/Images/](./test_data/Images/) and [test_data/PDFs/](./test_data/PDFs/) folders:

- [test_data/Images/](./test_data/Images/)
  - `test_driver_license.png` — Sample driver's license image for testing
  - `test_ead_card.png` — Sample EAD card image for testing
  - `test_passport.png` — Sample passport image for testing

- [test_data/PDFs/](./test_data/PDFs/)
  - `test_driver_license.pdf` — Sample driver's license PDF for testing
  - `test_ead_card.pdf` — Sample EAD card PDF for testing
  - `test_passport.pdf` — Sample passport PDF for testing

These files are used in automated tests and can also be used to manually try out the application's upload and extraction features. Feel free to add your own sample documents for further testing or demonstration.

## 🧪 Testing

This project includes comprehensive automated tests for both the backend (FastAPI) and frontend (React/TypeScript) to ensure reliability and maintainability.

### Testing Overview
- **Backend:** Uses `pytest` for unit, integration, and API endpoint tests.
- **Frontend:** Uses [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) and [Jest](https://jestjs.io/) for component and integration tests.

---

> **Note:** The `test_data/` directory contains all test data (e.g., sample images) used by tests. All backend test scripts are in `backend/tests/` (including standalone tests in `backend/tests/standalone/`), and frontend tests are colocated with components or in `frontend/src/__tests__/`.

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

- **Test location:** All backend tests are in [backend/tests/](./backend/tests/).
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
```
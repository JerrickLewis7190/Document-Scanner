# 📄 Document Scanner for Immigration Documents

A full-stack application designed to scan, classify, and extract information from immigration documents using OCR and AI-assisted processing.

## 🚀 Features

- 📷 Upload document images and PDFs
- 🧠 Classifies document types: `passport`, `driver_license`, or `ead_card`
- 🔍 Extracts key information using AI
- 📝 Allows manual correction of extracted fields
- 🗄️ Stores document history with SQLite
- 🖥️ Modern UI with React + TypeScript

## 🛠️ Tech Stack

### Backend
- **Framework**: Python, FastAPI
- **Database**: SQLAlchemy with SQLite
- **Document Processing**: OpenAI, PDF2Image
- **File Handling**: Pillow, PyMuPDF

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Components**: Material-UI (MUI)
- **HTTP Client**: Axios
- **File Upload**: React Dropzone

## 📂 Project Structure

```
Document-Scanner/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   ├── logs/               # Application logs
│   ├── uploads/            # Stored documents
│   ├── sample_documents/   # Test document samples
│   ├── tests/              # Backend tests
│   └── main.py             # FastAPI application
├── frontend/               # React/TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   └── package.json
├── Images/                 # Project images
└── PDFs/                   # Project PDFs
```

## 🧪 Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
   
2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. (Optional) Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. Run the FastAPI server:
   ```sh
   python main.py
   ```
   The API will be available at http://localhost:8000
   
   You can also run with uvicorn directly:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Verify the server is running by accessing the Swagger UI at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. (Optional) Create a `.env` file in the frontend directory if you need to customize the backend URL:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

4. Start the development server:
   ```sh
   npm start
   ```
   The application will be available at http://localhost:3000

## 🔄 Running Both Applications

For the full application experience, you'll need to run both the backend and frontend simultaneously:

1. Start the backend server in one terminal:
   ```sh
   cd backend
   .venv\Scripts\activate  # On Windows
   python main.py
   ```

2. Start the frontend server in another terminal:
   ```sh
   cd frontend
   npm start
   ```

3. Access the application at http://localhost:3000 in your browser

## 🔄 API Endpoints

- `POST /api/documents` - Process and store a new document
- `GET /api/documents` - Get list of processed documents
- `GET /api/documents/{id}` - Get a specific document
- `PATCH /api/documents/{id}` - Update document fields
- `DELETE /api/documents/{id}` - Delete a specific document
- `DELETE /api/documents` - Delete all documents
- `GET /health` - Health check endpoint

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 License

This project is licensed under the MIT License.

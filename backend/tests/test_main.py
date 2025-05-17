import io
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from main import app, UPLOAD_DIR

client = TestClient(app)

# Get the absolute path to the test files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'Images')
PDFS_DIR = os.path.join(BASE_DIR, 'PDFs')

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_module():
    """Setup test database and upload directory"""
    Base.metadata.create_all(bind=engine)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def teardown_module():
    """Cleanup after all tests"""
    # Close all database connections
    engine.dispose()
    
    # Remove test database
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    # Clean up upload directory
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)

def cleanup_after_test():
    """Cleanup after each test"""
    # Clean database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Clean upload directory
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

def test_process_passport_image():
    """Test processing a passport image"""
    try:
        with open(os.path.join(IMAGES_DIR, 'Passport Test Image.png'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("passport.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "passport"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_drivers_license_image():
    """Test processing a driver's license image"""
    try:
        with open(os.path.join(IMAGES_DIR, 'Drivers license Test Image.png'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("license.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "drivers_license"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_ead_image():
    """Test processing an EAD card image"""
    try:
        with open(os.path.join(IMAGES_DIR, 'EAD Test Image.png'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("ead.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "ead"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_passport_pdf():
    """Test processing a passport PDF"""
    try:
        with open(os.path.join(PDFS_DIR, 'sample_A_United_States_passport_issued_to_John_Michael_Do.pdf'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("passport.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "passport"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_drivers_license_pdf():
    """Test processing a driver's license PDF"""
    try:
        with open(os.path.join(PDFS_DIR, "sample_A_digital_photograph_of_a_United_States_driver's_l.pdf"), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("license.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "drivers_license"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_ead_pdf():
    """Test processing an EAD card PDF"""
    try:
        with open(os.path.join(PDFS_DIR, 'sample_EAD_card_matched.pdf'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("ead.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "ead"
        assert "document_content" in data
    finally:
        cleanup_after_test()

def test_process_invalid_file():
    """Test processing an invalid file"""
    try:
        # Create an invalid PDF file
        invalid_content = b"This is not a valid PDF file"
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("invalid.pdf", io.BytesIO(invalid_content), "application/pdf")},
        )
        assert response.status_code == 400
        assert "malformed" in response.json()["detail"].lower() or "corrupted" in response.json()["detail"].lower()
    finally:
        cleanup_after_test()

def test_process_unsupported_file_type():
    """Test processing an unsupported file type"""
    try:
        response = client.post(
            "/api/documents/process",
            files={"file": ("test.txt", io.BytesIO(b"test"), "text/plain")},
        )
        assert response.status_code == 400
        assert "invalid file type" in response.json()["detail"].lower()
    finally:
        cleanup_after_test()

def test_process_large_file():
    """Test processing a file that exceeds size limit"""
    try:
        # Create a large file (11MB)
        large_content = b"0" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/documents/process",
            files={"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")},
        )
        assert response.status_code == 400
        assert "file too large" in response.json()["detail"].lower()
    finally:
        cleanup_after_test()

def test_delete_document_success():
    """Test successful document deletion"""
    try:
        # First create a document
        with open(os.path.join(IMAGES_DIR, 'Passport Test Image.png'), 'rb') as f:
            file_content = f.read()
        
        # Upload document
        response = client.post(
            "/api/documents/process",
            files={"file": ("passport.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        document_id = data["id"]
        
        # Delete document
        response = client.delete(f"/api/documents/{document_id}")
        assert response.status_code == 200
        assert "successfully deleted" in response.json()["message"]
        
        # Verify it's gone
        response = client.get(f"/api/documents/{document_id}")
        assert response.status_code == 404
    finally:
        cleanup_after_test()

def test_delete_nonexistent_document():
    """Test deleting a non-existent document"""
    try:
        response = client.delete("/api/documents/99999")
        assert response.status_code == 404
        assert "Document not found" in response.json()["detail"]
    finally:
        cleanup_after_test() 
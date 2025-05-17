import io
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from main import app, UPLOAD_DIR
import pytest
from datetime import datetime
import json
from io import BytesIO
from PIL import Image

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
            "/api/documents",
            files={"file": ("passport.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "passport"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_drivers_license_image():
    """Test processing a driver's license image"""
    try:
        with open(os.path.join(IMAGES_DIR, 'test_driver_license.png'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents",
            files={"file": ("license.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "drivers_license"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_ead_image():
    """Test processing an EAD card image"""
    try:
        with open(os.path.join(IMAGES_DIR, 'EAD Test Image.png'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents",
            files={"file": ("ead.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "ead"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_passport_pdf():
    """Test processing a passport PDF"""
    try:
        with open(os.path.join(PDFS_DIR, 'test_passport.pdf'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents",
            files={"file": ("passport.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "passport"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_drivers_license_pdf():
    """Test processing a driver's license PDF"""
    try:
        with open(os.path.join(PDFS_DIR, 'test_driver_license.pdf'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents",
            files={"file": ("license.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "drivers_license"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_ead_card_pdf():
    """Test processing an EAD card PDF"""
    try:
        with open(os.path.join(PDFS_DIR, 'test_ead_card.pdf'), 'rb') as f:
            file_content = f.read()
        
        response = client.post(
            "/api/documents",
            files={"file": ("ead_card.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "ead_card"
        assert "fields" in data
    finally:
        cleanup_after_test()

def test_process_invalid_file():
    """Test processing an invalid file"""
    try:
        # Create an invalid PDF file
        invalid_content = b"This is not a valid PDF file"
        
        response = client.post(
            "/api/documents",
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
            "/api/documents",
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
            "/api/documents",
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
            "/api/documents",
            files={"file": ("passport.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200
        doc_id = response.json()["id"]
        
        # Delete document
        response = client.delete(f"/api/documents/{doc_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify document is deleted
        response = client.get(f"/api/documents/{doc_id}")
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

# Setup and teardown for each test
@pytest.fixture(scope="function")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Use our test database
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

# Override the get_db dependency
@pytest.fixture(scope="function")
def client(test_db):
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# Test data
@pytest.fixture
def test_document(test_db):
    document = Document(
        filename="test_file.jpg",
        document_type="drivers_license",
        extracted_fields={
            "license_number": "A1234567",
            "name": {
                "first_name": "John",
                "last_name": "Smith"
            },
            "date_of_birth": "1990-01-15",
            "expiration_date": "2025-01-15",
            "address": "123 Main St, Anytown, USA"
        },
        created_at=datetime.utcnow()
    )
    test_db.add(document)
    test_db.commit()
    test_db.refresh(document)
    
    # Add extracted fields
    fields = [
        ExtractedField(
            document_id=document.id,
            field_name="license_number",
            field_value="A1234567",
            corrected=False
        ),
        ExtractedField(
            document_id=document.id,
            field_name="date_of_birth",
            field_value="1990-01-15",
            corrected=False
        )
    ]
    test_db.add_all(fields)
    test_db.commit()
    
    return document

# Test GET /health
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Test GET /documents
def test_get_documents(client, test_document):
    response = client.get("/api/documents")
    assert response.status_code == 200
    documents = response.json()
    assert len(documents) == 1
    assert documents[0]["id"] == test_document.id

# Test GET /documents/{id}
def test_get_document(client, test_document):
    response = client.get(f"/api/documents/{test_document.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_document.id
    assert data["document_type"] == "drivers_license"
    assert data["document_content"]["license_number"] == "A1234567"

# Test DELETE /documents/{id}
def test_delete_document(client, test_document, test_db):
    response = client.delete(f"/api/documents/{test_document.id}")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # Verify document is deleted
    document = test_db.query(Document).filter(Document.id == test_document.id).first()
    assert document is None

# Test field correction persistence
def test_field_correction_persistence(client, test_document, test_db):
    """Test that PATCHing corrected fields updates the database and is reflected in subsequent GETs."""
    # Define the correction
    correction = {
        "fields": [
            {
                "field_name": "license_number",
                "field_value": "B9876543"  # Corrected value
            },
            {
                "field_name": "date_of_birth",
                "field_value": "1991-02-20"  # Corrected value
            }
        ]
    }
    
    # Send the PATCH request
    response = client.patch(
        f"/api/documents/{test_document.id}",
        json=correction
    )
    
    # Check response
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["document_content"]["license_number"] == "B9876543"
    assert updated_data["document_content"]["date_of_birth"] == "1991-02-20"
    
    # Verify database updates
    # 1. Check document content
    updated_doc = test_db.query(Document).filter(Document.id == test_document.id).first()
    assert updated_doc.extracted_fields["license_number"] == "B9876543"
    assert updated_doc.extracted_fields["date_of_birth"] == "1991-02-20"
    
    # 2. Check extracted fields are marked as corrected
    updated_license = test_db.query(ExtractedField).filter(
        ExtractedField.document_id == test_document.id,
        ExtractedField.field_name == "license_number"
    ).first()
    assert updated_license.field_value == "B9876543"
    assert updated_license.corrected is True
    
    updated_dob = test_db.query(ExtractedField).filter(
        ExtractedField.document_id == test_document.id,
        ExtractedField.field_name == "date_of_birth"
    ).first()
    assert updated_dob.field_value == "1991-02-20"
    assert updated_dob.corrected is True
    
    # 3. Verify GET returns updated values
    get_response = client.get(f"/api/documents/{test_document.id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["document_content"]["license_number"] == "B9876543"
    assert get_data["document_content"]["date_of_birth"] == "1991-02-20"

# Complete API Endpoint Integration Tests
def test_api_document_lifecycle(client, test_db):
    """Test the complete document lifecycle through API endpoints"""
    # 1. Create a test image file
    test_image = Image.new('RGB', (800, 600), color='white')
    image_bytes = io.BytesIO()
    test_image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    # 2. POST: Upload a new document
    response = client.post(
        "/api/documents",
        files={"file": ("test_document.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    document_data = response.json()
    document_id = document_data["id"]
    
    # Verify document was created
    assert document_data["filename"] == "test_document.jpg"
    assert "document_type" in document_data
    assert "document_content" in document_data
    
    # 3. GET: Retrieve all documents
    response = client.get("/api/documents")
    assert response.status_code == 200
    documents = response.json()
    assert len(documents) >= 1
    assert any(doc["id"] == document_id for doc in documents)
    
    # 4. GET: Retrieve specific document
    response = client.get(f"/api/documents/{document_id}")
    assert response.status_code == 200
    document = response.json()
    assert document["id"] == document_id
    
    # 5. PATCH: Update document fields
    original_license = document["document_content"].get("license_number", "A1234567")
    update_data = {
        "fields": [
            {
                "field_name": "license_number",
                "field_value": "CORRECTED123"
            }
        ]
    }
    
    response = client.patch(
        f"/api/documents/{document_id}",
        json=update_data
    )
    assert response.status_code == 200
    updated_doc = response.json()
    assert updated_doc["document_content"]["license_number"] == "CORRECTED123"
    
    # 6. GET: Verify update was persisted
    response = client.get(f"/api/documents/{document_id}")
    assert response.status_code == 200
    document = response.json()
    assert document["document_content"]["license_number"] == "CORRECTED123"
    
    # 7. DELETE: Remove document
    response = client.delete(f"/api/documents/{document_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # 8. GET: Verify document was deleted
    response = client.get(f"/api/documents/{document_id}")
    assert response.status_code == 404

def test_api_error_handling(client):
    """Test API error handling"""
    # 1. GET non-existent document
    response = client.get("/api/documents/9999")
    assert response.status_code == 404
    assert "Document not found" in response.json()["detail"]
    
    # 2. POST invalid file (empty)
    response = client.post(
        "/api/documents",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    
    # 3. POST invalid file (not an image)
    response = client.post(
        "/api/documents",
        files={"file": ("text.txt", b"This is not an image", "text/plain")}
    )
    assert response.status_code == 400
    
    # 4. PATCH non-existent document
    update_data = {
        "fields": [
            {
                "field_name": "license_number",
                "field_value": "ABCDEF"
            }
        ]
    }
    response = client.patch("/api/documents/9999", json=update_data)
    assert response.status_code == 404
    
    # 5. DELETE non-existent document
    response = client.delete("/api/documents/9999")
    assert response.status_code == 404 
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import Dict
import aiofiles
import os
from datetime import datetime
import logging

from app.database import get_db, engine
from app.models import Base, Document
from app.schemas import DocumentResponse, Document as DocumentSchema
from app.services.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Document Scanner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Initialize document processor
document_processor = DocumentProcessor()

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
if not os.path.exists(UPLOAD_DIR):
    logger.info(f"Creating upload directory at: {UPLOAD_DIR}")
    os.makedirs(UPLOAD_DIR)

@app.post("/api/documents/process", response_model=DocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Process a document image and extract information
    """
    try:
        # Read file contents
        contents = await file.read()
        
        # Process the document
        doc_type, extracted_fields = document_processor.process_image(contents)
        
        # Save the file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(contents)
        
        # Create database record
        db_document = Document(
            filename=file.filename,
            document_type=doc_type,
            extracted_fields=extracted_fields
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return DocumentResponse(
            document_type=doc_type,
            document_content=extracted_fields
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=list[DocumentSchema])
def get_documents(db: Session = Depends(get_db)):
    """
    Get all processed documents
    """
    return db.query(Document).all()

@app.put("/api/documents/{document_id}/correct")
def correct_fields(
    document_id: int,
    corrected_fields: Dict,
    db: Session = Depends(get_db)
):
    """
    Update document fields with corrections
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.corrected_fields = corrected_fields
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    return document

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
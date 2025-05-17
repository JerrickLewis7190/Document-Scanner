from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import logging

from ..database import get_db
from ..schemas import (
    Document,
    DocumentCreate,
    DocumentResponse,
    Field
)
from ..models.db_models import Document as DocumentModel
from ..services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

document_processor = DocumentProcessor()

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Process and store a new document"""
    logger.info(f"Processing new document: {file.filename}")
    try:
        logger.debug("Reading file contents...")
        contents = await file.read()
        
        # Process the document
        logger.info("Processing document with document processor...")
        doc_type, extracted_fields = document_processor.process_image(contents)
        logger.info(f"Document classified as: {doc_type}")
        logger.debug(f"Extracted fields: {extracted_fields}")
        
        # Create document record
        logger.debug("Creating database record...")
        db_document = DocumentModel(
            filename=file.filename,
            document_type=doc_type,
            extracted_fields=extracted_fields
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        logger.info(f"Document {db_document.id} saved successfully")
        
        return DocumentResponse(
            id=db_document.id,
            filename=file.filename,
            document_type=doc_type,
            created_at=db_document.created_at,
            fields=[Field(**field) for field in extracted_fields]
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of processed documents"""
    logger.info(f"Fetching documents (skip={skip}, limit={limit})")
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    logger.debug(f"Found {len(documents)} documents")
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            document_type=doc.document_type,
            created_at=doc.created_at,
            fields=[Field(**field) for field in doc.extracted_fields]
        )
        for doc in documents
    ]

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    logger.info(f"Fetching document with ID: {document_id}")
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        logger.warning(f"Document with ID {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.debug(f"Found document: {document.filename}")
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        document_type=document.document_type,
        created_at=document.created_at,
        fields=[Field(**field) for field in document.extracted_fields]
    )

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific document"""
    logger.info(f"Deleting document with ID: {document_id}")
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        logger.warning(f"Document with ID {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.debug(f"Deleting document: {document.filename}")
    db.delete(document)
    db.commit()
    logger.info(f"Document {document_id} deleted successfully")
    return {"status": "success"}

@router.delete("/documents")
def delete_all_documents(
    db: Session = Depends(get_db)
):
    """Delete all documents"""
    logger.info("Deleting all documents")
    count = db.query(DocumentModel).count()
    db.query(DocumentModel).delete()
    db.commit()
    logger.info(f"Successfully deleted {count} documents")
    return {"status": "success"} 
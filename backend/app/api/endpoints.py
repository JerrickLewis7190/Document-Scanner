from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from datetime import datetime
from pathlib import Path

from ..database import get_db
from ..models.db_models import Document as DocumentModel, ExtractedField
from ..models.schemas import DocumentResponse, ExtractedFieldBase as Field, UpdateFieldsRequest
from ..services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

document_processor = DocumentProcessor()

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document image
    """
    try:
        # Read file contents
        contents = await file.read()
        
        # Save the uploaded file to the uploads directory
        upload_dir = Path(__file__).parent.parent.parent / "uploads"
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename
        logger.debug(f"Saving uploaded file to: {file_path.resolve()}")
        try:
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as file_exc:
            logger.error(f"Failed to save file to {file_path.resolve()}: {file_exc}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {file_exc}")
        
        # Initialize document processor
        document_processor = DocumentProcessor()
        
        # Process the image
        doc_type, extracted_fields, error_msg = document_processor.process_image(contents)
        
        if error_msg:
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Convert extracted fields to dictionary format
        document_content = {
            field['field_name']: field['field_value']
            for field in extracted_fields
        }
        
        # Create document in database
        document = DocumentModel(
            filename=file.filename,
            document_type=doc_type,
            extracted_fields=document_content,  # Store as JSON in document
            created_at=datetime.utcnow()
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create extracted fields in database
        for field in extracted_fields:
            extracted_field = ExtractedField(
                document_id=document.id,
                field_name=field['field_name'],
                field_value=field['field_value'],
                corrected=False
            )
            db.add(extracted_field)
        
        db.commit()
        
        # Return response in correct format
        return DocumentResponse(
            id=document.id,
            document_type=doc_type,
            document_content=document_content,
            filename=file.filename,
            image_url=f"/uploads/{file.filename}"
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

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
            document_content=doc.extracted_fields,
            image_url=f"/uploads/{doc.filename}"
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
        document_content=document.extracted_fields,
        image_url=f"/uploads/{document.filename}"
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

@router.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document_fields(
    document_id: int,
    request: UpdateFieldsRequest,
    db: Session = Depends(get_db)
):
    """Update specific fields in a document"""
    logger.info(f"Updating fields for document {document_id}")
    
    # Get document
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        logger.warning(f"Document with ID {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update fields in document_content
    updated_content = document.extracted_fields.copy()
    for field in request.fields:
        if field.field_name != 'document_type':  # Prevent document_type from being changed
            updated_content[field.field_name] = field.field_value
            
            # Update or create ExtractedField
            extracted_field = db.query(ExtractedField).filter(
                ExtractedField.document_id == document_id,
                ExtractedField.field_name == field.field_name
            ).first()
            
            if extracted_field:
                extracted_field.field_value = field.field_value
                extracted_field.corrected = True
            else:
                new_field = ExtractedField(
                    document_id=document_id,
                    field_name=field.field_name,
                    field_value=field.field_value,
                    corrected=True
                )
                db.add(new_field)
    
    # Update document
    document.extracted_fields = updated_content
    db.commit()
    db.refresh(document)
    
    logger.info(f"Successfully updated fields for document {document_id}")
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        document_type=document.document_type,
        document_content=document.extracted_fields,
        image_url=f"/uploads/{document.filename}"
    ) 
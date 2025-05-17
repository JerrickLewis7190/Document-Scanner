from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import db_models, schemas

def create_document(db: Session, document: schemas.DocumentCreate) -> db_models.Document:
    db_document = db_models.Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int) -> Optional[db_models.Document]:
    return db.query(db_models.Document).filter(db_models.Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Document]:
    return db.query(db_models.Document).offset(skip).limit(limit).all()

def delete_document(db: Session, document_id: int) -> bool:
    document = db.query(db_models.Document).filter(db_models.Document.id == document_id).first()
    if document:
        db.delete(document)
        db.commit()
        return True
    return False

def delete_all_documents(db: Session) -> bool:
    db.query(db_models.Document).delete()
    db.commit()
    return True

def create_extracted_field(
    db: Session, field: schemas.ExtractedFieldCreate, document_id: int
) -> db_models.ExtractedField:
    db_field = db_models.ExtractedField(**field.dict(), document_id=document_id)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

def update_extracted_field(
    db: Session, field_id: int, field: schemas.ExtractedFieldCreate
) -> Optional[db_models.ExtractedField]:
    db_field = db.query(db_models.ExtractedField).filter(db_models.ExtractedField.id == field_id).first()
    if db_field:
        for key, value in field.dict().items():
            setattr(db_field, key, value)
        db.commit()
        db.refresh(db_field)
    return db_field 
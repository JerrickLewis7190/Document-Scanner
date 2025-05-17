from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    document_type: str

class DocumentCreate(DocumentBase):
    pass

class Field(BaseModel):
    field_name: str
    field_value: str
    corrected: bool = False

class Document(DocumentBase):
    id: int
    created_at: datetime
    fields: List[Field]

    class Config:
        from_attributes = True

class DocumentResponse(Document):
    pass

class DocumentClassification(BaseModel):
    document_type: str
    confidence: float

class FieldExtractionRequest(BaseModel):
    document_type: str
    text_content: str

class FieldExtractionResponse(BaseModel):
    fields: List[Field] 
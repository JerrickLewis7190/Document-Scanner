from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ExtractedFieldBase(BaseModel):
    field_name: str
    field_value: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_correction: bool = False
    error_message: Optional[str] = None

class ExtractedFieldCreate(ExtractedFieldBase):
    pass

class ExtractedField(ExtractedFieldBase):
    id: int
    document_id: int

    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    filename: str
    document_type: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_at: datetime
    fields: List[ExtractedField]

    class Config:
        orm_mode = True

class DocumentResponse(BaseModel):
    id: int
    document_type: str
    document_content: Dict[str, str]
    filename: str
    image_url: str  # URL to access the original uploaded image

class DocumentClassification(BaseModel):
    document_type: str
    confidence: float

class FieldExtractionRequest(BaseModel):
    document_type: str
    text_content: str

class FieldExtractionResponse(BaseModel):
    fields: List[ExtractedFieldBase]

class UpdateFieldsRequest(BaseModel):
    fields: List[ExtractedFieldBase] 
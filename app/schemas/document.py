from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    vehicle_id: int
    doc_type: str
    original_filename: str
    mime_type: str
    uploaded_at: datetime
    extracted: bool

    model_config = {"from_attributes": True}


class ExtractionResult(BaseModel):
    success: bool
    doc_type: str
    message: str
    data: Optional[dict] = None

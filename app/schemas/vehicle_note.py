from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VehicleNoteCreate(BaseModel):
    content: str
    pinned: bool = False


class VehicleNoteUpdate(BaseModel):
    content: Optional[str] = None
    pinned: Optional[bool] = None


class VehicleNoteOut(BaseModel):
    id: int
    vehicle_id: int
    content: str
    pinned: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

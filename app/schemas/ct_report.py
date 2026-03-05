from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class CTDefectOut(BaseModel):
    id: int
    code: Optional[str]
    description: str
    severity: str
    category: Optional[str]

    model_config = {"from_attributes": True}


class CTReportOut(BaseModel):
    id: int
    vehicle_id: int
    document_id: Optional[int]
    date: date
    mileage: Optional[int]
    center_name: Optional[str]
    result: str
    next_due_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    defects: list[CTDefectOut] = []

    model_config = {"from_attributes": True}

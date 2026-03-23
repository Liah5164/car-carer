from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class TaxInsuranceCreate(BaseModel):
    record_type: str  # "insurance", "vignette", "carbon_tax", "registration", "parking", "toll_tag", "other"
    name: str
    provider: Optional[str] = None
    date: date
    cost: float
    next_renewal_date: Optional[date] = None
    renewal_frequency: Optional[str] = None  # "monthly", "annual", "biennial", "one_time"
    notes: Optional[str] = None
    document_id: Optional[int] = None


class TaxInsuranceUpdate(BaseModel):
    record_type: Optional[str] = None
    name: Optional[str] = None
    provider: Optional[str] = None
    date: Optional[date] = None
    cost: Optional[float] = None
    next_renewal_date: Optional[date] = None
    renewal_frequency: Optional[str] = None
    notes: Optional[str] = None
    document_id: Optional[int] = None


class TaxInsuranceOut(BaseModel):
    id: int
    vehicle_id: int
    record_type: str
    name: str
    provider: Optional[str]
    date: date
    cost: float
    next_renewal_date: Optional[date]
    renewal_frequency: Optional[str]
    notes: Optional[str]
    document_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    trigger_mode: str  # "km_only", "date_only", "km_or_date"
    km_interval: Optional[int] = None
    months_interval: Optional[int] = None
    last_performed_km: Optional[int] = None
    last_performed_date: Optional[date] = None
    is_recurring: bool = True
    active: bool = True


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    trigger_mode: Optional[str] = None
    km_interval: Optional[int] = None
    months_interval: Optional[int] = None
    last_performed_km: Optional[int] = None
    last_performed_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    active: Optional[bool] = None


class ReminderOut(BaseModel):
    id: int
    vehicle_id: int
    title: str
    description: Optional[str]
    trigger_mode: str
    km_interval: Optional[int]
    months_interval: Optional[int]
    last_performed_km: Optional[int]
    last_performed_date: Optional[date]
    is_recurring: bool
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

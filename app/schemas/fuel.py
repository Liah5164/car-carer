from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class FuelRecordCreate(BaseModel):
    date: date
    mileage: Optional[int] = None
    liters: float
    price_total: float
    price_per_liter: Optional[float] = None
    station_name: Optional[str] = None
    fuel_type: Optional[str] = None
    is_full_tank: bool = True
    notes: Optional[str] = None
    document_id: Optional[int] = None


class FuelRecordUpdate(BaseModel):
    date: Optional[date] = None
    mileage: Optional[int] = None
    liters: Optional[float] = None
    price_total: Optional[float] = None
    price_per_liter: Optional[float] = None
    station_name: Optional[str] = None
    fuel_type: Optional[str] = None
    is_full_tank: Optional[bool] = None
    notes: Optional[str] = None
    document_id: Optional[int] = None


class FuelRecordOut(BaseModel):
    id: int
    vehicle_id: int
    date: date
    mileage: Optional[int]
    liters: float
    price_total: float
    price_per_liter: Optional[float]
    station_name: Optional[str]
    fuel_type: Optional[str]
    is_full_tank: bool
    notes: Optional[str]
    document_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

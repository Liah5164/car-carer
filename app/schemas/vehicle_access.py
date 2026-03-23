from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VehicleAccessCreate(BaseModel):
    user_id: int
    role: str  # "owner", "editor", "viewer"


class VehicleAccessUpdate(BaseModel):
    role: str  # "owner", "editor", "viewer"


class VehicleAccessOut(BaseModel):
    id: int
    vehicle_id: int
    user_id: int
    role: str
    granted_by_user_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

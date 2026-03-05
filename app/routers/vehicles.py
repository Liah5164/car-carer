from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vehicle, MaintenanceEvent, CTReport, Document
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut, VehicleSummary

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleSummary])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).order_by(Vehicle.name).all()
    results = []
    for v in vehicles:
        # Last mileage from maintenance or CT
        last_mileage = None
        last_maintenance_date = None

        last_event = (
            db.query(MaintenanceEvent)
            .filter(MaintenanceEvent.vehicle_id == v.id)
            .order_by(MaintenanceEvent.date.desc())
            .first()
        )
        if last_event:
            last_maintenance_date = last_event.date
            if last_event.mileage:
                last_mileage = last_event.mileage

        last_ct = (
            db.query(CTReport)
            .filter(CTReport.vehicle_id == v.id)
            .order_by(CTReport.date.desc())
            .first()
        )
        if last_ct and last_ct.mileage:
            if last_mileage is None or (last_ct.date and last_event and last_ct.date > last_event.date):
                last_mileage = last_ct.mileage

        total_spent = db.query(func.sum(MaintenanceEvent.total_cost)).filter(
            MaintenanceEvent.vehicle_id == v.id,
            MaintenanceEvent.event_type == "invoice",
        ).scalar() or 0

        doc_count = db.query(func.count(Document.id)).filter(Document.vehicle_id == v.id).scalar()
        ct_count = db.query(func.count(CTReport.id)).filter(CTReport.vehicle_id == v.id).scalar()

        results.append(VehicleSummary(
            id=v.id,
            name=v.name,
            brand=v.brand,
            model=v.model,
            year=v.year,
            plate_number=v.plate_number,
            last_mileage=last_mileage,
            last_maintenance_date=last_maintenance_date,
            total_spent=total_spent,
            document_count=doc_count,
            ct_count=ct_count,
        ))
    return results


@router.post("", response_model=VehicleOut, status_code=201)
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicule non trouve")
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicule non trouve")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, val)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicule non trouve")
    db.delete(vehicle)
    db.commit()

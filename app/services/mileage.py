"""Shared mileage & fuel consumption service — single source of truth for last known mileage."""

import logging

from sqlalchemy.orm import Session

from app.models import MaintenanceEvent, CTReport, FuelRecord

logger = logging.getLogger(__name__)


def get_last_known_mileage(db: Session, vehicle_id: int) -> int | None:
    """Get the highest known mileage for a vehicle from all sources."""
    logger.debug("Looking up last known mileage — vehicle_id=%d", vehicle_id)
    sources = []

    last_ev = db.query(MaintenanceEvent.mileage).filter(
        MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.mileage.isnot(None)
    ).order_by(MaintenanceEvent.mileage.desc()).first()
    if last_ev:
        sources.append(last_ev[0])

    last_ct = db.query(CTReport.mileage).filter(
        CTReport.vehicle_id == vehicle_id, CTReport.mileage.isnot(None)
    ).order_by(CTReport.mileage.desc()).first()
    if last_ct:
        sources.append(last_ct[0])

    last_fuel = db.query(FuelRecord.mileage).filter(
        FuelRecord.vehicle_id == vehicle_id, FuelRecord.mileage.isnot(None)
    ).order_by(FuelRecord.mileage.desc()).first()
    if last_fuel:
        sources.append(last_fuel[0])

    result = max(sources) if sources else None
    logger.debug("Last known mileage for vehicle_id=%d: %s", vehicle_id, result)
    return result


def calculate_fuel_consumption(db: Session, vehicle_id: int) -> dict:
    """Calculate fuel consumption stats for a vehicle.

    Uses the full-tank-to-full-tank method: consumption between two consecutive
    full tanks is calculated as liters / km_driven * 100 (L/100km).
    Only records with is_full_tank=True and a non-null mileage are used.
    """
    records = db.query(FuelRecord).filter(
        FuelRecord.vehicle_id == vehicle_id,
        FuelRecord.is_full_tank == True,  # noqa: E712
        FuelRecord.mileage.isnot(None)
    ).order_by(FuelRecord.mileage).all()

    if len(records) < 2:
        return {"avg_consumption": None, "total_cost": 0, "total_liters": 0, "records": []}

    consumptions = []
    for i in range(1, len(records)):
        km = records[i].mileage - records[i - 1].mileage
        if km > 0:
            consumption = (records[i].liters / km) * 100  # L/100km
            consumptions.append({
                "date": str(records[i].date),
                "km_driven": km,
                "liters": float(records[i].liters),
                "consumption": round(consumption, 1),
                "cost": float(records[i].price_total),
            })

    avg = sum(c["consumption"] for c in consumptions) / len(consumptions) if consumptions else None
    total_cost = sum(float(r.price_total) for r in records)
    total_liters = sum(float(r.liters) for r in records)

    return {
        "avg_consumption": round(avg, 1) if avg else None,
        "total_cost": round(total_cost, 2),
        "total_liters": round(total_liters, 1),
        "records": consumptions,
    }

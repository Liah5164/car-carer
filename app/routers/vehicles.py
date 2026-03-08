import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response as RawResponse
from sqlalchemy import func, extract
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Vehicle, MaintenanceEvent, MaintenanceItem, CTReport, CTDefect, Document, ShareLink
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut, VehicleSummary
from app.services.analysis import analyze_vehicle
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


# --- Dashboard (multi-vehicle overview) ---

@router.get("/dashboard")
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Multi-vehicle dashboard with health scores and key stats."""
    vehicles = (
        db.query(Vehicle)
        .filter((Vehicle.user_id == user.id) | (Vehicle.user_id.is_(None)))
        .order_by(Vehicle.name)
        .all()
    )
    results = []
    total_spent_all = 0
    for v in vehicles:
        analysis = analyze_vehicle(db, v.id)
        hs = analysis.get("health_score", {})

        spent = db.query(func.sum(MaintenanceEvent.total_cost)).filter(
            MaintenanceEvent.vehicle_id == v.id, MaintenanceEvent.event_type == "invoice"
        ).scalar() or 0
        total_spent_all += float(spent)

        critical_count = len([a for a in analysis.get("alerts", []) if a["level"] == "critical"])
        warning_count = len([a for a in analysis.get("alerts", []) if a["level"] == "warning"])

        last_mileage = None
        last_ev = db.query(MaintenanceEvent).filter(
            MaintenanceEvent.vehicle_id == v.id, MaintenanceEvent.mileage.isnot(None)
        ).order_by(MaintenanceEvent.date.desc()).first()
        if last_ev:
            last_mileage = last_ev.mileage

        results.append({
            "id": v.id, "name": v.name, "brand": v.brand, "model": v.model, "year": v.year,
            "plate_number": v.plate_number,
            "health_score": hs.get("score"), "health_label": hs.get("label"), "health_color": hs.get("color"),
            "critical_alerts": critical_count, "warning_alerts": warning_count,
            "total_spent": round(float(spent), 2), "last_mileage": last_mileage,
        })

    avg_score = round(sum(r["health_score"] or 0 for r in results) / len(results), 1) if results else 0
    return {
        "vehicles": results,
        "summary": {
            "vehicle_count": len(results),
            "avg_health_score": avg_score,
            "total_spent": round(total_spent_all, 2),
            "total_critical": sum(r["critical_alerts"] for r in results),
            "total_warnings": sum(r["warning_alerts"] for r in results),
        },
    }


def _get_vehicle_or_404(vehicle_id: int, user: User, db: Session) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle or (vehicle.user_id and vehicle.user_id != user.id):
        raise HTTPException(404, "Vehicule non trouve")
    return vehicle


@router.get("", response_model=list[VehicleSummary])
def list_vehicles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicles = (
        db.query(Vehicle)
        .filter((Vehicle.user_id == user.id) | (Vehicle.user_id.is_(None)))
        .order_by(Vehicle.name)
        .all()
    )
    results = []
    for v in vehicles:
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
            id=v.id, name=v.name, brand=v.brand, model=v.model, year=v.year,
            plate_number=v.plate_number, last_mileage=last_mileage,
            last_maintenance_date=last_maintenance_date, total_spent=total_spent,
            document_count=doc_count, ct_count=ct_count,
        ))
    return results


@router.post("", response_model=VehicleOut, status_code=201)
def create_vehicle(data: VehicleCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump(), user_id=user.id)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_vehicle_or_404(vehicle_id, user, db)


@router.patch("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = _get_vehicle_or_404(vehicle_id, user, db)
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, val)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = _get_vehicle_or_404(vehicle_id, user, db)
    db.delete(vehicle)
    db.commit()


@router.get("/{vehicle_id}/analysis")
def get_vehicle_analysis(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_vehicle_or_404(vehicle_id, user, db)
    return analyze_vehicle(db, vehicle_id)


@router.get("/{vehicle_id}/stats")
def get_vehicle_stats(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return spending and mileage data for charts."""
    _get_vehicle_or_404(vehicle_id, user, db)

    # Spending by month (invoices only)
    events = (
        db.query(MaintenanceEvent)
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "invoice")
        .order_by(MaintenanceEvent.date)
        .all()
    )
    spending_by_month = {}
    for ev in events:
        if ev.date and ev.total_cost:
            key = ev.date.strftime("%Y-%m")
            spending_by_month[key] = spending_by_month.get(key, 0) + float(ev.total_cost)

    # Mileage timeline (from events + CTs)
    mileage_points = []
    for ev in events:
        if ev.date and ev.mileage:
            mileage_points.append({"date": str(ev.date), "km": ev.mileage, "source": "entretien"})
    cts = (
        db.query(CTReport)
        .filter(CTReport.vehicle_id == vehicle_id)
        .order_by(CTReport.date)
        .all()
    )
    for ct in cts:
        if ct.date and ct.mileage:
            mileage_points.append({"date": str(ct.date), "km": ct.mileage, "source": "CT"})
    mileage_points.sort(key=lambda x: x["date"])

    # Spending by category
    items = (
        db.query(MaintenanceItem)
        .join(MaintenanceEvent)
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "invoice")
        .all()
    )
    spending_by_cat = {}
    for item in items:
        cat = item.category or "autre"
        spending_by_cat[cat] = spending_by_cat.get(cat, 0) + float(item.total_price or 0)

    return {
        "spending_by_month": [{"month": k, "amount": round(v, 2)} for k, v in sorted(spending_by_month.items())],
        "mileage_timeline": mileage_points,
        "spending_by_category": [{"category": k, "amount": round(v, 2)} for k, v in sorted(spending_by_cat.items(), key=lambda x: -x[1])],
    }


@router.get("/{vehicle_id}/export-pdf")
def export_vehicle_pdf(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a PDF report for the vehicle."""
    vehicle = _get_vehicle_or_404(vehicle_id, user, db)
    analysis = analyze_vehicle(db, vehicle_id)

    from app.services.pdf_export import generate_vehicle_pdf
    pdf_bytes = generate_vehicle_pdf(vehicle, analysis, db)

    filename = f"rapport_{vehicle.name.replace(' ', '_')}_{vehicle_id}.pdf"
    return RawResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --- CRUD for maintenance events and CT reports ---

@router.delete("/{vehicle_id}/maintenance/{event_id}", status_code=204)
def delete_maintenance_event(vehicle_id: int, event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_vehicle_or_404(vehicle_id, user, db)
    event = db.get(MaintenanceEvent, event_id)
    if not event or event.vehicle_id != vehicle_id:
        raise HTTPException(404, "Entretien non trouve")
    db.delete(event)
    db.commit()


@router.delete("/{vehicle_id}/ct/{ct_id}", status_code=204)
def delete_ct_report(vehicle_id: int, ct_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_vehicle_or_404(vehicle_id, user, db)
    ct = db.get(CTReport, ct_id)
    if not ct or ct.vehicle_id != vehicle_id:
        raise HTTPException(404, "CT non trouve")
    db.delete(ct)
    db.commit()


# --- Share links ---

@router.post("/{vehicle_id}/share")
def create_share_link(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a share token for read-only access to a vehicle's history."""
    import secrets
    _get_vehicle_or_404(vehicle_id, user, db)
    token = secrets.token_urlsafe(32)
    link = ShareLink(vehicle_id=vehicle_id, token=token)
    db.add(link)
    db.commit()
    db.refresh(link)
    return {"token": token, "id": link.id}


@router.delete("/{vehicle_id}/share/{link_id}", status_code=204)
def revoke_share_link(vehicle_id: int, link_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_vehicle_or_404(vehicle_id, user, db)
    link = db.get(ShareLink, link_id)
    if not link or link.vehicle_id != vehicle_id:
        raise HTTPException(404)
    db.delete(link)
    db.commit()


@router.get("/{vehicle_id}/shares")
def list_share_links(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_vehicle_or_404(vehicle_id, user, db)
    links = db.query(ShareLink).filter(ShareLink.vehicle_id == vehicle_id, ShareLink.active == True).all()
    return [{"id": l.id, "token": l.token, "created_at": str(l.created_at)} for l in links]


# --- CSV Export ---

@router.get("/{vehicle_id}/export-csv")
def export_vehicle_csv(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export full maintenance history as CSV."""
    vehicle = _get_vehicle_or_404(vehicle_id, user, db)
    events = (
        db.query(MaintenanceEvent)
        .options(joinedload(MaintenanceEvent.items))
        .filter(MaintenanceEvent.vehicle_id == vehicle_id)
        .order_by(MaintenanceEvent.date.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Date", "Type", "Garage", "Km", "Description", "Categorie", "Montant HT", "Montant TTC", "Total facture"])
    for ev in events:
        for item in ev.items:
            writer.writerow([
                str(ev.date) if ev.date else "",
                ev.event_type or "",
                ev.garage_name or "",
                ev.mileage or "",
                item.description or "",
                item.category or "",
                f"{item.unit_price:.2f}" if item.unit_price else "",
                f"{item.total_price:.2f}" if item.total_price else "",
                f"{ev.total_cost:.2f}" if ev.total_cost else "",
            ])
    content = output.getvalue().encode("utf-8-sig")  # BOM for Excel
    filename = f"historique_{vehicle.name.replace(' ', '_')}.csv"
    return RawResponse(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --- Maintenance search ---

@router.get("/{vehicle_id}/maintenance-search")
def search_maintenance(
    vehicle_id: int,
    q: str = Query("", description="Recherche dans descriptions"),
    event_type: Optional[str] = Query(None, description="invoice or quote"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search and filter maintenance events."""
    _get_vehicle_or_404(vehicle_id, user, db)
    query = (
        db.query(MaintenanceEvent)
        .options(joinedload(MaintenanceEvent.items))
        .filter(MaintenanceEvent.vehicle_id == vehicle_id)
    )
    if event_type:
        query = query.filter(MaintenanceEvent.event_type == event_type)
    if date_from:
        query = query.filter(MaintenanceEvent.date >= date_from)
    if date_to:
        query = query.filter(MaintenanceEvent.date <= date_to)
    events = query.order_by(MaintenanceEvent.date.desc()).all()

    # Text search in items
    if q.strip():
        q_lower = q.lower()
        filtered = []
        for ev in events:
            match = q_lower in (ev.garage_name or "").lower()
            if not match:
                for item in ev.items:
                    if q_lower in (item.description or "").lower() or q_lower in (item.category or "").lower():
                        match = True
                        break
            if match:
                filtered.append(ev)
        events = filtered

    return [
        {
            "id": ev.id, "date": str(ev.date) if ev.date else None, "event_type": ev.event_type,
            "garage_name": ev.garage_name, "mileage": ev.mileage,
            "total_cost": float(ev.total_cost) if ev.total_cost else None,
            "items": [{"id": i.id, "description": i.description, "category": i.category, "total_price": float(i.total_price) if i.total_price else None} for i in ev.items],
        }
        for ev in events
    ]


# --- Calendar (upcoming maintenance) ---

@router.get("/{vehicle_id}/calendar")
def get_maintenance_calendar(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predict upcoming maintenance based on intervals."""
    _get_vehicle_or_404(vehicle_id, user, db)
    analysis = analyze_vehicle(db, vehicle_id)
    from datetime import date
    from dateutil.relativedelta import relativedelta

    upcoming = []

    # CT due date
    ct_status = analysis.get("current_ct_status")
    if ct_status and ct_status.get("next_due"):
        upcoming.append({
            "type": "Controle technique",
            "due_date": ct_status["next_due"],
            "priority": "high" if ct_status["next_due"] < str(date.today()) else "normal",
            "source": "CT",
        })

    # Maintenance intervals overdue or coming up
    for interval in analysis.get("maintenance_intervals", []):
        if interval["level"] == "warning":
            upcoming.append({
                "type": interval.get("maintenance_type", interval.get("title", "")),
                "due_date": str(date.today()),  # Already overdue
                "priority": "overdue",
                "detail": interval.get("detail", ""),
                "source": "interval",
            })
        elif interval["level"] == "ok" and interval.get("last_date"):
            # Estimate next due
            from app.services.analysis import INTERVALS
            for keywords, max_km, max_months, label in INTERVALS:
                if label == interval.get("maintenance_type"):
                    if max_months and interval["last_date"]:
                        try:
                            last = date.fromisoformat(interval["last_date"])
                            next_due = last + relativedelta(months=max_months)
                            upcoming.append({
                                "type": label,
                                "due_date": str(next_due),
                                "priority": "normal",
                                "source": "interval",
                            })
                        except (ValueError, TypeError):
                            pass
                    break

    upcoming.sort(key=lambda x: x.get("due_date", "9999"))
    return upcoming


# --- Quote comparator ---

@router.get("/{vehicle_id}/compare-quotes")
def compare_quotes(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Compare quotes (devis) for the same vehicle."""
    _get_vehicle_or_404(vehicle_id, user, db)
    quotes = (
        db.query(MaintenanceEvent)
        .options(joinedload(MaintenanceEvent.items))
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "quote")
        .order_by(MaintenanceEvent.date.desc())
        .all()
    )
    if not quotes:
        return {"quotes": [], "comparison": None}

    # Build comparison: group items by category across quotes
    all_categories = set()
    quote_data = []
    for q in quotes:
        items_by_cat = {}
        for item in q.items:
            cat = item.category or item.description or "autre"
            if cat not in items_by_cat:
                items_by_cat[cat] = 0
            items_by_cat[cat] += float(item.total_price or 0)
            all_categories.add(cat)
        quote_data.append({
            "id": q.id, "date": str(q.date) if q.date else None, "garage": q.garage_name,
            "total": float(q.total_cost) if q.total_cost else 0, "items_by_category": items_by_cat,
        })

    return {
        "quotes": quote_data,
        "categories": sorted(all_categories),
    }


# --- Budget forecast ---

@router.get("/{vehicle_id}/budget-forecast")
def get_budget_forecast(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predict annual spending based on historical data and upcoming maintenance."""
    from datetime import date
    from dateutil.relativedelta import relativedelta

    _get_vehicle_or_404(vehicle_id, user, db)

    # Historical: average yearly spending over past years
    events = (
        db.query(MaintenanceEvent)
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "invoice")
        .order_by(MaintenanceEvent.date)
        .all()
    )

    if not events:
        return {"historical_avg": 0, "forecast": 0, "breakdown": [], "yearly_history": []}

    # Yearly spending history
    yearly = {}
    for ev in events:
        if ev.date and ev.total_cost:
            year = ev.date.year
            yearly[year] = yearly.get(year, 0) + float(ev.total_cost)

    yearly_history = [{"year": y, "amount": round(a, 2)} for y, a in sorted(yearly.items())]
    historical_avg = round(sum(yearly.values()) / len(yearly), 2) if yearly else 0

    # Category-based forecast: average cost per category per year
    category_yearly = {}
    for ev in events:
        if ev.date and ev.total_cost:
            for item in ev.items:
                cat = item.category or "autre"
                year = ev.date.year
                key = (cat, year)
                category_yearly[key] = category_yearly.get(key, 0) + float(item.total_price or 0)

    categories = set(k[0] for k in category_yearly)
    years_count = len(yearly) or 1
    breakdown = []
    for cat in sorted(categories):
        total = sum(v for (c, y), v in category_yearly.items() if c == cat)
        avg = round(total / years_count, 2)
        breakdown.append({"category": cat, "yearly_avg": avg})

    breakdown.sort(key=lambda x: -x["yearly_avg"])
    forecast = round(sum(b["yearly_avg"] for b in breakdown), 2)

    return {
        "historical_avg": historical_avg,
        "forecast": forecast,
        "breakdown": breakdown,
        "yearly_history": yearly_history,
    }


# --- Price history (cost tracking by operation type) ---

@router.get("/{vehicle_id}/price-history")
def get_price_history(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Track how prices for common operations have changed over time."""
    _get_vehicle_or_404(vehicle_id, user, db)
    items = (
        db.query(MaintenanceItem, MaintenanceEvent.date, MaintenanceEvent.garage_name)
        .join(MaintenanceEvent)
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "invoice")
        .order_by(MaintenanceEvent.date)
        .all()
    )

    # Group by category
    by_category = {}
    for item, ev_date, garage in items:
        cat = item.category or "autre"
        if cat not in by_category:
            by_category[cat] = []
        if item.total_price:
            by_category[cat].append({
                "date": str(ev_date) if ev_date else None,
                "description": item.description,
                "price": round(float(item.total_price), 2),
                "garage": garage,
            })

    # Only categories with 2+ data points are interesting
    history = {}
    for cat, points in by_category.items():
        if len(points) >= 2:
            history[cat] = points

    return {"categories": history}


# --- Official maintenance booklet PDF ---

@router.get("/{vehicle_id}/export-booklet")
def export_maintenance_booklet(vehicle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate an official-style maintenance booklet PDF."""
    vehicle = _get_vehicle_or_404(vehicle_id, user, db)
    events = (
        db.query(MaintenanceEvent)
        .options(joinedload(MaintenanceEvent.items))
        .filter(MaintenanceEvent.vehicle_id == vehicle_id, MaintenanceEvent.event_type == "invoice")
        .order_by(MaintenanceEvent.date)
        .all()
    )
    cts = (
        db.query(CTReport)
        .options(joinedload(CTReport.defects))
        .filter(CTReport.vehicle_id == vehicle_id)
        .order_by(CTReport.date)
        .all()
    )

    from app.services.pdf_export import generate_booklet_pdf
    pdf_bytes = generate_booklet_pdf(vehicle, events, cts)
    filename = f"carnet_entretien_{vehicle.name.replace(' ', '_')}.pdf"
    return RawResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

import json
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import UPLOAD_PATH
from app.database import get_db
from app.models import Document, Vehicle, MaintenanceEvent, MaintenanceItem, CTReport, CTDefect
from app.schemas.document import DocumentOut, ExtractionResult
from app.schemas.maintenance import MaintenanceEventOut
from app.schemas.ct_report import CTReportOut
from app.services.extraction import extract_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_MIME = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


@router.post("/upload", response_model=ExtractionResult)
async def upload_and_extract(
    vehicle_id: int = Form(...),
    doc_type: str = Form("auto"),  # invoice, ct_report, quote, auto
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicule non trouve")

    mime = file.content_type or "application/octet-stream"
    if mime not in ALLOWED_MIME:
        raise HTTPException(400, f"Type de fichier non supporte: {mime}")

    # Save file
    ext = Path(file.filename).suffix if file.filename else ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_PATH / filename
    content = await file.read()
    file_path.write_bytes(content)

    # Create document record
    doc = Document(
        vehicle_id=vehicle_id,
        doc_type=doc_type if doc_type != "auto" else "unknown",
        file_path=str(file_path),
        original_filename=file.filename or "unknown",
        mime_type=mime,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Extract with Gemini
    try:
        data = await extract_document(str(file_path), doc_type)
    except Exception as e:
        return ExtractionResult(
            success=False, doc_type=doc.doc_type, message=f"Erreur d'extraction: {e}"
        )

    if "error" in data:
        doc.extraction_raw = json.dumps(data, ensure_ascii=False)
        db.commit()
        return ExtractionResult(
            success=False, doc_type=doc.doc_type, message=data["error"], data=data
        )

    # Store raw extraction
    doc.extraction_raw = json.dumps(data, ensure_ascii=False)
    doc.extracted = True

    # Enrich vehicle info from extracted data
    _enrich_vehicle(vehicle, data.get("vehicle_info"))

    # Determine actual doc type from extraction
    actual_type = data.get("doc_type", doc_type)
    if actual_type in ("invoice", "quote"):
        doc.doc_type = actual_type
        event = _create_maintenance_event(db, vehicle_id, doc.id, data)
        db.commit()
        return ExtractionResult(
            success=True,
            doc_type=actual_type,
            message=f"{'Facture' if actual_type == 'invoice' else 'Devis'} extrait(e): {len(data.get('items', []))} lignes",
            data=data,
        )
    elif actual_type == "ct_report" or "defects" in data:
        doc.doc_type = "ct_report"
        ct = _create_ct_report(db, vehicle_id, doc.id, data)
        db.commit()
        return ExtractionResult(
            success=True,
            doc_type="ct_report",
            message=f"CT extrait: {data.get('result', '?')}, {len(data.get('defects', []))} defaut(s)",
            data=data,
        )
    else:
        db.commit()
        return ExtractionResult(
            success=True, doc_type="unknown", message="Document extrait mais type non identifie", data=data
        )


def _enrich_vehicle(vehicle: Vehicle, vehicle_info: dict | None) -> None:
    """Update vehicle fields from extracted document data (only fills blanks)."""
    if not vehicle_info:
        return
    field_map = {
        "brand": "brand",
        "model": "model",
        "year": "year",
        "plate_number": "plate_number",
        "vin": "vin",
        "fuel_type": "fuel_type",
        "owner_count": "owner_count",
    }
    for src_key, dest_attr in field_map.items():
        value = vehicle_info.get(src_key)
        if value and not getattr(vehicle, dest_attr):
            setattr(vehicle, dest_attr, value)


def _create_maintenance_event(db: Session, vehicle_id: int, doc_id: int, data: dict) -> MaintenanceEvent:
    event_date = date.fromisoformat(data["date"]) if data.get("date") else date.today()
    event = MaintenanceEvent(
        vehicle_id=vehicle_id,
        document_id=doc_id,
        date=event_date,
        mileage=data.get("mileage"),
        garage_name=data.get("garage_name"),
        total_cost=data.get("total_cost"),
        notes=data.get("notes"),
        event_type=data.get("doc_type", "invoice"),
    )
    db.add(event)
    db.flush()

    for item_data in data.get("items", []):
        item = MaintenanceItem(
            event_id=event.id,
            description=item_data.get("description", ""),
            category=item_data.get("category"),
            part_name=item_data.get("part_name"),
            quantity=item_data.get("quantity"),
            unit_price=item_data.get("unit_price"),
            labor_cost=item_data.get("labor_cost"),
            total_price=item_data.get("total_price"),
        )
        db.add(item)
    return event


def _create_ct_report(db: Session, vehicle_id: int, doc_id: int, data: dict) -> CTReport:
    ct_date = date.fromisoformat(data["date"]) if data.get("date") else date.today()
    next_due = date.fromisoformat(data["next_due_date"]) if data.get("next_due_date") else None
    ct = CTReport(
        vehicle_id=vehicle_id,
        document_id=doc_id,
        date=ct_date,
        mileage=data.get("mileage"),
        center_name=data.get("center_name"),
        result=data.get("result", "favorable"),
        next_due_date=next_due,
        notes=data.get("notes"),
    )
    db.add(ct)
    db.flush()

    for defect_data in data.get("defects", []):
        defect = CTDefect(
            ct_report_id=ct.id,
            code=defect_data.get("code"),
            description=defect_data.get("description", ""),
            severity=defect_data.get("severity", "mineur"),
            category=defect_data.get("category"),
        )
        db.add(defect)
    return ct


@router.get("/{vehicle_id}", response_model=list[DocumentOut])
def list_documents(vehicle_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.vehicle_id == vehicle_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


@router.get("/{vehicle_id}/maintenance", response_model=list[MaintenanceEventOut])
def list_maintenance(vehicle_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    return (
        db.query(MaintenanceEvent)
        .options(joinedload(MaintenanceEvent.items))
        .filter(MaintenanceEvent.vehicle_id == vehicle_id)
        .order_by(MaintenanceEvent.date.desc())
        .all()
    )


@router.get("/{vehicle_id}/ct-reports", response_model=list[CTReportOut])
def list_ct_reports(vehicle_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    return (
        db.query(CTReport)
        .options(joinedload(CTReport.defects))
        .filter(CTReport.vehicle_id == vehicle_id)
        .order_by(CTReport.date.desc())
        .all()
    )

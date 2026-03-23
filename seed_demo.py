"""Seed Car Carer with realistic demo data for screenshots."""

import sys
import httpx

BASE = "http://127.0.0.1:8200/api"
client = httpx.Client(base_url=BASE, timeout=30)


def seed():
    # ── Register + login ──
    print("Creating demo user...")
    res = client.post("/auth/register", json={"email": "demo@carcarer.app", "password": "demo123456"})
    if res.status_code == 409:
        res = client.post("/auth/login", json={"email": "demo@carcarer.app", "password": "demo123456"})
    if res.status_code not in (200, 201):
        print(f"Auth failed: {res.status_code} {res.text}")
        sys.exit(1)
    cookies = dict(res.cookies)
    client.cookies = cookies
    print(f"  Logged in as demo@carcarer.app")

    # ── Create 2nd user for sharing demo ──
    print("Creating garage user...")
    res2 = client.post("/auth/register", json={"email": "garage.martin@example.com", "password": "garage123456"})
    # Re-login as demo user
    client.post("/auth/login", json={"email": "demo@carcarer.app", "password": "demo123456"})

    # ── Vehicle 1: Peugeot 308 ──
    print("\nCreating Vehicle 1: Peugeot 308...")
    v1 = client.post("/vehicles", json={
        "name": "Peugeot 308",
        "brand": "Peugeot",
        "model": "308 II SW",
        "year": 2019,
        "plate_number": "FG-234-HJ",
        "vin": "VF3LCYHZPKS123456",
        "fuel_type": "diesel",
        "initial_mileage": 45000,
        "purchase_date": "2021-06-15",
    }).json()
    v1_id = v1["id"]
    print(f"  ID={v1_id}")

    # Maintenance events for Peugeot
    print("  Adding maintenance events...")
    maintenances_308 = [
        {"date": "2022-01-15", "mileage": 52000, "garage_name": "Garage Martin", "total_cost": 285.0, "event_type": "invoice", "work_type": "service",
         "items": [
            {"description": "Vidange huile moteur 5W30", "category": "moteur", "part_name": "Huile 5W30 5L", "quantity": 1, "unit_price": 45.0, "labor_cost": 40.0, "total_price": 85.0},
            {"description": "Filtre a huile", "category": "moteur", "part_name": "Filtre huile PSA", "quantity": 1, "unit_price": 15.0, "labor_cost": 0, "total_price": 15.0},
            {"description": "Filtre a air", "category": "moteur", "part_name": "Filtre air PSA", "quantity": 1, "unit_price": 25.0, "labor_cost": 10.0, "total_price": 35.0},
            {"description": "Filtre habitacle", "category": "climatisation", "part_name": "Filtre habitacle charbon actif", "quantity": 1, "unit_price": 20.0, "labor_cost": 10.0, "total_price": 30.0},
            {"description": "Controle des niveaux et points de securite", "category": "autre", "quantity": 1, "unit_price": 0, "labor_cost": 120.0, "total_price": 120.0},
         ]},
        {"date": "2022-09-20", "mileage": 63000, "garage_name": "Feu Vert Strasbourg", "total_cost": 420.0, "event_type": "invoice", "work_type": "repair",
         "items": [
            {"description": "Plaquettes de frein avant", "category": "freinage", "part_name": "Plaquettes AV Bosch", "quantity": 1, "unit_price": 65.0, "labor_cost": 80.0, "total_price": 145.0},
            {"description": "Disques de frein avant", "category": "freinage", "part_name": "Disques AV 283mm", "quantity": 2, "unit_price": 55.0, "labor_cost": 60.0, "total_price": 170.0},
            {"description": "Liquide de frein DOT4", "category": "freinage", "part_name": "DOT4 1L", "quantity": 1, "unit_price": 15.0, "labor_cost": 30.0, "total_price": 45.0},
            {"description": "Diagnostic electronique", "category": "electronique", "quantity": 1, "unit_price": 0, "labor_cost": 60.0, "total_price": 60.0},
         ]},
        {"date": "2023-03-10", "mileage": 71500, "garage_name": "Garage Martin", "total_cost": 195.0, "event_type": "invoice", "work_type": "service",
         "items": [
            {"description": "Vidange huile moteur 5W30", "category": "moteur", "part_name": "Huile 5W30 5L", "quantity": 1, "unit_price": 48.0, "labor_cost": 40.0, "total_price": 88.0},
            {"description": "Filtre a huile", "category": "moteur", "part_name": "Filtre huile PSA", "quantity": 1, "unit_price": 16.0, "labor_cost": 0, "total_price": 16.0},
            {"description": "Balais essuie-glace AV", "category": "carrosserie", "part_name": "Bosch Aerotwin 650/475", "quantity": 1, "unit_price": 35.0, "labor_cost": 0, "total_price": 35.0},
            {"description": "Controle visuel 30 points", "category": "autre", "quantity": 1, "unit_price": 0, "labor_cost": 56.0, "total_price": 56.0},
         ]},
        {"date": "2023-11-05", "mileage": 82000, "garage_name": "Garage Martin", "total_cost": 650.0, "event_type": "invoice", "work_type": "repair",
         "items": [
            {"description": "Kit distribution + pompe a eau", "category": "distribution", "part_name": "Kit distrib Gates + PAE", "quantity": 1, "unit_price": 280.0, "labor_cost": 320.0, "total_price": 600.0},
            {"description": "Liquide de refroidissement", "category": "refroidissement", "part_name": "LDR G12 5L", "quantity": 1, "unit_price": 20.0, "labor_cost": 30.0, "total_price": 50.0},
         ]},
        {"date": "2024-06-12", "mileage": 91000, "garage_name": "Garage Martin", "total_cost": 310.0, "event_type": "invoice", "work_type": "service",
         "items": [
            {"description": "Revision complete 90000 km", "category": "moteur", "part_name": "Kit revision complet", "quantity": 1, "unit_price": 120.0, "labor_cost": 140.0, "total_price": 260.0},
            {"description": "Filtre a gasoil", "category": "moteur", "part_name": "Filtre gasoil PSA", "quantity": 1, "unit_price": 30.0, "labor_cost": 20.0, "total_price": 50.0},
         ]},
        {"date": "2025-04-18", "mileage": 102000, "garage_name": "Feu Vert Strasbourg", "total_cost": 180.0, "event_type": "invoice", "work_type": "upgrade",
         "items": [
            {"description": "Ampoules LED phares avant H7", "category": "eclairage", "part_name": "Philips Ultinon H7 LED", "quantity": 2, "unit_price": 55.0, "labor_cost": 30.0, "total_price": 140.0},
            {"description": "Ampoules LED feux arriere", "category": "eclairage", "part_name": "LED P21W", "quantity": 2, "unit_price": 10.0, "labor_cost": 20.0, "total_price": 40.0},
         ]},
    ]

    for m in maintenances_308:
        items = m.pop("items")
        from sqlalchemy.orm import Session
        # Use direct DB insertion since API doesn't support full maintenance creation with items
        pass  # Will do via DB below

    # CT Reports for Peugeot
    print("  Adding CT reports...")

    # Fuel records for Peugeot
    print("  Adding fuel records...")
    fuels_308 = [
        {"date": "2024-01-10", "mileage": 85000, "liters": 45.2, "price_total": 76.84, "price_per_liter": 1.70, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2024-02-15", "mileage": 85750, "liters": 42.1, "price_total": 71.57, "price_per_liter": 1.70, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2024-03-22", "mileage": 86600, "liters": 44.8, "price_total": 74.37, "price_per_liter": 1.66, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2024-05-01", "mileage": 87800, "liters": 46.5, "price_total": 78.12, "price_per_liter": 1.68, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2024-06-18", "mileage": 89100, "liters": 48.2, "price_total": 82.58, "price_per_liter": 1.71, "station_name": "Shell A4", "is_full_tank": True},
        {"date": "2024-08-05", "mileage": 90500, "liters": 43.8, "price_total": 74.46, "price_per_liter": 1.70, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2024-09-20", "mileage": 91800, "liters": 47.1, "price_total": 80.07, "price_per_liter": 1.70, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2024-11-10", "mileage": 93200, "liters": 50.2, "price_total": 85.34, "price_per_liter": 1.70, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2025-01-05", "mileage": 95000, "liters": 49.5, "price_total": 84.15, "price_per_liter": 1.70, "station_name": "Shell A4", "is_full_tank": True},
        {"date": "2025-03-15", "mileage": 97200, "liters": 51.8, "price_total": 88.06, "price_per_liter": 1.70, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2025-06-01", "mileage": 99500, "liters": 48.9, "price_total": 85.58, "price_per_liter": 1.75, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2025-09-10", "mileage": 101800, "liters": 50.1, "price_total": 87.68, "price_per_liter": 1.75, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2026-01-20", "mileage": 104500, "liters": 52.3, "price_total": 93.61, "price_per_liter": 1.79, "station_name": "Shell A4", "is_full_tank": True},
        {"date": "2026-03-10", "mileage": 106200, "liters": 45.6, "price_total": 81.62, "price_per_liter": 1.79, "station_name": "TotalEnergies A35", "is_full_tank": True},
    ]
    for f in fuels_308:
        r = client.post(f"/vehicles/{v1_id}/fuel", json=f)
        if r.status_code != 201:
            print(f"    WARN fuel: {r.status_code} {r.text[:100]}")

    # Tax/insurance for Peugeot
    print("  Adding tax/insurance records...")
    taxes_308 = [
        {"record_type": "insurance", "name": "Assurance tous risques MAIF", "provider": "MAIF", "date": "2025-04-01", "cost": 720.0, "next_renewal_date": "2026-04-01", "renewal_frequency": "annual"},
        {"record_type": "vignette", "name": "Vignette Crit'Air 2", "provider": "Ministere Ecologie", "date": "2021-07-01", "cost": 3.70, "next_renewal_date": None, "renewal_frequency": "one_time"},
        {"record_type": "carbon_tax", "name": "Taxe regionale carte grise", "provider": "Prefecture Bas-Rhin", "date": "2021-06-15", "cost": 192.0, "next_renewal_date": None, "renewal_frequency": "one_time"},
        {"record_type": "toll_tag", "name": "Badge telepeage Bip&Go", "provider": "Bip&Go", "date": "2025-01-15", "cost": 24.0, "next_renewal_date": "2026-01-15", "renewal_frequency": "annual"},
        {"record_type": "insurance", "name": "Assistance depannage 0km", "provider": "MAIF", "date": "2025-04-01", "cost": 48.0, "next_renewal_date": "2026-04-01", "renewal_frequency": "annual"},
    ]
    for t in taxes_308:
        r = client.post(f"/vehicles/{v1_id}/tax-insurance", json=t)
        if r.status_code != 201:
            print(f"    WARN tax: {r.status_code} {r.text[:100]}")

    # Notes for Peugeot
    print("  Adding notes...")
    notes_308 = [
        {"content": "Bruit sourd cote passager au passage de ralentisseurs depuis janvier. A surveiller au prochain passage au garage.", "pinned": True},
        {"content": "Pneus hiver Michelin Alpin 6 stockes au garage Martin (rack C3). Montes en novembre, retires en mars."},
        {"content": "Le garage Martin recommande de changer la courroie d'accessoire au prochain entretien (~110 000 km)."},
        {"content": "Rappel constructeur PSA effectue le 15/09/2024 : mise a jour calculateur injection (gratuit)."},
    ]
    for n in notes_308:
        r = client.post(f"/vehicles/{v1_id}/notes", json=n)

    # Custom reminders
    print("  Adding custom reminders...")
    reminders_308 = [
        {"title": "Vidange huile moteur", "description": "Huile 5W30, filtre huile, controle niveaux", "trigger_mode": "km_or_date", "km_interval": 20000, "months_interval": 12, "last_performed_km": 91000, "last_performed_date": "2024-06-12"},
        {"title": "Controle technique", "description": "CT obligatoire tous les 2 ans", "trigger_mode": "date_only", "months_interval": 24, "last_performed_date": "2024-08-22"},
        {"title": "Pneus hiver", "description": "Monter les pneus hiver avant novembre", "trigger_mode": "date_only", "months_interval": 12, "last_performed_date": "2025-11-01"},
        {"title": "Courroie accessoire", "description": "A remplacer vers 110 000 km selon Garage Martin", "trigger_mode": "km_only", "km_interval": 110000, "last_performed_km": 0},
    ]
    for rem in reminders_308:
        r = client.post(f"/vehicles/{v1_id}/reminders-custom", json=rem)

    # Share with garage
    print("  Sharing with garage...")
    r = client.post(f"/vehicles/{v1_id}/share", json={"email": "garage.martin@example.com", "role": "editor"})
    if r.status_code == 201:
        print("    Shared with garage.martin@example.com (editor)")

    # ── Vehicle 2: Renault Clio ──
    print("\nCreating Vehicle 2: Renault Clio...")
    v2 = client.post("/vehicles", json={
        "name": "Renault Clio",
        "brand": "Renault",
        "model": "Clio V",
        "year": 2022,
        "plate_number": "GH-456-KL",
        "fuel_type": "essence",
        "initial_mileage": 12000,
        "purchase_date": "2022-09-01",
    }).json()
    v2_id = v2["id"]
    print(f"  ID={v2_id}")

    # Fuel for Clio
    print("  Adding fuel records...")
    fuels_clio = [
        {"date": "2025-01-10", "mileage": 28000, "liters": 35.2, "price_total": 63.36, "price_per_liter": 1.80, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2025-03-05", "mileage": 29500, "liters": 36.8, "price_total": 66.24, "price_per_liter": 1.80, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2025-05-20", "mileage": 31200, "liters": 38.1, "price_total": 70.49, "price_per_liter": 1.85, "station_name": "Shell A4", "is_full_tank": True},
        {"date": "2025-08-15", "mileage": 33000, "liters": 37.5, "price_total": 71.25, "price_per_liter": 1.90, "station_name": "Leclerc Vendenheim", "is_full_tank": True},
        {"date": "2025-11-01", "mileage": 34800, "liters": 36.2, "price_total": 68.78, "price_per_liter": 1.90, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2026-02-10", "mileage": 36500, "liters": 37.8, "price_total": 73.71, "price_per_liter": 1.95, "station_name": "Shell A4", "is_full_tank": True},
    ]
    for f in fuels_clio:
        client.post(f"/vehicles/{v2_id}/fuel", json=f)

    # Tax for Clio
    taxes_clio = [
        {"record_type": "insurance", "name": "Assurance tiers+ GMF", "provider": "GMF", "date": "2025-09-01", "cost": 480.0, "next_renewal_date": "2026-09-01", "renewal_frequency": "annual"},
        {"record_type": "registration", "name": "Carte grise", "provider": "Prefecture Bas-Rhin", "date": "2022-09-01", "cost": 156.0, "renewal_frequency": "one_time"},
    ]
    for t in taxes_clio:
        client.post(f"/vehicles/{v2_id}/tax-insurance", json=t)

    # ── Vehicle 3: BMW Serie 3 ──
    print("\nCreating Vehicle 3: BMW Serie 3...")
    v3 = client.post("/vehicles", json={
        "name": "BMW 320d",
        "brand": "BMW",
        "model": "320d F30",
        "year": 2017,
        "plate_number": "EM-789-NP",
        "fuel_type": "diesel",
        "initial_mileage": 95000,
        "purchase_date": "2020-03-10",
    }).json()
    v3_id = v3["id"]
    print(f"  ID={v3_id}")

    # Tax for BMW (one expired to show red badge)
    taxes_bmw = [
        {"record_type": "insurance", "name": "Assurance tous risques Allianz", "provider": "Allianz", "date": "2025-02-01", "cost": 960.0, "next_renewal_date": "2026-02-01", "renewal_frequency": "annual"},
        {"record_type": "vignette", "name": "Vignette Crit'Air 2", "provider": "Ministere Ecologie", "date": "2020-03-15", "cost": 3.70, "renewal_frequency": "one_time"},
        {"record_type": "parking", "name": "Abonnement parking residence", "provider": "Nexity", "date": "2025-06-01", "cost": 85.0, "next_renewal_date": "2026-01-01", "renewal_frequency": "annual", "notes": "Place B12, sous-sol -1"},
    ]
    for t in taxes_bmw:
        client.post(f"/vehicles/{v3_id}/tax-insurance", json=t)

    # Fuel for BMW
    fuels_bmw = [
        {"date": "2025-06-01", "mileage": 138000, "liters": 52.1, "price_total": 88.57, "price_per_liter": 1.70, "station_name": "Esso Kehl", "is_full_tank": True},
        {"date": "2025-08-15", "mileage": 140500, "liters": 48.9, "price_total": 83.13, "price_per_liter": 1.70, "station_name": "Shell Offenburg", "is_full_tank": True},
        {"date": "2025-11-01", "mileage": 143000, "liters": 51.2, "price_total": 89.60, "price_per_liter": 1.75, "station_name": "TotalEnergies A35", "is_full_tank": True},
        {"date": "2026-01-20", "mileage": 145500, "liters": 53.8, "price_total": 96.30, "price_per_liter": 1.79, "station_name": "Esso Kehl", "is_full_tank": True},
        {"date": "2026-03-15", "mileage": 148000, "liters": 50.5, "price_total": 90.40, "price_per_liter": 1.79, "station_name": "Shell Offenburg", "is_full_tank": True},
    ]
    for f in fuels_bmw:
        client.post(f"/vehicles/{v3_id}/fuel", json=f)

    # ── Insert maintenance + CT via direct DB ──
    print("\nInserting maintenance events and CT reports via DB...")
    from datetime import date as D
    sys.path.insert(0, ".")
    from app.database import SessionLocal
    from app.models.maintenance import MaintenanceEvent, MaintenanceItem
    from app.models.ct_report import CTReport, CTDefect

    db = SessionLocal()
    try:
        # Maintenance events for Peugeot 308
        for m in maintenances_308:
            items_data = m.pop("items", [])
            if isinstance(m.get("date"), str):
                m["date"] = D.fromisoformat(m["date"])
            ev = MaintenanceEvent(vehicle_id=v1_id, **m)
            db.add(ev)
            db.flush()
            for it in items_data:
                item = MaintenanceItem(event_id=ev.id, **it)
                db.add(item)

        # CT Reports for Peugeot 308
        ct1 = CTReport(vehicle_id=v1_id, date=D(2022, 8, 22), mileage=60000, center_name="Dekra Strasbourg", result="favorable", next_due_date=D(2024, 8, 22))
        db.add(ct1)
        db.flush()
        db.add(CTDefect(ct_report_id=ct1.id, code="6.1.2", description="Feu de position avant droit: intensite insuffisante", severity="mineur", category="eclairage"))
        db.add(CTDefect(ct_report_id=ct1.id, code="1.1.3", description="Jeu rotule de direction avant gauche", severity="a_surveiller", category="direction"))

        ct2 = CTReport(vehicle_id=v1_id, date=D(2024, 8, 22), mileage=92000, center_name="Dekra Strasbourg", result="favorable", next_due_date=D(2026, 8, 22))
        db.add(ct2)
        db.flush()
        db.add(CTDefect(ct_report_id=ct2.id, code="1.1.3", description="Jeu rotule de direction avant gauche: en augmentation", severity="mineur", category="direction"))
        db.add(CTDefect(ct_report_id=ct2.id, code="5.1.1", description="Fuite suintement amortisseur arriere gauche", severity="a_surveiller", category="suspension"))
        db.add(CTDefect(ct_report_id=ct2.id, code="8.2.1", description="Corrosion perforante sous caisse cote droit", severity="majeur", category="carrosserie"))

        # Maintenance for Clio
        ev_clio1 = MaintenanceEvent(vehicle_id=v2_id, date=D(2024, 3, 15), mileage=24000, garage_name="Norauto Hautepierre", total_cost=175.0, event_type="invoice", work_type="service")
        db.add(ev_clio1)
        db.flush()
        db.add(MaintenanceItem(event_id=ev_clio1.id, description="Revision 20000 km", category="moteur", part_name="Kit revision Renault", quantity=1, unit_price=80.0, labor_cost=95.0, total_price=175.0))

        ev_clio2 = MaintenanceEvent(vehicle_id=v2_id, date=D(2025, 9, 10), mileage=33500, garage_name="Norauto Hautepierre", total_cost=95.0, event_type="invoice", work_type="service")
        db.add(ev_clio2)
        db.flush()
        db.add(MaintenanceItem(event_id=ev_clio2.id, description="Vidange huile 5W40", category="moteur", part_name="Huile Elf 5W40 4L", quantity=1, unit_price=38.0, labor_cost=40.0, total_price=78.0))
        db.add(MaintenanceItem(event_id=ev_clio2.id, description="Filtre a huile", category="moteur", part_name="Filtre huile Renault", quantity=1, unit_price=12.0, labor_cost=5.0, total_price=17.0))

        # Maintenance for BMW
        ev_bmw1 = MaintenanceEvent(vehicle_id=v3_id, date=D(2024, 11, 20), mileage=135000, garage_name="BMW Strasbourg", total_cost=890.0, event_type="invoice", work_type="repair")
        db.add(ev_bmw1)
        db.flush()
        db.add(MaintenanceItem(event_id=ev_bmw1.id, description="Turbo remplacement", category="moteur", part_name="Turbo Garrett reconditionne", quantity=1, unit_price=480.0, labor_cost=350.0, total_price=830.0))
        db.add(MaintenanceItem(event_id=ev_bmw1.id, description="Joint admission turbo", category="moteur", quantity=1, unit_price=25.0, labor_cost=35.0, total_price=60.0))

        ev_bmw2 = MaintenanceEvent(vehicle_id=v3_id, date=D(2025, 5, 15), mileage=140000, garage_name="BMW Strasbourg", total_cost=380.0, event_type="invoice", work_type="service")
        db.add(ev_bmw2)
        db.flush()
        db.add(MaintenanceItem(event_id=ev_bmw2.id, description="Revision complete 140000 km", category="moteur", part_name="Kit revision BMW", quantity=1, unit_price=180.0, labor_cost=200.0, total_price=380.0))

        db.commit()
        print("  All maintenance and CT records inserted.")
    finally:
        db.close()

    # ── Summary ──
    print("\n" + "=" * 60)
    print("DEMO DATA SEEDED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nLogin: demo@carcarer.app / demo123456")
    print(f"URL:   http://localhost:8200")
    print(f"\n3 vehicles:")
    print(f"  1. Peugeot 308 SW — 6 entretiens, 2 CT, 14 pleins, 5 taxes, 4 notes, 4 rappels, 1 partage")
    print(f"  2. Renault Clio V — 2 entretiens, 6 pleins, 2 taxes")
    print(f"  3. BMW 320d       — 2 entretiens, 5 pleins, 3 taxes")
    print(f"\nGarage user: garage.martin@example.com / garage123456 (editor on Peugeot 308)")
    print(f"\nReady for screenshots!")


if __name__ == "__main__":
    seed()

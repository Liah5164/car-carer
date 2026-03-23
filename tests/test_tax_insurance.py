"""Tests for tax & insurance record endpoints."""


def _create_vehicle(auth_client):
    res = auth_client.post("/api/vehicles", json={"name": "TaxCar"})
    assert res.status_code == 201
    return res.json()["id"]


def _tax_data(**overrides):
    data = {
        "record_type": "insurance",
        "name": "Assurance auto MAIF",
        "provider": "MAIF",
        "date": "2026-01-15",
        "cost": 650.0,
        "next_renewal_date": "2027-01-15",
        "renewal_frequency": "annual",
    }
    data.update(overrides)
    return data


def test_create_tax_record(auth_client):
    vid = _create_vehicle(auth_client)
    res = auth_client.post(f"/api/vehicles/{vid}/tax-insurance", json=_tax_data())
    assert res.status_code == 201
    data = res.json()
    assert data["vehicle_id"] == vid
    assert data["record_type"] == "insurance"
    assert data["name"] == "Assurance auto MAIF"
    assert data["provider"] == "MAIF"
    assert data["cost"] == 650.0
    assert data["next_renewal_date"] == "2027-01-15"
    assert data["renewal_frequency"] == "annual"
    assert "id" in data
    assert "created_at" in data


def test_list_tax_records(auth_client):
    vid = _create_vehicle(auth_client)
    auth_client.post(f"/api/vehicles/{vid}/tax-insurance", json=_tax_data(
        record_type="insurance", name="Assurance", date="2026-01-01",
    ))
    auth_client.post(f"/api/vehicles/{vid}/tax-insurance", json=_tax_data(
        record_type="vignette", name="Vignette Crit'Air", date="2026-06-01",
    ))

    res = auth_client.get(f"/api/vehicles/{vid}/tax-insurance")
    assert res.status_code == 200
    records = res.json()
    assert len(records) == 2
    # Ordered by date desc
    assert records[0]["date"] == "2026-06-01"
    assert records[1]["date"] == "2026-01-01"


def test_update_tax_record(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/tax-insurance", json=_tax_data())
    record_id = create_res.json()["id"]

    res = auth_client.patch(f"/api/vehicles/{vid}/tax-insurance/{record_id}", json={
        "cost": 720.0,
        "notes": "Augmentation prime",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["cost"] == 720.0
    assert data["notes"] == "Augmentation prime"
    # Unchanged fields preserved
    assert data["record_type"] == "insurance"
    assert data["name"] == "Assurance auto MAIF"


def test_delete_tax_record(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/tax-insurance", json=_tax_data())
    record_id = create_res.json()["id"]

    res = auth_client.delete(f"/api/vehicles/{vid}/tax-insurance/{record_id}")
    assert res.status_code == 204

    # Verify it's gone
    list_res = auth_client.get(f"/api/vehicles/{vid}/tax-insurance")
    assert len(list_res.json()) == 0


def test_tax_requires_auth(client):
    res = client.post("/api/vehicles/1/tax-insurance", json=_tax_data())
    assert res.status_code == 401

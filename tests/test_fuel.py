"""Tests for fuel record endpoints."""


def _create_vehicle(auth_client):
    res = auth_client.post("/api/vehicles", json={"name": "FuelCar"})
    assert res.status_code == 201
    return res.json()["id"]


def _fuel_data(**overrides):
    data = {
        "date": "2026-03-01",
        "liters": 45.0,
        "price_total": 72.0,
        "fuel_type": "SP95",
        "is_full_tank": True,
        "station_name": "TotalEnergies",
    }
    data.update(overrides)
    return data


def test_create_fuel_record(auth_client):
    vid = _create_vehicle(auth_client)
    res = auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data())
    assert res.status_code == 201
    data = res.json()
    assert data["vehicle_id"] == vid
    assert data["liters"] == 45.0
    assert data["price_total"] == 72.0
    assert data["fuel_type"] == "SP95"
    assert data["is_full_tank"] is True
    assert data["station_name"] == "TotalEnergies"
    assert "id" in data
    assert "created_at" in data
    # price_per_liter auto-calculated: 72 / 45 = 1.6
    assert data["price_per_liter"] == 1.6


def test_list_fuel_records(auth_client):
    vid = _create_vehicle(auth_client)
    auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data(date="2026-01-10"))
    auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data(date="2026-02-15"))
    auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data(date="2026-03-01"))

    res = auth_client.get(f"/api/vehicles/{vid}/fuel")
    assert res.status_code == 200
    records = res.json()
    assert len(records) == 3
    # Ordered by date desc
    assert records[0]["date"] == "2026-03-01"
    assert records[2]["date"] == "2026-01-10"


def test_delete_fuel_record(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data())
    fuel_id = create_res.json()["id"]

    res = auth_client.delete(f"/api/vehicles/{vid}/fuel/{fuel_id}")
    assert res.status_code == 204

    # Verify it's gone
    list_res = auth_client.get(f"/api/vehicles/{vid}/fuel")
    assert len(list_res.json()) == 0


def test_fuel_stats_empty(auth_client):
    vid = _create_vehicle(auth_client)
    res = auth_client.get(f"/api/vehicles/{vid}/fuel/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_liters"] == 0
    assert data["total_cost"] == 0
    assert data["record_count"] == 0
    assert data["consumptions"] == []


def test_fuel_stats_with_data(auth_client):
    vid = _create_vehicle(auth_client)
    # Two full-tank fills with mileage to trigger consumption calculation
    auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data(
        date="2026-01-01", mileage=10000, liters=40.0, price_total=64.0, is_full_tank=True,
    ))
    auth_client.post(f"/api/vehicles/{vid}/fuel", json=_fuel_data(
        date="2026-02-01", mileage=10500, liters=35.0, price_total=56.0, is_full_tank=True,
    ))

    res = auth_client.get(f"/api/vehicles/{vid}/fuel/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["record_count"] == 2
    assert data["total_liters"] == 75.0
    assert data["total_cost"] == 120.0
    assert len(data["consumptions"]) == 1
    # 35 liters / 500 km * 100 = 7.0 L/100km
    assert data["consumptions"][0]["liters_100km"] == 7.0
    assert data["avg_consumption_l100km"] == 7.0


def test_fuel_requires_auth(client):
    res = client.post("/api/vehicles/1/fuel", json=_fuel_data())
    assert res.status_code == 401

"""Tests for vehicle CRUD and analysis endpoints."""


def test_create_vehicle(auth_client):
    res = auth_client.post("/api/vehicles", json={"name": "Ma Clio"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Ma Clio"
    assert "id" in data


def test_list_vehicles(auth_client):
    auth_client.post("/api/vehicles", json={"name": "V1"})
    auth_client.post("/api/vehicles", json={"name": "V2"})
    res = auth_client.get("/api/vehicles")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_vehicle(auth_client):
    create = auth_client.post("/api/vehicles", json={"name": "Test"})
    vid = create.json()["id"]
    res = auth_client.get(f"/api/vehicles/{vid}")
    assert res.status_code == 200
    assert res.json()["name"] == "Test"


def test_update_vehicle(auth_client):
    create = auth_client.post("/api/vehicles", json={"name": "Old"})
    vid = create.json()["id"]
    res = auth_client.patch(f"/api/vehicles/{vid}", json={"name": "New", "brand": "Renault"})
    assert res.status_code == 200
    assert res.json()["name"] == "New"
    assert res.json()["brand"] == "Renault"


def test_delete_vehicle(auth_client):
    create = auth_client.post("/api/vehicles", json={"name": "ToDelete"})
    vid = create.json()["id"]
    res = auth_client.delete(f"/api/vehicles/{vid}")
    assert res.status_code == 204
    res = auth_client.get(f"/api/vehicles/{vid}")
    assert res.status_code == 404


def test_vehicle_analysis(auth_client):
    create = auth_client.post("/api/vehicles", json={"name": "Analyse"})
    vid = create.json()["id"]
    res = auth_client.get(f"/api/vehicles/{vid}/analysis")
    assert res.status_code == 200
    data = res.json()
    assert "alerts" in data
    assert "health_score" in data
    assert "maintenance_intervals" in data


def test_vehicle_stats(auth_client):
    create = auth_client.post("/api/vehicles", json={"name": "Stats"})
    vid = create.json()["id"]
    res = auth_client.get(f"/api/vehicles/{vid}/stats")
    assert res.status_code == 200
    data = res.json()
    assert "spending_by_month" in data
    assert "mileage_timeline" in data
    assert "spending_by_category" in data


def test_vehicle_requires_auth(client):
    res = client.get("/api/vehicles")
    assert res.status_code == 401


def test_vehicle_not_found(auth_client):
    res = auth_client.get("/api/vehicles/999")
    assert res.status_code == 404

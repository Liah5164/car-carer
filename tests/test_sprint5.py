"""Tests for Sprint 5 features: dashboard, budget, price history, booklet."""


def test_dashboard(auth_client):
    auth_client.post("/api/vehicles", json={"name": "V1"})
    auth_client.post("/api/vehicles", json={"name": "V2"})
    res = auth_client.get("/api/vehicles/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["vehicle_count"] == 2
    assert len(data["vehicles"]) == 2
    assert "avg_health_score" in data["summary"]


def test_dashboard_requires_auth(client):
    res = client.get("/api/vehicles/dashboard")
    assert res.status_code == 401


def test_budget_forecast(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Budget"}).json()
    res = auth_client.get(f"/api/vehicles/{v['id']}/budget-forecast")
    assert res.status_code == 200
    data = res.json()
    assert "forecast" in data
    assert "historical_avg" in data
    assert "breakdown" in data
    assert "yearly_history" in data


def test_price_history(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Prices"}).json()
    res = auth_client.get(f"/api/vehicles/{v['id']}/price-history")
    assert res.status_code == 200
    assert "categories" in res.json()


def test_export_booklet(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Booklet"}).json()
    res = auth_client.get(f"/api/vehicles/{v['id']}/export-booklet")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 0

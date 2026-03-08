"""Tests for vehicle sharing."""


def test_create_share_link(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Shared"}).json()
    res = auth_client.post(f"/api/vehicles/{v['id']}/share")
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert len(data["token"]) > 20


def test_list_share_links(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Shared"}).json()
    auth_client.post(f"/api/vehicles/{v['id']}/share")
    auth_client.post(f"/api/vehicles/{v['id']}/share")
    res = auth_client.get(f"/api/vehicles/{v['id']}/shares")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_access_shared_vehicle(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Public"}).json()
    share = auth_client.post(f"/api/vehicles/{v['id']}/share").json()
    # Access without auth (new client is fine since TestClient uses same session)
    res = auth_client.get(f"/api/shared/{share['token']}")
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle"]["name"] == "Public"
    assert "health_score" in data


def test_invalid_share_token(auth_client):
    res = auth_client.get("/api/shared/invalid-token-12345")
    assert res.status_code == 404


def test_revoke_share_link(auth_client):
    v = auth_client.post("/api/vehicles", json={"name": "Revoke"}).json()
    share = auth_client.post(f"/api/vehicles/{v['id']}/share").json()
    res = auth_client.delete(f"/api/vehicles/{v['id']}/share/{share['id']}")
    assert res.status_code == 204
    # Token should no longer work
    res = auth_client.get(f"/api/shared/{share['token']}")
    assert res.status_code == 404

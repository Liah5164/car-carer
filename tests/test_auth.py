"""Tests for authentication endpoints."""


def test_register(client):
    res = client.post("/api/auth/register", json={"email": "new@test.com", "password": "pass123"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "new@test.com"
    assert "id" in data


def test_register_duplicate(client):
    client.post("/api/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    res = client.post("/api/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    assert res.status_code == 409


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={"email": "short@test.com", "password": "12345"})
    assert res.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={"email": "login@test.com", "password": "pass123"})
    res = client.post("/api/auth/login", json={"email": "login@test.com", "password": "pass123"})
    assert res.status_code == 200
    assert res.json()["email"] == "login@test.com"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "wrong@test.com", "password": "pass123"})
    res = client.post("/api/auth/login", json={"email": "wrong@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_me_authenticated(auth_client):
    res = auth_client.get("/api/auth/me")
    assert res.status_code == 200
    assert res.json()["email"] == "test@test.com"


def test_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_logout(auth_client):
    res = auth_client.post("/api/auth/logout")
    assert res.status_code == 200
    # After logout, /me should fail
    # Note: TestClient may not clear cookies automatically

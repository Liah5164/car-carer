"""Tests for settings endpoints (change password)."""


def test_change_password(auth_client):
    """Changing password with correct current password should succeed."""
    res = auth_client.post("/api/auth/change-password", json={
        "current_password": "test123",
        "new_password": "newpass456",
    })
    assert res.status_code == 200
    assert res.json()["ok"] is True

    # Verify login works with new password
    auth_client.post("/api/auth/logout")
    login_res = auth_client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "newpass456",
    })
    assert login_res.status_code == 200


def test_change_password_wrong_current(auth_client):
    """Changing password with wrong current password should fail."""
    res = auth_client.post("/api/auth/change-password", json={
        "current_password": "wrongpassword",
        "new_password": "newpass456",
    })
    assert res.status_code == 400


def test_change_password_too_short(auth_client):
    """New password must be at least 6 characters."""
    res = auth_client.post("/api/auth/change-password", json={
        "current_password": "test123",
        "new_password": "short",
    })
    assert res.status_code == 400


def test_change_password_requires_auth(client):
    """Change password should require authentication."""
    res = client.post("/api/auth/change-password", json={
        "current_password": "test123",
        "new_password": "newpass456",
    })
    assert res.status_code == 401

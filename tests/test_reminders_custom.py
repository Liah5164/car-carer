"""Tests for custom reminders endpoints."""


def _create_vehicle(auth_client):
    res = auth_client.post("/api/vehicles", json={"name": "ReminderCar"})
    assert res.status_code == 201
    return res.json()["id"]


def _reminder_data(**overrides):
    data = {
        "title": "Vidange",
        "description": "Changement huile moteur",
        "trigger_mode": "km_or_date",
        "km_interval": 15000,
        "months_interval": 12,
        "is_recurring": True,
        "active": True,
    }
    data.update(overrides)
    return data


def test_create_reminder(auth_client):
    vid = _create_vehicle(auth_client)
    res = auth_client.post(f"/api/vehicles/{vid}/reminders-custom", json=_reminder_data())
    assert res.status_code == 201
    data = res.json()
    assert data["vehicle_id"] == vid
    assert data["title"] == "Vidange"
    assert data["description"] == "Changement huile moteur"
    assert data["trigger_mode"] == "km_or_date"
    assert data["km_interval"] == 15000
    assert data["months_interval"] == 12
    assert data["is_recurring"] is True
    assert data["active"] is True
    assert "id" in data
    assert "created_at" in data


def test_list_reminders(auth_client):
    vid = _create_vehicle(auth_client)
    auth_client.post(f"/api/vehicles/{vid}/reminders-custom", json=_reminder_data(title="Vidange"))
    auth_client.post(f"/api/vehicles/{vid}/reminders-custom", json=_reminder_data(title="Pneus"))

    res = auth_client.get(f"/api/vehicles/{vid}/reminders-custom")
    assert res.status_code == 200
    reminders = res.json()
    assert len(reminders) == 2
    titles = {r["title"] for r in reminders}
    assert titles == {"Vidange", "Pneus"}


def test_update_reminder(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/reminders-custom", json=_reminder_data())
    rid = create_res.json()["id"]

    res = auth_client.patch(f"/api/vehicles/{vid}/reminders-custom/{rid}", json={
        "title": "Vidange modifiee",
        "km_interval": 20000,
        "active": False,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Vidange modifiee"
    assert data["km_interval"] == 20000
    assert data["active"] is False
    # Unchanged fields preserved
    assert data["trigger_mode"] == "km_or_date"


def test_delete_reminder(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/reminders-custom", json=_reminder_data())
    rid = create_res.json()["id"]

    res = auth_client.delete(f"/api/vehicles/{vid}/reminders-custom/{rid}")
    assert res.status_code == 204

    # Verify it's gone
    list_res = auth_client.get(f"/api/vehicles/{vid}/reminders-custom")
    assert len(list_res.json()) == 0


def test_reminder_requires_auth(client):
    res = client.post("/api/vehicles/1/reminders-custom", json=_reminder_data())
    assert res.status_code == 401

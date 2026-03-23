"""Tests for vehicle notes endpoints."""


def _create_vehicle(auth_client):
    res = auth_client.post("/api/vehicles", json={"name": "NoteCar"})
    assert res.status_code == 201
    return res.json()["id"]


def test_create_note(auth_client):
    vid = _create_vehicle(auth_client)
    res = auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Penser a verifier la pression des pneus",
        "pinned": False,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["vehicle_id"] == vid
    assert data["content"] == "Penser a verifier la pression des pneus"
    assert data["pinned"] is False
    assert "id" in data
    assert "created_at" in data


def test_list_notes_pinned_first(auth_client):
    vid = _create_vehicle(auth_client)
    # Create normal note first, then pinned note
    auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Note normale",
        "pinned": False,
    })
    auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Note importante",
        "pinned": True,
    })

    res = auth_client.get(f"/api/vehicles/{vid}/notes")
    assert res.status_code == 200
    notes = res.json()
    assert len(notes) == 2
    # Pinned note should come first
    assert notes[0]["pinned"] is True
    assert notes[0]["content"] == "Note importante"
    assert notes[1]["pinned"] is False
    assert notes[1]["content"] == "Note normale"


def test_search_notes(auth_client):
    vid = _create_vehicle(auth_client)
    auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Pneus hiver montes le 15 novembre",
    })
    auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Vidange prevue en janvier",
    })
    auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Rappel constructeur pneus arriere",
    })

    # Search for "pneus"
    res = auth_client.get(f"/api/vehicles/{vid}/notes", params={"q": "pneus"})
    assert res.status_code == 200
    notes = res.json()
    assert len(notes) == 2
    contents = {n["content"] for n in notes}
    assert "Pneus hiver montes le 15 novembre" in contents
    assert "Rappel constructeur pneus arriere" in contents


def test_update_note_pin(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Note a epingler",
        "pinned": False,
    })
    note_id = create_res.json()["id"]

    # Pin the note
    res = auth_client.patch(f"/api/vehicles/{vid}/notes/{note_id}", json={
        "pinned": True,
    })
    assert res.status_code == 200
    assert res.json()["pinned"] is True
    assert res.json()["content"] == "Note a epingler"


def test_update_note_content(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "Contenu original",
    })
    note_id = create_res.json()["id"]

    res = auth_client.patch(f"/api/vehicles/{vid}/notes/{note_id}", json={
        "content": "Contenu modifie",
    })
    assert res.status_code == 200
    assert res.json()["content"] == "Contenu modifie"


def test_delete_note(auth_client):
    vid = _create_vehicle(auth_client)
    create_res = auth_client.post(f"/api/vehicles/{vid}/notes", json={
        "content": "A supprimer",
    })
    note_id = create_res.json()["id"]

    res = auth_client.delete(f"/api/vehicles/{vid}/notes/{note_id}")
    assert res.status_code == 204

    # Verify it's gone
    list_res = auth_client.get(f"/api/vehicles/{vid}/notes")
    assert len(list_res.json()) == 0


def test_notes_require_auth(client):
    res = client.post("/api/vehicles/1/notes", json={"content": "test"})
    assert res.status_code == 401

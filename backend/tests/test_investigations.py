import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.investigation_service import investigation_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_in_memory_store():
    investigation_service.clear()
    yield
    investigation_service.clear()


def test_create_investigation_valid_event_name():
    """Test creating an investigation with only event_name."""
    response = client.post(
        "/api/investigations",
        json={"event_name": "AI Systems Summit 2026"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "investigation_id" in data
    assert data["investigation_id"].startswith("inv_")
    assert data["input"]["event_name"] == "AI Systems Summit 2026"
    assert data["input"]["event_url"] is None
    assert data["status"] == "pending"
    assert "created_at" in data


def test_create_investigation_valid_event_url():
    """Test creating an investigation with only event_url."""
    response = client.post(
        "/api/investigations",
        json={"event_url": "https://aisummit2026.example.org"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "investigation_id" in data
    assert data["investigation_id"].startswith("inv_")
    assert data["input"]["event_url"] == "https://aisummit2026.example.org"
    assert data["input"]["event_name"] is None
    assert data["status"] == "pending"
    assert "created_at" in data


def test_create_investigation_valid_both_name_and_url():
    """Test creating an investigation with both event_name and event_url."""
    response = client.post(
        "/api/investigations",
        json={
            "event_name": "AI Systems Summit 2026",
            "event_url": "https://aisummit2026.example.org",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["input"]["event_name"] == "AI Systems Summit 2026"
    assert data["input"]["event_url"] == "https://aisummit2026.example.org"
    assert data["status"] == "pending"


def test_create_investigation_invalid_neither_field():
    """Test that requesting an investigation with neither field returns a validation error."""
    response = client.post(
        "/api/investigations",
        json={},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_create_investigation_invalid_empty_whitespace():
    """Test that empty or whitespace-only inputs are rejected."""
    response = client.post(
        "/api/investigations",
        json={"event_name": "   ", "event_url": ""},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_get_investigation_by_id():
    """Test retrieving an investigation after creation."""
    create_res = client.post(
        "/api/investigations",
        json={"event_name": "DevCon 2026"},
    )
    assert create_res.status_code == 201
    inv_id = create_res.json()["investigation_id"]

    get_res = client.get(f"/api/investigations/{inv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["investigation_id"] == inv_id
    assert get_res.json()["input"]["event_name"] == "DevCon 2026"


def test_get_investigation_not_found():
    """Test retrieving a non-existent investigation returns 404."""
    response = client.get("/api/investigations/inv_nonexistent")
    assert response.status_code == 404

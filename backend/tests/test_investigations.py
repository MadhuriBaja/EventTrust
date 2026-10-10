from fastapi.testclient import TestClient

from app.main import app
from app.models.event import EventProfile
from app.services.investigation_service import (
    event_extraction_service,
    investigation_service,
)


client = TestClient(app)


def setup_function():
    """Clear in-memory investigations before each test."""
    investigation_service.clear()


def test_create_investigation_valid_event_name():
    """Test creating an investigation with only event_name."""

    response = client.post(
        "/api/investigations",
        json={"event_name": "AI Systems Summit 2026"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["investigation_id"].startswith("inv_")
    assert data["input"]["event_name"] == "AI Systems Summit 2026"
    assert data["input"]["event_url"] is None
    assert data["status"] == "pending"
    assert data["event_profile"] is None


def test_create_investigation_valid_event_url(monkeypatch):
    """Test creating an investigation with only event_url."""

    def mock_extract_from_url(event_url):
        return EventProfile(
            event_name="AI Systems Summit 2026",
            source_url=event_url,
            description="A technology summit.",
        )

    monkeypatch.setattr(
        event_extraction_service,
        "extract_from_url",
        mock_extract_from_url,
    )

    response = client.post(
        "/api/investigations",
        json={"event_url": "https://aisummit2026.example.org"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["input"]["event_name"] is None
    assert data["input"]["event_url"] == "https://aisummit2026.example.org"
    assert data["status"] == "pending"

    assert data["event_profile"]["event_name"] == "AI Systems Summit 2026"
    assert data["event_profile"]["source_url"] == "https://aisummit2026.example.org"
    assert data["event_profile"]["description"] == "A technology summit."


def test_create_investigation_valid_both_name_and_url(monkeypatch):
    """Test creating an investigation with both event_name and event_url."""

    def mock_extract_from_url(event_url):
        return EventProfile(
            event_name="Extracted AI Summit",
            source_url=event_url,
            description="An extracted event description.",
        )

    monkeypatch.setattr(
        event_extraction_service,
        "extract_from_url",
        mock_extract_from_url,
    )

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

    assert data["event_profile"]["event_name"] == "Extracted AI Summit"
    assert data["event_profile"]["source_url"] == "https://aisummit2026.example.org"


def test_create_investigation_missing_both():
    """Test that both event_name and event_url are required."""

    response = client.post(
        "/api/investigations",
        json={},
    )

    assert response.status_code == 422


def test_create_investigation_empty_event_name():
    """Test that an empty event_name is rejected."""

    response = client.post(
        "/api/investigations",
        json={"event_name": "   "},
    )

    assert response.status_code == 422


def test_create_investigation_empty_event_url():
    """Test that an empty event_url is rejected."""

    response = client.post(
        "/api/investigations",
        json={"event_url": "   "},
    )

    assert response.status_code == 422


def test_get_investigation():
    """Test retrieving an existing investigation."""

    create_response = client.post(
        "/api/investigations",
        json={"event_name": "AI Systems Summit 2026"},
    )

    assert create_response.status_code == 201

    investigation_id = create_response.json()["investigation_id"]

    response = client.get(
        f"/api/investigations/{investigation_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["investigation_id"] == investigation_id
    assert data["input"]["event_name"] == "AI Systems Summit 2026"
    assert data["status"] == "pending"


def test_get_investigation_not_found():
    """Test retrieving an investigation that does not exist."""

    response = client.get(
        "/api/investigations/inv_doesnotexist"
    )

    assert response.status_code == 404

    data = response.json()

    assert "not found" in data["detail"].lower()


def test_create_investigation_trims_input():
    """Test that leading and trailing whitespace is removed."""

    response = client.post(
        "/api/investigations",
        json={
            "event_name": "  AI Systems Summit 2026  ",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["input"]["event_name"] == "AI Systems Summit 2026"


def test_get_created_investigation_contains_event_profile(monkeypatch):
    """Test that extracted event information is stored with the investigation."""

    def mock_extract_from_url(event_url):
        return EventProfile(
            event_name="Tech Conference 2026",
            organizer="Example Organizer",
            event_date="2026-11-20",
            venue="Hyderabad Convention Centre",
            source_url=event_url,
        )

    monkeypatch.setattr(
        event_extraction_service,
        "extract_from_url",
        mock_extract_from_url,
    )

    create_response = client.post(
        "/api/investigations",
        json={
            "event_url": "https://example.com/event",
        },
    )

    assert create_response.status_code == 201

    investigation_id = create_response.json()["investigation_id"]

    response = client.get(
        f"/api/investigations/{investigation_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_profile"]["event_name"] == "Tech Conference 2026"
    assert data["event_profile"]["organizer"] == "Example Organizer"
    assert data["event_profile"]["event_date"] == "2026-11-20"
    assert data["event_profile"]["venue"] == "Hyderabad Convention Centre"
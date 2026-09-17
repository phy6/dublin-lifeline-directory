import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from validate import validate_location, validate_services, run_validation, validate_clinic

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICES_PATH = os.path.join(PROJECT_ROOT, "src", "lib", "data", "services.json")


def test_validate_location_valid():
    loc = {
        "id": "test-centre",
        "name": "Test Centre",
        "address": "1 Test St",
        "latitude": 53.35,
        "longitude": -6.25,
        "category": "Emergency Shelter",
        "services": ["food", "shelter"],
        "phone": "+353-1-123-4567",
        "email": "test@test.ie",
        "website": "https://test.ie",
        "hours": {"mon-fri": "09:00-17:00"},
    }
    result = validate_location(loc)
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validate_location_missing_required():
    loc = {"id": "test", "name": "", "address": "", "latitude": 0, "longitude": 0}
    result = validate_location(loc)
    assert len(result["errors"]) > 0
    assert any("name" in e for e in result["errors"])
    assert any("address" in e for e in result["errors"])


def test_validate_location_invalid_latitude():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 100,
        "longitude": 0,
        "category": "Test",
        "services": ["food"],
    }
    result = validate_location(loc)
    assert any("latitude" in e for e in result["errors"])


def test_validate_location_invalid_services():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["Invalid Service"],
    }
    result = validate_location(loc)
    assert any("slug" in e for e in result["errors"])


def test_validate_location_duplicate_services():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food", "food"],
    }
    result = validate_location(loc)
    assert any("duplicate" in e for e in result["errors"])


def test_validate_location_invalid_email():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food"],
        "email": "notanemail",
    }
    result = validate_location(loc)
    assert any("email" in e for e in result["warnings"])


def test_validate_location_invalid_website():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food"],
        "website": "not-a-url",
    }
    result = validate_location(loc)
    assert any("website" in e for e in result["warnings"])


def test_validate_location_empty_services():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": [],
    }
    result = validate_location(loc)
    assert any("non-empty array" in e for e in result["errors"])


def test_validate_hours_invalid_time_range():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food"],
        "hours": {"mon-fri": "17:00-09:00"},
    }
    result = validate_location(loc)
    assert any("not after start" in w for w in result["warnings"])


def test_validate_hours_all_closed():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food"],
        "hours": {"mon-fri": "closed"},
    }
    result = validate_location(loc)
    assert any("invalid format" in w for w in result["warnings"])


def test_validate_clinic_invalid_location_id():
    loc = {
        "id": "test",
        "name": "Test",
        "address": "1 St",
        "latitude": 53.0,
        "longitude": -6.0,
        "category": "Test",
        "services": ["food"],
        "location_id": "nonexistent-location",
    }
    errors = validate_clinic(loc, ["existing-id"])
    assert len(errors) > 0


def test_validate_services_valid():
    data = {
        "services": [
            {
                "id": "test",
                "name": "Test",
                "address": "1 St",
                "latitude": 53.0,
                "longitude": -6.0,
                "category": "Test",
                "services": ["food"],
            }
        ]
    }
    result = validate_services(data)
    assert result["valid"] is True
    assert len(result["locations"]) == 1


def test_validate_services_invalid():
    data = {
        "services": [
            {
                "id": "test",
                "name": "",
                "address": "",
                "latitude": 200,
                "longitude": 200,
                "category": "",
                "services": [],
            }
        ]
    }
    result = validate_services(data)
    assert result["valid"] is False
    assert len(result["locations"]) == 1
    assert len(result["locations"][0]["errors"]) > 0


def test_run_validation_on_real_data():
    if not os.path.exists(SERVICES_PATH):
        pytest.skip("services.json not found")
    result = run_validation(SERVICES_PATH)
    assert "valid" in result
    assert "locations" in result
    assert len(result["locations"]) > 0
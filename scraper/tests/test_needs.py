import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import NEEDS, normalize_services
from validate import validate_location


def test_needs_has_15_curated_slugs():
    assert len(NEEDS) == 15
    assert "food" in NEEDS and "mental-health" in NEEDS
    assert "housing" in NEEDS and "support" in NEEDS and "elderly" in NEEDS


def test_normalize_drops_unknown_fail_closed():
    assert normalize_services(["Hot Meals", "Dragon Riding"]) == ["food"]


def test_normalize_maps_fallback_vocabulary():
    result = normalize_services(
        ["homelessness", "housing", "addiction", "elderly", "counselling", "outreach", "clothing"]
    )
    assert result == [
        "addiction-support",
        "clothing",
        "counselling",
        "elderly",
        "housing",
        "outreach",
        "shelter",
    ]


def test_normalize_maps_clinical_synonyms_to_medical():
    result = normalize_services(["GP clinic", "primary care", "nursing", "health"])
    assert result == ["medical"]


def test_every_config_fallback_backfills_nonempty_services():
    import json

    with open("scraper/config/sources.json") as f:
        targets = json.load(f)["targets"]
    for t in targets:
        result = normalize_services(t["fallback"].get("services", []))
        assert result, f"{t['id']}: fallback backfills to empty services"


def test_normalize_keeps_multiword_slugs():
    assert "connectivity" in normalize_services(["WiFi & phone charging"])


def test_validate_rejects_unknown_need():
    loc = {
        "id": "x",
        "name": "X",
        "address": "1 St",
        "latitude": 53.3,
        "longitude": -6.2,
        "category": "Food",
        "services": ["dragon-riding"],
    }
    result = validate_location(loc)
    assert any("unknown need" in e for e in result["errors"])


def test_validate_accepts_curated_need():
    loc = {
        "id": "x",
        "name": "X",
        "address": "1 St",
        "latitude": 53.3,
        "longitude": -6.2,
        "category": "Food",
        "services": ["food"],
    }
    assert validate_location(loc)["errors"] == []

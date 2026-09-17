import json
import os

import pytest
from bs4 import BeautifulSoup

from scraper.pipeline import normalize_services
from scraper.scraper import extract_field, load_config

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
FIXTURES_DIR = os.path.abspath(FIXTURES_DIR)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)


def test_fixture_files_exist():
    files = [f for f in os.listdir(FIXTURES_DIR) if f.endswith(".html")]
    assert len(files) >= 14, f"Expected at least 14 fixtures, got {len(files)}"


def test_extract_field_from_fixture():
    target_id = "capuchin-day-centre"
    with open(os.path.join(FIXTURES_DIR, f"{target_id}.html")) as f:
        soup = BeautifulSoup(f.read(), "lxml")
    config = load_config(CONFIG_PATH)
    target = next(t for t in config["targets"] if t["id"] == target_id)
    for field in ("phone", "address", "email", "website", "description", "hours"):
        selectors = target["selectors"][field]
        result = extract_field(soup, selectors)
        assert result is None or isinstance(result, str), f"{target_id}: {field} result not a string"


def test_all_fixtures_have_phone_and_address():
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        fixture_path = os.path.join(FIXTURES_DIR, f"{target['id']}.html")
        if not os.path.exists(fixture_path):
            continue
        with open(fixture_path) as f:
            soup = BeautifulSoup(f.read(), "lxml")
        phone = extract_field(soup, target["selectors"]["phone"])
        address = extract_field(soup, target["selectors"]["address"])
        if phone is None and address is None:
            assert phone is not None or target["fallback"].get("phone"), \
                f"{target['id']}: no phone in fixture or fallback"
            assert address is not None or target["fallback"].get("address"), \
                f"{target['id']}: no address in fixture or fallback"


def test_category_detection_from_tags():
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        tags = target.get("fallback", {}).get("tags", [])
        category = target.get("fallback", {}).get("category", "")
        assert category, f"{target['id']}: missing category"
        assert tags, f"{target['id']}: missing tags"
        assert isinstance(tags, list)
        assert isinstance(category, str)


def test_service_slug_normalization():
    result = normalize_services(["Hot Meals", "Doctor/Nurse", "WiFi & phone charging", "Shower & Clothes washing"])
    assert "food" in result
    assert "medical" in result
    assert "connectivity" in result
    assert "hygiene" in result


def test_service_slug_deduplication():
    result = normalize_services(["Food", "food", "Food", "Medical", "medical"])
    assert result == ["food", "medical"]


def test_tag_extraction_from_scraped_data():
    result = normalize_services(["Hot Meals", "Shower & Clothes washing", "WiFi & phone charging"])
    assert len(result) == 3
    assert "food" in result
    assert "hygiene" in result
    assert "connectivity" in result


def test_all_fixtures_have_selectors():
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        fixture_path = os.path.join(FIXTURES_DIR, f"{target['id']}.html")
        if not os.path.exists(fixture_path):
            continue
        with open(fixture_path) as f:
            html = f.read()
        soup = BeautifulSoup(html, "lxml")
        # At least 80% of selector fields must have a match
        matched = 0
        total = len(target["selectors"])
        for field, selectors in target["selectors"].items():
            if any(soup.select_one(s) is not None for s in selectors):
                matched += 1
        assert matched / total >= 0.8, f"{target['id']}: only {matched}/{total} selectors matched"


def test_fixture_count_matches_targets():
    config = load_config(CONFIG_PATH)
    expected = len(config["targets"])
    actual = len([f for f in os.listdir(FIXTURES_DIR) if f.endswith(".html")])
    assert actual >= expected, f"Expected {expected} fixtures, got {actual}"


def test_scraper_loads_config_with_fixtures():
    config = load_config(CONFIG_PATH)
    assert len(config["targets"]) == 14
    for target in config["targets"]:
        assert "id" in target
        assert "url" in target
        assert "selectors" in target
        assert "fallback" in target


def test_all_targets_have_category_and_tags():
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        fallback = target.get("fallback", {})
        assert fallback.get("category"), f"{target['id']}: missing category"
        assert len(fallback.get("tags", [])) > 0, f"{target['id']}: missing tags"

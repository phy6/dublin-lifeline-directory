import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from overlay import (
    EDITORIAL_ALLOW_LIST,
    FACTUAL_PINNABLE,
    parse_overlay,
    apply_overlay,
)


def test_allow_list_covers_editorial_not_factual():
    assert "description" in EDITORIAL_ALLOW_LIST
    assert "address" not in EDITORIAL_ALLOW_LIST
    assert "address" in FACTUAL_PINNABLE or "hours" in FACTUAL_PINNABLE


def test_parse_overlay_frontmatter_and_body():
    text = "---\nid: test-centre\npinned: [phone]\ndescription: Nice place\n---\nBody notes here\n"
    ov = parse_overlay(text)
    assert ov["id"] == "test-centre"
    assert ov["pinned"] == ["phone"]
    assert ov["overrides"]["description"] == "Nice place"
    assert ov["notes"] == "Body notes here"


def test_editorial_allow_list_overrides_scrape():
    merged = {"id": "a", "description": "scraped desc", "category": "Food"}
    editorial = {"id": "a", "pinned": [], "overrides": {"description": "editorial desc"}, "notes": ""}
    out = apply_overlay(merged, editorial)
    assert out["description"] == "editorial desc"


def test_factual_stays_scrape_wins_unless_pinned():
    merged = {"id": "a", "phone": "scraped-phone", "address": "scraped-addr"}
    editorial = {
        "id": "a",
        "pinned": [],
        "overrides": {"phone": "editorial-phone", "address": "editorial-addr"},
        "notes": "",
    }
    out = apply_overlay(merged, editorial)
    assert out["phone"] == "scraped-phone"
    assert out["address"] == "scraped-addr"


def test_pinned_factual_overrides_scrape():
    merged = {"id": "a", "phone": "scraped-phone"}
    editorial = {"id": "a", "pinned": ["phone"], "overrides": {"phone": "editorial-phone"}, "notes": ""}
    out = apply_overlay(merged, editorial)
    assert out["phone"] == "editorial-phone"


def test_unknown_fields_ignored():
    merged = {"id": "a", "description": "x"}
    editorial = {"id": "a", "pinned": [], "overrides": {"__proto__": "evil"}, "notes": ""}
    out = apply_overlay(merged, editorial)
    assert "__proto__" not in out

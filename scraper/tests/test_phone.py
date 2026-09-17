import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from bs4 import BeautifulSoup

from scraper.phone import extract_phone, sanitize_phone, looks_like_phone
from scraper.scraper import extract_field, quarantine_junk


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extract_phone_finds_landline():
    assert extract_phone(soup("<p>Call us on 01 872 0185 today</p>")) == "01 872 0185"


def test_extract_phone_finds_mobile():
    assert extract_phone(soup("<p>Text 087 123 4567</p>")) == "087 123 4567"


def test_extract_phone_finds_freephone():
    assert extract_phone(soup("<p>CALL 1800 707 707</p>")) == "1800 707 707"


def test_extract_phone_returns_none_without_number():
    assert extract_phone(soup("<p>Call us for details</p>")) is None


def test_extract_field_phone_falls_back_to_mobile():
    html = "<div><p>Ring 086-123-4567 after 9am</p></div>"
    assert extract_field(soup(html), [".phone"], field="phone") == "086-123-4567"


def test_sanitize_phone_strips_labels():
    assert sanitize_phone("Freephone: 1800 78 68 28") == "1800 78 68 28"
    assert sanitize_phone("Tel:  01 872 0185") == "01 872 0185"
    assert sanitize_phone("01 872 0185") == "01 872 0185"


def test_looks_like_phone_gates_quarantine():
    assert looks_like_phone("Tel: 01 872 0185") is True
    assert looks_like_phone("call us for details") is False
    assert looks_like_phone(None) is False


def test_quarantine_junk_drops_undialable_phone():
    result = {
        "phone": "call us for details",
        "address": "somewhere",
        "services": ["food"],
    }
    reasons = quarantine_junk(result)
    assert result["phone"] is None
    assert any("phone" in r for r in reasons)


def test_quarantine_junk_keeps_dialable_phone():
    result = {
        "phone": "Tel: 01 872 0185",
        "address": "somewhere",
        "services": ["food"],
    }
    reasons = quarantine_junk(result)
    assert result["phone"] == "Tel: 01 872 0185"
    assert not any("phone" in r for r in reasons)

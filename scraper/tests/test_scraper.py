import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bs4 import BeautifulSoup
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scraper.scraper import load_config, extract_field, extract_services, fetch_with_fallback, DublinLifelineScraper, _RateLimiter, _retry_fetch, quarantine_junk

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
FIXTURES_DIR = os.path.abspath(FIXTURES_DIR)


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")


def test_extract_field_returns_first_match():
    html = '<div class="phone">555-1234</div><p class="contact-number">555-5678</p>'
    soup = BeautifulSoup(html, "lxml")
    result = extract_field(soup, [".phone", ".contact-number"])
    assert result == "555-1234"


def test_extract_field_returns_none_when_no_match():
    html = '<div>No matching element</div>'
    soup = BeautifulSoup(html, "lxml")
    result = extract_field(soup, [".phone", ".contact-number"])
    assert result is None


def test_load_config_returns_dict_with_13_targets():
    config = load_config(CONFIG_PATH)
    assert isinstance(config, dict)
    assert len(config["targets"]) == 13


def test_confirmed_targets_carry_registered_rcn():
    import re
    config = load_config(CONFIG_PATH)
    by_id = {t["id"]: t for t in config["targets"]}
    assert by_id["capuchin-day-centre"]["rcn"] == "20166120"
    assert by_id["crosscare"]["rcn"] == "20169084"
    assert by_id["alone"]["rcn"] == "20020057"
    for tid, target in by_id.items():
        if "rcn" in target:
            assert re.match(r"^\d{8}$", target["rcn"]), f"{tid}: malformed RCN"
            assert target.get("registered_name"), f"{tid}: rcn without registered_name"


def test_extract_field_returns_first_non_empty_match():
    html = '<div class="phone"></div><p class="contact-number">555-9999</p>'
    soup = BeautifulSoup(html, "lxml")
    result = extract_field(soup, [".phone", ".contact-number"])
    assert result == "555-9999"


def test_extract_field_website_prefers_href_over_link_text():
    html = '<nav><a class="nav-home" href="https://example.com/about">HOME</a></nav>'
    soup = BeautifulSoup(html, "lxml")
    assert extract_field(soup, [".nav-home"], "website") == "https://example.com/about"


def test_extract_field_website_skips_bare_nav_text():
    html = '<nav><a class="nav-home" href="/">HOME</a></nav>'
    soup = BeautifulSoup(html, "lxml")
    assert extract_field(soup, [".nav-home"], "website") == "/"


def test_quarantine_junk_flags_empty_record():
    result = {"id": "x", "address": None, "phone": None, "website": None, "services": []}
    reasons = quarantine_junk(result)
    assert len(reasons) == 1
    assert "empty record" in reasons[0]


def test_parse_hours_canonical_range():
    from scraper.scraper import parse_hours
    assert parse_hours("Mon-Fri 09:00-17:00") == {"mon-fri": "09:00-17:00"}


@pytest.mark.asyncio
async def test_retry_logic_works_with_mocked_failure():
    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.RequestError("Connection failed", request=MagicMock())
        resp = MagicMock()
        resp.text = "<html>success</html>"
        resp.raise_for_status = MagicMock()
        return resp

    client = httpx.AsyncClient()
    with patch.object(client, "get", side_effect=mock_get):
        from scraper.scraper import _retry_fetch
        result = await _retry_fetch(client, "http://example.com", max_attempts=3, base_delay=0.01)
        assert result == "<html>success</html>"
    await client.aclose()


@pytest.mark.asyncio
async def test_local_archive_fallback_when_fetch_fails():
    target = {
        "id": "capuchin-day-centre",
        "name": "Capuchin Day Centre",
        "url": "https://capuchindaycentre.ie/",
        "selectors": {"phone": ["a[href^=\"tel\"]"]},
    }
    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("Connection failed", request=MagicMock())
    transport = httpx.MockTransport(mock_get)
    client = httpx.AsyncClient(transport=transport)
    html, source = await fetch_with_fallback(target, DOCS_DIR, client=client)
    assert source == "archive"
    assert html is not None
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_with_fallback_returns_none_when_no_archive():
    target = {
        "id": "nonexistent-target",
        "name": "Nonexistent",
        "url": "https://example.invalid/",
        "selectors": {"phone": ["a[href^=\"tel\"]"]},
    }
    html, source = await fetch_with_fallback(target, DOCS_DIR)
    assert html is None
    assert source == "none"


@pytest.mark.asyncio
async def test_rate_limiter_adds_delay():
    limiter = _RateLimiter(interval=0.1, jitter=0.0)
    start = asyncio.get_event_loop().time()
    await limiter.wait()
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed >= 0.09


@pytest.mark.asyncio
async def test_scraper_run_returns_results(tmp_path):
    scraper = DublinLifelineScraper(CONFIG_PATH)
    # run() persists to output_dir: redirect at tmp so the test never
    # clobbers the real scraper/output/scraped_output.json.
    scraper.output_dir = str(tmp_path)
    results = await scraper.run(targets=["capuchin-day-centre", "focus-ireland"])
    assert len(results) == 2
    assert results[0]["id"] == "capuchin-day-centre"
    assert results[1]["id"] == "focus-ireland"
    assert results[0]["source"] in ("live", "archive", "quarantined")


def test_all_config_targets_have_tags_and_category():
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        fallback = target.get("fallback", {})
        assert len(fallback.get("tags", [])) > 0, f"{target['id']}: missing tags"
        assert fallback.get("category"), f"{target['id']}: missing category"


def test_tag_patterns_are_valid_slugs():
    import re
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        for tag in target.get("tags", []):
            assert re.match(r"^[a-z-]+$", tag), f"{target['id']}: tag '{tag}' is not a valid slug"


def test_extract_services_from_fixture():
    target_id = "capuchin-day-centre"
    with open(os.path.join(FIXTURES_DIR, f"{target_id}.html")) as f:
        soup = BeautifulSoup(f.read(), "lxml")
    from scraper.scraper import extract_services
    services = extract_services(soup)
    assert "food" in services
    assert "shelter" in services
    assert len(services) > 0


def test_quarantine_junk_strips_chrome_text_website():
    result = {"id": "x", "website": "HOME", "address": "1 Main St"}
    reasons = quarantine_junk(result)
    assert len(reasons) == 1
    assert "website" in reasons[0]
    assert result["website"] is None
    assert result["address"] == "1 Main St"


def test_quarantine_junk_strips_malformed_email():
    result = {"id": "x", "email": "Campaigns", "website": "https://example.com"}
    reasons = quarantine_junk(result)
    assert len(reasons) == 1
    assert result["email"] is None
    assert result["website"] == "https://example.com"


def test_quarantine_junk_passes_clean_result():
    result = {"id": "x", "website": "https://example.com", "email": "a@example.com", "address": None}
    assert quarantine_junk(result) == []
    assert result["website"] == "https://example.com"


@pytest.mark.asyncio
async def test_fetch_target_quarantines_live_junk():
    scraper = DublinLifelineScraper(CONFIG_PATH)
    target = {
        "id": "junk-target",
        "name": "Junk Target",
        "url": "https://example.com/",
        "selectors": {"website": [".nav-home"]},
        "fallback": {},
    }
    html = '<html><body><span class="nav-home">HOME</span></body></html>'
    with patch("scraper.scraper.fetch_with_fallback", new=AsyncMock(return_value=(html, "live"))):
        result = await scraper.fetch_target(target)
    assert result["source"] == "quarantined"
    assert result["website"] is None
    assert len(result["quarantine_reasons"]) == 1


@pytest.mark.asyncio
async def test_fetch_target_keeps_clean_live_result():
    scraper = DublinLifelineScraper(CONFIG_PATH)
    target = {
        "id": "clean-target",
        "name": "Clean Target",
        "url": "https://example.com/",
        "selectors": {"phone": [".phone"]},
        "fallback": {},
    }
    html = '<html><body><span class="phone">01-2345678</span></body></html>'
    with patch("scraper.scraper.fetch_with_fallback", new=AsyncMock(return_value=(html, "live"))):
        result = await scraper.fetch_target(target)
    assert result["source"] == "live"
    assert "quarantine_reasons" not in result


@pytest.mark.asyncio
async def test_fetch_target_uses_contact_url_when_homepage_empty():
    scraper = DublinLifelineScraper(CONFIG_PATH)
    target = {
        "id": "contact-target",
        "name": "Contact Target",
        "url": "https://example.com/",
        "contactUrl": "https://example.com/contact/",
        "selectors": {"phone": [".phone"], "email": ["a.contact-mail"]},
        "fallback": {},
    }
    home_html = '<html><body><p>Welcome, no contact info here</p></body></html>'
    contact_html = '<html><body><span class="phone">01-8780404</span><a class="contact-mail" href="mailto:info@example.com">Email</a></body></html>'
    with (
        patch("scraper.scraper.fetch_with_fallback", new=AsyncMock(return_value=(home_html, "live"))),
        patch("scraper.scraper._retry_fetch", new=AsyncMock(return_value=contact_html)),
    ):
        result = await scraper.fetch_target(target)
    assert result["phone"] == "01-8780404"
    assert result["email"] == "info@example.com"
    assert result.get("contactFallback") is True
    assert result["source"] == "live"


def test_extract_field_phone_regex_fallback():
    html = '<div><p>Call us on 01 836 0011 today</p></div>'
    soup = BeautifulSoup(html, "lxml")
    assert extract_field(soup, [".phone", ".contact-number"], "phone") == "01 836 0011"


def test_extract_field_phone_selector_beats_regex():
    html = '<div><span class="phone">01-1111111</span><p>Also 01 836 0011</p></div>'
    soup = BeautifulSoup(html, "lxml")
    assert extract_field(soup, [".phone"], "phone") == "01-1111111"


@pytest.mark.asyncio
async def test_fetch_with_fallback_retries_insecure_tls(tmp_path):
    from scraper.scraper import fetch_with_fallback
    target = {"id": "tls-target", "name": "TLS", "url": "https://example.com/", "fallback": {}}
    with patch("scraper.scraper._retry_fetch", side_effect=[Exception("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"), "<html></html>"]) as m:
        html, source = await fetch_with_fallback(target, str(tmp_path))
    assert source == "live"
    assert html == "<html></html>"
    assert m.call_count == 2


def test_quarantined_maps_to_fallback_in_merge():
    from scraper.pipeline import merge_location
    scraped = {"id": "x", "name": "X", "source": "quarantined", "services": [], "fallback": {}}
    merged = merge_location(scraped, flyer=None, fallback={})
    assert merged["dataSource"] == "fallback"
    assert merged["scrapeSuccess"] is False


def test_tag_patterns_are_valid_slugs():
    import re
    config = load_config(CONFIG_PATH)
    for target in config["targets"]:
        for tag in target.get("tags", []):
            assert re.match(r"^[a-z-]+$", tag), f"{target['id']}: tag '{tag}' is not a valid slug"

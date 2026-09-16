import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bs4 import BeautifulSoup
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scraper.scraper import load_config, extract_field, fetch_with_fallback, DublinLifelineScraper, _RateLimiter, _retry_fetch


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


def test_load_config_returns_dict_with_14_targets():
    config = load_config(CONFIG_PATH)
    assert isinstance(config, dict)
    assert len(config["targets"]) == 14


def test_extract_field_returns_first_non_empty_match():
    html = '<div class="phone"></div><p class="contact-number">555-9999</p>'
    soup = BeautifulSoup(html, "lxml")
    result = extract_field(soup, [".phone", ".contact-number"])
    assert result == "555-9999"


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
async def test_scraper_run_returns_results():
    scraper = DublinLifelineScraper(CONFIG_PATH)
    results = await scraper.run(targets=["capuchin-day-centre", "focus-ireland"])
    assert len(results) == 2
    assert results[0]["id"] == "capuchin-day-centre"
    assert results[1]["id"] == "focus-ireland"
    assert results[0]["source"] in ("live", "archive")

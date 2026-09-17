import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scraper import DublinLifelineScraper

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")

DIR_HTML = """
<html><body>
<h2><a href="https://example.com/org/alpha">Alpha Centre</a></h2>
<h3><a href="https://example.org/beta">Beta Shelter</a></h3>
<div class="org-name"><a href="/gamma">Gamma House</a></div>
<h2><a href="mailto:x@y.z">Mail link</a></h2>
<h2><a href="https://example.com/org/alpha">Alpha Centre</a></h2>
</body></html>
"""


def _make_scraper():
    s = DublinLifelineScraper(CONFIG_PATH)
    s.config["discovery"] = {
        "urls": ["https://directory.example.net/dir"],
        "selectors": {"name": ["h2 a", "h3 a", ".org-name"]},
        "interval": 0,
        "maxResults": 10,
    }
    return s


@pytest.mark.asyncio
async def test_discover_providers_parses_links_dedupes_and_skips_self_links():
    s = _make_scraper()

    async def fake_retry(client, url, timeout=5.0, max_attempts=3, base_delay=2.0):
        return DIR_HTML

    with patch("scraper.scraper._retry_fetch", side_effect=fake_retry):
        with patch("asyncio.sleep", new=AsyncMock()):
            res = await s.discover_providers()

    # Gamma resolves to the directory host itself -> excluded; Alpha deduped; mailto excluded.
    assert len(res) == 2
    assert res[0]["name"] == "Alpha Centre"
    assert res[0]["url"] == "https://example.com/org/alpha"
    urls = [r["url"] for r in res]
    assert "https://example.org/beta" in urls
    assert not any(u.startswith("mailto:") for u in urls)
    assert not any("Gamma" in r["name"] for r in res)


@pytest.mark.asyncio
async def test_discover_providers_returns_empty_when_no_discovery_config():
    s = DublinLifelineScraper(CONFIG_PATH)
    s.config.pop("discovery", None)
    res = await s.discover_providers()
    assert res == []


@pytest.mark.asyncio
async def test_run_discovery_slugifies_and_extracts_services():
    from scraper.main import run_discovery

    mock_scraper = MagicMock()
    mock_scraper.docs_dir = "/tmp"
    mock_scraper.discover_providers = AsyncMock(
        return_value=[
            {"name": "Alpha Centre", "url": "https://example.com/alpha", "source": "https://example.com/dir"},
            {"name": "Beta! Shelter @Dublin", "url": "https://example.com/beta", "source": "https://example.com/dir"},
        ]
    )
    fake_html = "<html><body><h3>Food and Meal Services</h3></body></html>"
    with patch(
        "scraper.main.fetch_with_fallback",
        new=AsyncMock(side_effect=[(fake_html, "live"), (None, "none")]),
    ):
        res = await run_discovery(mock_scraper, no_fallback=False)

    assert res[0]["id"] == "alpha-centre"
    assert res[1]["id"] == "beta-shelter-dublin"
    assert res[0]["services"] == ["food"]
    assert res[1]["services"] == []


@pytest.mark.asyncio
async def test_run_discovery_no_fallback_raises():
    from scraper.main import run_discovery

    mock_scraper = MagicMock()
    mock_scraper.docs_dir = "/tmp"
    mock_scraper.discover_providers = AsyncMock(
        return_value=[{"name": "Alpha", "url": "https://example.com/a", "source": "d"}]
    )
    with patch("scraper.main.fetch_with_fallback", new=AsyncMock(return_value=(None, "none"))):
        with pytest.raises(RuntimeError):
            await run_discovery(mock_scraper, no_fallback=True)


FOCUS_HTML = """
<html><body><div class="two-col-content__row"><div>
<h3>Advice, information, advocacy and support</h3>
<ul>
<li><a href="http://www.threshold.ie/">Threshold</a></li>
<li><a href="https://www.svp.ie/Home.aspx">Saint Vincent DePaul</a></li>
</ul>
<h3>Legal</h3>
<ul><li><a href="https://mercylaw.ie/">Mercy Law Resource Centre</a></li></ul>
</div></div></body></html>
"""


@pytest.mark.asyncio
async def test_discover_dict_entry_uses_scoped_selectors_and_category():
    s = DublinLifelineScraper(CONFIG_PATH)
    s.config["discovery"] = {
        "urls": [
            {
                "url": "https://example.com/orgs",
                "name_selectors": [".two-col-content__row li a"],
                "capture_category": True,
            }
        ],
        "selectors": {"name": ["h2 a"]},
        "interval": 0,
        "maxResults": 10,
    }

    async def fake_retry(client, url, timeout=5.0, max_attempts=3, base_delay=2.0):
        return FOCUS_HTML

    with patch("scraper.scraper._retry_fetch", side_effect=fake_retry):
        with patch("asyncio.sleep", new=AsyncMock()):
            res = await s.discover_providers()

    assert len(res) == 3
    by_name = {r["name"]: r for r in res}
    assert by_name["Threshold"]["category"] == "Advice, information, advocacy and support"
    assert by_name["Mercy Law Resource Centre"]["category"] == "Legal"
    assert by_name["Threshold"]["url"] == "http://www.threshold.ie/"


@pytest.mark.asyncio
async def test_discover_string_entry_stays_backward_compatible():
    s = DublinLifelineScraper(CONFIG_PATH)
    s.config["discovery"] = {
        "urls": ["https://directory.example.net/dir"],
        "selectors": {"name": ["h2 a"]},
        "interval": 0,
        "maxResults": 10,
    }
    html = '<html><body><h2><a href="https://example.com/x">X Org</a></h2></body></html>'

    async def fake_retry(client, url, timeout=5.0, max_attempts=3, base_delay=2.0):
        return html

    with patch("scraper.scraper._retry_fetch", side_effect=fake_retry):
        with patch("asyncio.sleep", new=AsyncMock()):
            res = await s.discover_providers()

    assert len(res) == 1
    assert res[0]["name"] == "X Org"
    assert "category" not in res[0]


@pytest.mark.asyncio
async def test_discover_skips_links_back_to_directory_itself():
    s = DublinLifelineScraper(CONFIG_PATH)
    s.config["discovery"] = {
        "urls": ["https://directory.example.net/orgs"],
        "selectors": {"name": ["li a"]},
        "interval": 0,
        "maxResults": 10,
    }
    html = (
        '<html><body><ul>'
        '<li><a href="https://directory.example.net/">Directory Home</a></li>'
        '<li><a href="https://example.org/real-org">Real Org</a></li>'
        "</ul></body></html>"
    )

    async def fake_retry(client, url, timeout=5.0, max_attempts=3, base_delay=2.0):
        return html

    with patch("scraper.scraper._retry_fetch", side_effect=fake_retry):
        with patch("asyncio.sleep", new=AsyncMock()):
            res = await s.discover_providers()

    assert [r["name"] for r in res] == ["Real Org"]

"""Foundations-done data gate (04): 5-10 real orgs render name/needs/contact."""

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICES_PATH = os.path.join(PROJECT_ROOT, "src", "lib", "data", "services.json")


def test_data_gate_min_five_renderable_orgs():
    with open(SERVICES_PATH) as f:
        data = json.load(f)
    renderable = [
        s
        for s in data.get("services", [])
        if s.get("name") and (s.get("phone") or s.get("email") or s.get("website") or s.get("address"))
    ]
    assert len(renderable) >= 5, f"data gate needs >=5 renderable orgs, found {len(renderable)}"


def test_data_gate_includes_scraped_orgs():
    with open(SERVICES_PATH) as f:
        data = json.load(f)
    scraped = [s for s in data.get("services", []) if s.get("scrapeSuccess")]
    assert len(scraped) >= 5, f"data gate needs >=5 scraped orgs, found {len(scraped)}"

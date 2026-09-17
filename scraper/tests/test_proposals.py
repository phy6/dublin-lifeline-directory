import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scraper.register_proposals import build_proposals, normalize_name, summarize


def _cand(name, rcn="20000001", aka=None):
    return {
        "rcn": rcn,
        "name": name,
        "aka": aka,
        "status": "Registered",
        "classification": "",
        "address": "Dublin",
        "purpose": "",
    }


def _target(tid, name):
    return {"id": tid, "name": name, "url": "https://example.com", "selectors": {}}


def test_normalize_strips_legal_suffixes():
    assert normalize_name("Focus Ireland Limited") == "focus ireland"
    assert normalize_name("Mendicity Institution Company Limited By Guarantee") == "mendicity institution"
    assert normalize_name("  Dublin   Simon!! ") == "dublin simon"


def test_trading_name_contained_in_registered_name_is_near_match():
    targets = [_target("crosscare", "Crosscare")]
    cands = [_cand("Crosscare Catholic Social Services")]
    res = build_proposals(cands, targets)
    assert res["matched"] == []
    assert len(res["near_matches"]) == 1
    assert res["near_matches"][0]["target_id"] == "crosscare"


def test_exact_match_on_name_or_aka():
    targets = [_target("focus-ireland", "Focus Ireland")]
    cands = [_cand("Some Other Org", aka="Focus Ireland")]
    res = build_proposals(cands, targets)
    assert len(res["matched"]) == 1
    assert res["matched"][0]["target_id"] == "focus-ireland"
    assert res["near_matches"] == [] and res["new_orgs"] == []


def test_brand_new_org_listed_separately():
    targets = [_target("focus-ireland", "Focus Ireland")]
    cands = [_cand("Threshold")]
    res = build_proposals(cands, targets)
    assert len(res["new_orgs"]) == 1
    assert res["unmatched_targets"] == [{"id": "focus-ireland", "name": "Focus Ireland"}]


def test_summarize_fits_chat_message():
    proposals = {
        "matched": [{"target_id": "a", "rcn": "1", "name": "A"}],
        "near_matches": [{"target_id": "b", "candidate_name": "B Org", "candidate_rcn": "2", "matched_on": "b"}],
        "new_orgs": [],
        "unmatched_targets": [{"id": "c", "name": "C"}],
    }
    text = summarize(proposals)
    assert "1 matched" in text
    assert "Is 'B Org' (RCN 2) == b? (yes/no)" in text
    assert "Missing from register cut: c" in text
    assert len(text) < 1000

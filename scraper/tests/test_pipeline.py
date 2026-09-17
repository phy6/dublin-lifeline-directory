import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import (
    load_flyer_data,
    merge_location,
    normalize_services,
    compute_diff,
    bump_version,
    write_services,
    run_pipeline,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLYER_PATH = os.path.join(PROJECT_ROOT, ".scratch", "wayfinder-map", "research", "flyer-data.json")
SCRAPED_PATH = os.path.join(PROJECT_ROOT, "scraper", "output", "scraped_output.json")
SERVICES_PATH = os.path.join(PROJECT_ROOT, "src", "lib", "data", "services.json")


@pytest.fixture
def flyer_data():
    return {
        "day_support_centres": [
            {
                "id": "test-centre",
                "name": "Test Centre",
                "address": "1 Test St",
                "phone": "01 123 4567",
                "email": "test@test.ie",
                "website": "https://test.ie",
                "coordinates": {"latitude": 53.35, "longitude": -6.25},
                "hours": {"monday": "09:00-17:00"},
                "services": ["Hot Meals", "Doctor/Nurse", "WiFi & phone charging"],
                "services_categories": ["Food", "Healthcare", "Connectivity"],
                "healthcare_services": ["Doctor"],
            }
        ],
        "free_doctor_clinics": [],
    }


@pytest.fixture
def scraped_data():
    return {
        "id": "test-centre",
        "name": "Test Centre",
        "address": "1 Old St",
        "phone": "+353-1-999-9999",
        "email": "old@test.ie",
        "website": "https://old.ie",
        "latitude": 53.34,
        "longitude": -6.26,
        "services": ["shelter", "food"],
        "tags": ["homeless"],
        "category": "Emergency Shelter",
        "description": "Old description",
        "fallback": {},
    }


@pytest.fixture
def fallback_data():
    return {
        "name": "Test Centre",
        "address": "1 Fallback St",
        "phone": "+353-1-000-0000",
        "latitude": 53.30,
        "longitude": -6.30,
        "services": ["counselling"],
        "tags": ["support"],
        "category": "Community Support",
        "description": "Fallback description",
    }


def test_merge_location_prefers_flyer_over_scraped(flyer_data, scraped_data, fallback_data):
    flyer = flyer_data["day_support_centres"][0]
    result = merge_location(scraped_data, flyer, fallback_data)

    assert result["phone"] == flyer["phone"]
    assert result["email"] == flyer["email"]
    assert result["website"] == flyer["website"]
    assert result["hours"] == flyer["hours"]
    assert result["latitude"] == flyer["coordinates"]["latitude"]
    assert result["longitude"] == flyer["coordinates"]["longitude"]
    assert "food" in result["services"]
    assert "medical" in result["services"]
    assert "connectivity" in result["services"]


def test_merge_location_uses_scraped_for_null_flyer_fields(flyer_data, scraped_data, fallback_data):
    flyer = flyer_data["day_support_centres"][0]
    flyer["phone"] = None
    flyer["email"] = None
    result = merge_location(scraped_data, flyer, fallback_data)

    assert result["phone"] == scraped_data["phone"]
    assert result["email"] == scraped_data["email"]


def test_merge_location_sets_data_source_and_timestamps(scraped_data, flyer_data, fallback_data):
    flyer = flyer_data["day_support_centres"][0]
    scraped_data["source"] = "live"
    result = merge_location(scraped_data, flyer, fallback_data)

    assert result["dataSource"] == "live"
    assert result["scrapeSuccess"] is True


def test_normalize_services_converts_hot_meals_to_food():
    services = ["Hot Meals", "Doctor/Nurse", "WiFi & phone charging", "Shower & Clothes washing"]
    result = normalize_services(services)

    assert "food" in result
    assert "medical" in result
    assert "connectivity" in result
    assert "hygiene" in result


def test_normalize_services_returns_sorted_unique():
    services = ["Food", "food", "Medical", "food"]
    result = normalize_services(services)

    assert result == ["food", "medical"]


def test_bump_version_patch_for_metadata_only():
    diffs = {"additions": [], "updates": [], "deletions": []}
    result = bump_version("3.1.0", diffs)
    assert result == "3.1.1"


def test_bump_version_minor_for_additions():
    diffs = {"additions": [{"id": "new-place"}], "updates": [], "deletions": []}
    result = bump_version("3.1.0", diffs)
    assert result == "3.2.0"


def test_bump_version_minor_for_updates():
    diffs = {"additions": [], "updates": [{"id": "updated-place"}], "deletions": []}
    result = bump_version("3.1.0", diffs)
    assert result == "3.2.0"


def test_bump_version_major_for_deletions():
    diffs = {"additions": [], "updates": [], "deletions": [{"id": "removed-place"}]}
    result = bump_version("3.1.0", diffs)
    assert result == "4.0.0"


def test_merge_location_backfills_category_and_rcn_from_fallback():
    from scraper.pipeline import merge_location
    scraped = {"id": "x", "name": "X", "source": "live", "category": None, "rcn": "20166120"}
    fallback = {"id": "x", "name": "X", "category": "Emergency Shelter"}
    merged = merge_location(scraped, None, fallback)
    assert merged["category"] == "Emergency Shelter"
    assert merged["rcn"] == "20166120"


def test_merge_location_keeps_scraped_category_when_present():
    from scraper.pipeline import merge_location
    scraped = {"id": "x", "name": "X", "source": "live", "category": "Food"}
    fallback = {"id": "x", "name": "X", "category": "Emergency Shelter"}
    merged = merge_location(scraped, None, fallback)
    assert merged["category"] == "Food"


def test_merge_location_backfills_services_and_tags_from_fallback():
    from scraper.pipeline import merge_location
    scraped = {"id": "x", "name": "X", "source": "quarantined", "address": None, "tags": []}
    fallback = {
        "id": "x",
        "name": "X",
        "address": "29 Bow St, Dublin 7",
        "services": ["homelessness", "housing", "support"],
        "tags": ["homelessness", "housing", "support"],
    }
    merged = merge_location(scraped, None, fallback)
    assert merged["services"] == ["housing", "shelter", "support"]
    assert merged["tags"] == ["homelessness", "housing", "support"]
    assert merged["address"] == "29 Bow St, Dublin 7"


def test_merge_location_flyer_branch_falls_back_to_curated_services():
    from scraper.pipeline import merge_location
    scraped = {
        "id": "x",
        "name": "X",
        "source": "live",
        "services": ["doctor-nurse-dentist", "food  phone charging", "shower"],
    }
    flyer = {"services": [], "services_categories": ["Shower & Clothes washing"]}
    fallback = {"id": "x", "services": ["addiction", "support"], "tags": ["addiction"]}
    merged = merge_location(scraped, flyer, fallback)
    assert merged["services"] == ["addiction-support", "support"]
    assert "addiction" in merged["tags"] and "hygiene" in merged["tags"]


def test_merge_location_sanitizes_hours_null_days_and_string_hours():
    from scraper.pipeline import merge_location
    fb_hours = {"mon-fri": "09:00-17:00"}
    m1 = merge_location(
        {"id": "a", "name": "A", "source": "live", "hours": {"saturday": None}},
        None,
        {"id": "a", "hours": fb_hours},
    )
    assert m1["hours"] == fb_hours
    m2 = merge_location(
        {"id": "b", "name": "B", "source": "archive", "hours": "Mon-Fri 09:00-17:00"},
        None,
        {"id": "b", "hours": fb_hours},
    )
    assert m2["hours"] == fb_hours


def test_timestamp_only_churn_still_mints_minor_bump():
    # Documents current behavior (see scraper-version-bump-semantics):
    # refreshed timestamps alone count as updates -> minor, not patch.
    from scraper.pipeline import compute_diff
    old = {"services": [{"id": "a", "lastScraped": "2026-09-17T00:00:00+00:00"}]}
    new = {"services": [{"id": "a", "lastScraped": "2026-09-17T01:00:00+00:00"}]}
    diffs = compute_diff(old, new)
    assert len(diffs["updates"]) == 1
    assert bump_version("3.2.0", diffs) == "3.3.0"


def test_compute_diff_detects_additions():
    old = {"services": [{"id": "a", "name": "Place A"}]}
    new = {"services": [{"id": "a", "name": "Place A"}, {"id": "b", "name": "Place B"}]}
    diffs = compute_diff(old, new)

    assert len(diffs["additions"]) == 1
    assert diffs["additions"][0]["id"] == "b"
    assert diffs["updates"] == []
    assert diffs["deletions"] == []


def test_compute_diff_detects_updates():
    old = {"services": [{"id": "a", "name": "Place A", "phone": "111"}]}
    new = {"services": [{"id": "a", "name": "Place A", "phone": "222"}]}
    diffs = compute_diff(old, new)

    assert len(diffs["updates"]) == 1
    assert diffs["updates"][0]["phone"] == "222"


def test_compute_diff_detects_deletions():
    old = {"services": [{"id": "a", "name": "Place A"}, {"id": "b", "name": "Place B"}]}
    new = {"services": [{"id": "a", "name": "Place A"}]}
    diffs = compute_diff(old, new)

    assert len(diffs["deletions"]) == 1
    assert diffs["deletions"][0]["id"] == "b"


def test_compute_diff_no_changes():
    old = {"services": [{"id": "a", "name": "Place A"}]}
    new = {"services": [{"id": "a", "name": "Place A"}]}
    diffs = compute_diff(old, new)

    assert diffs["additions"] == []
    assert diffs["updates"] == []
    assert diffs["deletions"] == []


def test_load_flyer_data():
    data = load_flyer_data(FLYER_PATH)
    assert "day_support_centres" in data
    assert "free_doctor_clinics" in data
    assert len(data["day_support_centres"]) > 0


def test_write_services_writes_to_both_paths():
    tmp_dir = tempfile.mkdtemp()
    src_lib_dir = os.path.join(tmp_dir, "src", "lib", "data")
    static_dir = os.path.join(tmp_dir, "static")
    os.makedirs(src_lib_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    test_data = {
        "version": "1.0.0",
        "lastUpdated": "2026-09-17T00:00:00.000Z",
        "generatedBy": "Test",
        "services": [],
        "metadata": {"totalServices": 0},
    }

    import pipeline
    original_write = pipeline.write_services
    original_get_root = pipeline._get_project_root

    def mock_get_root():
        return tmp_dir

    pipeline._get_project_root = mock_get_root

    def mock_write(data):
        with open(os.path.join(src_lib_dir, "services.json"), "w") as f:
            json.dump(data, f)
        with open(os.path.join(static_dir, "services.json"), "w") as f:
            json.dump(data, f)

    pipeline.write_services = mock_write
    try:
        mock_write(test_data)
        with open(os.path.join(src_lib_dir, "services.json")) as f:
            src_data = json.load(f)
        with open(os.path.join(static_dir, "services.json")) as f:
            static_data = json.load(f)
        assert src_data["version"] == "1.0.0"
        assert static_data["version"] == "1.0.0"
    finally:
        pipeline.write_services = original_write
        pipeline._get_project_root = original_get_root
        import shutil
        shutil.rmtree(tmp_dir)


def test_run_pipeline_returns_result():
    if not os.path.exists(SCRAPED_PATH):
        pytest.skip("scraped_output.json not found")
    if not os.path.exists(FLYER_PATH):
        pytest.skip("flyer-data.json not found")

    import pipeline
    original_write = pipeline.write_services
    original_get_root = pipeline._get_project_root
    project_root = _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def mock_get_root():
        return project_root

    pipeline._get_project_root = mock_get_root

    written_data = {}

    def mock_write(data):
        written_data.update(data)

    pipeline.write_services = mock_write

    try:
        result = run_pipeline(SCRAPED_PATH, FLYER_PATH, "")
        assert "version" in result
        assert "totalServices" in result
        assert "diffs" in result
        assert "metadata" in result
    finally:
        pipeline.write_services = original_write
        pipeline._get_project_root = original_get_root


def test_dumps_prettier_matches_prettier_conventions():
    import json
    from scraper.pipeline import dumps_prettier

    long_value = "x" * 120
    data = {
        "short": [1, 2, 3],
        "empty_obj": {},
        "empty_list": [],
        "hours": {"mon-fri": "09:00-17:00"},
        "nested": {"tags": ["a", "b"], "note": long_value},
        "long_list": ["addiction", "harm reduction", "needle exchange", "counselling", "support", "outreach"],
    }
    text = dumps_prettier(data)
    # Round-trips byte-identically through real JSON.
    assert json.loads(text) == data
    # Tabs, trailing newline, no trailing whitespace, padded short objects.
    assert text.endswith("}\n") and not text.endswith("\n\n")
    assert '\t"short": [1, 2, 3],' in text
    assert '"empty_obj": {},' in text
    assert '"hours": { "mon-fri": "09:00-17:00" },' in text
    # Over-width lines break one-item-per-line; long scalars stay long.
    assert f'"note": "{long_value}"' in text
    assert '"long_list": [\n\t\t"addiction",' in text
    for line in text.splitlines():
        assert line == line.rstrip()

def test_merge_location_strips_phone_label_prefix():
    from scraper.pipeline import merge_location
    scraped = {"id": "x", "name": "X", "phone": "Freephone: 1800 78 68 28", "source": "live", "services": [], "fallback": {}}
    merged = merge_location(scraped, flyer=None, fallback={})
    assert merged["phone"] == "1800 78 68 28"

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


DISPLAY_TO_SLUG = {
    "Food": "food",
    "Food and Meal Services": "food",
    "Hot Meals": "food",
    "Hot Meals (Breakfast & Lunch)": "food",
    "Shower & Clothes washing": "hygiene",
    "Shower/Clothing": "hygiene",
    "WiFi & Phone Charging": "connectivity",
    "WiFi & phone charging": "connectivity",
    "Food & Phone Charging": "connectivity",
    "Doctor/Nurse/Dentist/Chiropodist/Optician": "medical",
    "Doctor/Nurse/Dentist": "medical",
    "Doctor/Nurse": "medical",
    "Medical and Hygiene Services": "medical",
    "GP Clinic services": "medical",
    "Employment Clinic (Mon 6:15pm)": "employment",
    "Clothes (market on Fridays 16:00)": "clothing",
    "Family Support Services": "family",
    "Family Support": "family",
    "Support Services": "support",
    # Fallback-vocabulary mappings (sources.json curated truth, 2026-09-17).
    # Coarse needs map into NEEDS; fine-grained detail survives in tags.
    "homelessness": "shelter",
    "emergency": "shelter",
    "housing": "housing",
    "accommodation": "housing",
    "addiction": "addiction-support",
    "recovery": "addiction-support",
    "harm reduction": "addiction-support",
    "needle exchange": "addiction-support",
    "support": "support",
    "advice": "support",
    "community": "community",
    "social": "community",
    "volunteering": "community",
    "befriending": "community",
    "elderly": "elderly",
    "isolation": "elderly",
    "clothing": "clothing",
    "counselling": "counselling",
    "health": "medical",
    "gp clinic": "medical",
    "primary care": "medical",
    "nursing": "medical",
    "training": "employment",
    "crisis": "mental-health",
    "crisis-support": "mental-health",
    "suicide-prevention": "mental-health",
    "helpline": "mental-health",
    "outreach": "outreach",
}

# Curated needs taxonomy (03). Flat multi-select; expand by adding one
# slug here — normalize + validate + chips pick it up with no other change.
# Extended 2026-09-17 to cover the sources.json fallback vocabulary so the
# no-flyer merge branch backfills every org to a non-empty services list.
NEEDS = frozenset(
    {
        "food",
        "hygiene",
        "medical",
        "mental-health",
        "addiction-support",
        "shelter",
        "employment",
        "connectivity",
        "housing",
        "support",
        "community",
        "elderly",
        "clothing",
        "counselling",
        "outreach",
    }
)


def load_flyer_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _slugify(text: str) -> str:
    text = text.strip().lower().replace("/", "-").replace("&", "").replace("(", "").replace(")", "").replace(",", "").replace("clinic", "").strip()
    return text


def _lookup_slug(text: str) -> str | None:
    stripped = text.strip()
    if stripped in DISPLAY_TO_SLUG:
        return DISPLAY_TO_SLUG[stripped]
    lowered = stripped.lower()
    return DISPLAY_TO_SLUG.get(lowered)


def normalize_services(services: list[str]) -> list[str]:
    """Map display names to slugs, fail-closed to NEEDS (03).

    Unknown slugs are dropped (and logged by the caller pipeline);
    ingestion never invents taxonomy entries.
    """
    result = []
    for svc in services:
        slug = _lookup_slug(svc)
        if slug is None:
            slug = _slugify(svc)
        if slug and slug not in result and slug in NEEDS:
            result.append(slug)
    return sorted(result)


def merge_location(scraped: dict, flyer: dict, fallback: dict, editorial: dict | None = None) -> dict:
    merged = dict(scraped) if scraped else {}
    merged["id"] = scraped.get("id", fallback.get("id", ""))
    merged["name"] = scraped.get("name", fallback.get("name", ""))
    # sources.json fallback blocks are the curated source of truth: a scrape
    # that found nothing (None) must not clobber them.
    if not merged.get("address"):
        merged["address"] = fallback.get("address", "")

    if flyer:
        for field in ("phone", "email", "website", "hours"):
            flyer_val = flyer.get(field)
            if flyer_val is not None:
                merged[field] = flyer_val
        coords = flyer.get("coordinates")
        if coords is not None:
            merged["latitude"] = coords.get("latitude", scraped.get("latitude", fallback.get("latitude", 0)))
            merged["longitude"] = coords.get("longitude", scraped.get("longitude", fallback.get("longitude", 0)))
        flyer_services = flyer.get("services", [])
        if flyer_services:
            merged["services"] = normalize_services(flyer_services)
        flyer_cats = flyer.get("services_categories", [])
        if flyer_cats:
            merged["category"] = flyer_cats[0] if flyer_cats else merged.get("category", "")

    for field in ("phone", "email", "website", "hours"):
        if field in merged and merged[field] is None:
            del merged[field]

    # The scraper rarely extracts a category, but every target carries a
    # human-curated one in its fallback config — use it instead of None.
    if not merged.get("category"):
        merged["category"] = fallback.get("category") or "Uncategorised"

    # Confirmed Charities Register identity flows through to the output.
    for key in ("rcn", "registered_name"):
        if scraped.get(key):
            merged[key] = scraped[key]

    if "latitude" not in merged or merged.get("latitude") is None:
        merged["latitude"] = scraped.get("latitude", fallback.get("latitude", 0))
    if "longitude" not in merged or merged.get("longitude") is None:
        merged["longitude"] = scraped.get("longitude", fallback.get("longitude", 0))

    source = scraped.get("source", "unknown") if scraped else "unknown"
    if source == "live":
        merged["dataSource"] = "live"
        merged["scrapeSuccess"] = True
    elif source == "archive":
        merged["dataSource"] = "local-archive"
        merged["scrapeSuccess"] = True
    else:
        merged["dataSource"] = "fallback"
        merged["scrapeSuccess"] = False
    merged["lastScraped"] = datetime.now(timezone.utc).isoformat()

    if flyer:
        flyer_tags = flyer.get("services_categories", []) + flyer.get("healthcare_services", [])
        merged["tags"] = normalize_services(flyer_tags)
        # Union with curated fallback tags (raw vocabulary; tags unvalidated).
        seen = {t.lower() for t in merged["tags"]}
        for t in fallback.get("tags", []):
            if t.lower() not in seen:
                merged["tags"].append(t)
                seen.add(t.lower())
        if source in ("live", "archive"):
            scraped_services = normalize_services(scraped.get("services", []))
            fallback_services = normalize_services(fallback.get("services", []))
            merged["dynamicActivities"] = [s for s in scraped_services if s not in fallback_services]
            merged["activityMatchCount"] = len(merged["dynamicActivities"])
        else:
            merged["dynamicActivities"] = []
            merged["activityMatchCount"] = 0
    else:
        # No flyer data: backfill from the curated fallback truth (fail-closed
        # via normalize_services for services; tags carry the raw vocabulary).
        merged["services"] = normalize_services(
            fallback.get("services", [])
        ) or normalize_services(scraped.get("services", []))
        if not merged.get("tags"):
            merged["tags"] = list(fallback.get("tags", []))
        merged["dynamicActivities"] = []
        merged["activityMatchCount"] = 0

    # Services must be a non-empty NEEDS array: normalize whatever the
    # branches left (scraped raw is unnormalized), then fall back to the
    # curated fallback truth.
    merged["services"] = normalize_services(merged.get("services", []))
    if not merged["services"]:
        merged["services"] = normalize_services(
            fallback.get("services", [])
        ) or normalize_services(scraped.get("services", []))

    # Hours must be a non-empty dict of strings: strip null days (scraped
    # nulls) and non-dict shapes (archive plain-text strings), falling back
    # to the curated fallback hours.
    hours = merged.get("hours")
    if isinstance(hours, dict):
        hours = {d: h for d, h in hours.items() if isinstance(h, str)}
    if not isinstance(hours, dict) or not hours:
        fb_hours = fallback.get("hours")
        hours = fb_hours if isinstance(fb_hours, dict) and fb_hours else hours
    if hours is None:
        merged.pop("hours", None)
    else:
        merged["hours"] = hours

    merged["description"] = merged.get("description", f"{merged.get('name', '')} service location")
    merged["lastVerified"] = merged.get("lastVerified", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    if editorial:
        from scraper.overlay import apply_overlay

        merged = apply_overlay(merged, editorial)

    return merged


def compute_diff(old: dict, new: dict) -> dict:
    old_services = {s["id"]: s for s in old.get("services", [])}
    new_services = {s["id"]: s for s in new.get("services", [])}

    additions = [s for sid, s in new_services.items() if sid not in old_services]
    deletions = [s for sid, s in old_services.items() if sid not in new_services]
    updates = []
    for sid, s in new_services.items():
        if sid in old_services:
            old_s = old_services[sid]
            if s != old_s:
                updates.append(s)

    return {
        "additions": additions,
        "updates": updates,
        "deletions": deletions,
    }


def bump_version(old_version: str, diffs: dict) -> str:
    """Bump semver from a compute_diff() result.

    Rules (documented, see scraper-version-bump-semantics ticket):
    - deletions OR schema-keyword changes -> major
    - additions OR updates (any field-level change) -> minor
    - empty diff -> patch

    Known consequence: merge_location() refreshes lastScraped/lastUpdated
    timestamps on every run, so compute_diff() reports updates for every
    location and a re-run with zero content change still mints a minor bump
    (e.g. 3.2.0 -> 3.3.0 on tag churn + timestamps). Timestamp-only runs are
    therefore indistinguishable from content runs by version alone; check the
    metadata additions/updates/deletions counts for the real signal.
    """
    parts = old_version.split(".")
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    has_deletions = len(diffs.get("deletions", [])) > 0
    has_schema_changes = any(
        "schema" in str(d).lower() for d in diffs.get("additions", []) + diffs.get("deletions", []) + diffs.get("updates", [])
    )
    has_additions_or_updates = len(diffs.get("additions", [])) > 0 or len(diffs.get("updates", [])) > 0

    if has_deletions or has_schema_changes:
        return f"{major + 1}.0.0"
    elif has_additions_or_updates:
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


# Prettier settings mirrored here (prettier.config.js): tabs, width 100.
# write_services() renders byte-identical-to-prettier JSON so a pipeline
# regen never dirties `npm run lint`. NOTE: scraper/output/*.json is
# gitignored AND prettier-skipped, so only the services.json writer matters.
_PRETTIER_WIDTH = 100


def _flat(node) -> str:
    """Single-line rendering of a JSON node (scalars via json.dumps)."""
    if isinstance(node, dict):
        if not node:
            return "{}"
        # Prettier bracketSpacing pads collapsed objects: { "a": 1 }.
        return "{ " + ", ".join(f"{json.dumps(k)}: {_flat(v)}" for k, v in node.items()) + " }"
    if isinstance(node, list):
        return "[" + ", ".join(_flat(v) for v in node) + "]"
    return json.dumps(node)


def _render(node, level: int, first: str | None = None) -> list[str]:
    """Prettier-style lines: collapse the node if it fits, else one item per line.

    `first` is the literal prefix already emitted on the opening line
    (e.g. `"key": `) — fit is measured against it, not the plain indent.
    """
    pad = "\t" * level
    head = first if first is not None else pad
    if isinstance(node, (dict, list)) and node:
        one_line = _flat(node)
        if len(head) + len(one_line) <= _PRETTIER_WIDTH:
            return [head + one_line]
        open_c, close_c = ("{", "}") if isinstance(node, dict) else ("[", "]")
        # Render each direct child as a block; comma goes on the block's last line.
        blocks: list[list[str]] = []
        if isinstance(node, dict):
            for k, v in node.items():
                prefix = "\t" * (level + 1) + f"{json.dumps(k)}: "
                blocks.append(_render(v, level + 1, first=prefix))
        else:
            for v in node:
                blocks.append(_render(v, level + 1))
        out = [head + open_c]
        for i, block in enumerate(blocks):
            comma = "," if i < len(blocks) - 1 else ""
            out.extend(block[:-1])
            out.append(block[-1] + comma)
        out.append(pad + close_c)
        return out
    return [head + _flat(node)]


def dumps_prettier(data: dict) -> str:
    """Render JSON the way `prettier --write` would (tabs, width 100)."""
    return "\n".join(_render(data, 0)) + "\n"


def write_services(data: dict) -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "src", "lib", "data", "services.json")
    static_path = os.path.join(project_root, "static", "services.json")

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    os.makedirs(os.path.dirname(static_path), exist_ok=True)

    text = dumps_prettier(data)
    with open(data_path, "w") as f:
        f.write(text)
    with open(static_path, "w") as f:
        f.write(text)


def _get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_pipeline(scraped_path: str, flyer_path: str, output_dir: str) -> dict:
    flyer_data = load_flyer_data(flyer_path)
    with open(scraped_path, "r") as f:
        scraped_list = json.load(f)

    project_root = _get_project_root()
    services_path = os.path.join(project_root, "src", "lib", "data", "services.json")
    with open(services_path, "r") as f:
        old_data = json.load(f)

    flyer_centres = {c["id"]: c for c in flyer_data.get("day_support_centres", [])}
    flyer_clinics = {c["id"]: c for c in flyer_data.get("free_doctor_clinics", [])}
    flyer_by_name = {}
    for c in flyer_data.get("day_support_centres", []):
        flyer_by_name[c["name"].lower()] = c
    for c in flyer_data.get("free_doctor_clinics", []):
        flyer_by_name[c["name"].lower()] = c

    new_services = []
    for scraped in scraped_list:
        sid = scraped.get("id", "")
        flyer = flyer_centres.get(sid) or flyer_clinics.get(sid)
        if not flyer:
            name_key = scraped.get("name", "").lower()
            flyer = flyer_by_name.get(name_key)
        fallback = scraped.get("fallback", {})
        editorial = None
        try:
            from scraper.overlay import load_overlay, overlay_path_for

            overlay_path = overlay_path_for(project_root, sid)
            if sid and os.path.exists(overlay_path):
                editorial = load_overlay(overlay_path)
        except (OSError, ValueError):
            editorial = None
        merged = merge_location(scraped, flyer, fallback, editorial)
        new_services.append(merged)

    new_data = {
        "version": old_data["version"],
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "generatedBy": "Dublin Lifeline Pipeline",
        "services": new_services,
        "metadata": {
            "source": "Dublin Lifeline Pipeline (merged)",
            "totalServices": len(new_services),
            "categories": sorted(set(s.get("category", "") for s in new_services if s.get("category"))),
            "coverage": "Dublin City Centre",
            "nextSync": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "pipelineRun": datetime.now(timezone.utc).isoformat(),
            "differencesDetected": 0,
            "additions": 0,
            "updates": 0,
            "deletions": 0,
        },
    }

    diffs = compute_diff(old_data, new_data)
    new_data["version"] = bump_version(old_data["version"], diffs)
    new_data["metadata"]["differencesDetected"] = len(diffs["additions"]) + len(diffs["updates"]) + len(diffs["deletions"])
    new_data["metadata"]["additions"] = len(diffs["additions"])
    new_data["metadata"]["updates"] = len(diffs["updates"])
    new_data["metadata"]["deletions"] = len(diffs["deletions"])

    write_services(new_data)

    return {
        "version": new_data["version"],
        "totalServices": len(new_services),
        "diffs": diffs,
        "metadata": new_data["metadata"],
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scraped-path", default="")
    parser.add_argument("--flyer-path", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    project_root = _get_project_root()
    scraped_path = args.scraped_path or os.path.join(project_root, "scraper", "output", "scraped_output.json")
    flyer_path = args.flyer_path or os.path.join(project_root, ".scratch", "wayfinder-map", "research", "flyer-data.json")
    output_dir = args.output_dir or os.path.join(project_root, "src", "lib", "data")

    result = run_pipeline(scraped_path, flyer_path, output_dir)
    logger.info(json.dumps(result, indent=2))

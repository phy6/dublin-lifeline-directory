"""Editorial overlay (02): per-org Markdown+YAML frontmatter, field-level precedence.

File shape (<id>.md):
    ---
    id: <org-id>
    pinned: [phone, ...]      # factual fields editorial pins (opt-in)
    description: ...          # allow-listed overrides as frontmatter keys
    category: ...
    ---
    Body text -> notes (and description fallback if no frontmatter description).

Precedence:
- EDITORIAL_ALLOW_LIST fields: editorial wins when present/non-empty.
- FACTUAL_PINNABLE fields: scrape wins unless listed in `pinned`.
- Unknown keys are ignored (fail-closed).
"""

import re

EDITORIAL_ALLOW_LIST = frozenset({"description", "notes", "category", "services", "tags"})

FACTUAL_PINNABLE = frozenset({"phone", "email", "website", "address", "hours", "latitude", "longitude"})

_OVERLAY_DIRNAME = "overlays"


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text.strip()
    raw, body = m.group(1), m.group(2).strip()
    fm: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "pinned":
            v = v.strip("[]")
            fm["pinned"] = [p.strip() for p in v.split(",") if p.strip()] if v else []
        else:
            fm[k] = v.strip("\"'")
    return fm, body


def parse_overlay(text: str) -> dict:
    fm, body = _parse_frontmatter(text)
    org_id = fm.get("id", "")
    pinned = [p for p in fm.get("pinned", []) if p in FACTUAL_PINNABLE]
    overrides = {k: v for k, v in fm.items() if k not in ("id", "pinned") and (k in EDITORIAL_ALLOW_LIST or k in FACTUAL_PINNABLE)}
    if body and "description" not in overrides and "notes" not in overrides:
        overrides["notes"] = body
    elif body and "notes" not in overrides and "description" in overrides:
        overrides["notes"] = body
    return {"id": org_id, "pinned": pinned, "overrides": overrides, "notes": body}


def load_overlay(path: str) -> dict:
    with open(path) as f:
        return parse_overlay(f.read())


def apply_overlay(merged: dict, editorial: dict | None) -> dict:
    out = dict(merged)
    if not editorial:
        return out
    pinned = set(editorial.get("pinned", []))
    overrides = editorial.get("overrides", {})
    for field, value in overrides.items():
        if value is None or value == "":
            continue
        if field in EDITORIAL_ALLOW_LIST:
            out[field] = value
        elif field in FACTUAL_PINNABLE and field in pinned:
            out[field] = value
        # else: ignored (scrape-wins / unknown)
    notes = editorial.get("notes")
    if notes and "notes" in EDITORIAL_ALLOW_LIST and not out.get("notes"):
        out["notes"] = notes
    return out


def overlay_path_for(project_root: str, org_id: str) -> str:
    import os

    return os.path.join(project_root, "scraper", "content", "orgs", f"{org_id}.md")

import re
import json
from typing import List, Dict, Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://.+")
TIME_RE = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}(?:,\s*\d{2}:\d{2}-\d{2}:\d{2})*$")


def validate_location(loc: dict) -> dict:
    errors: List[str] = []
    warnings: List[str] = []

    if not loc.get("id") or not isinstance(loc["id"], str):
        errors.append(f"{loc.get('id', 'unknown')}: missing or invalid id")
    if not loc.get("name") or not isinstance(loc["name"], str):
        errors.append(f"{loc.get('id', 'unknown')}: missing or invalid name")
    if not loc.get("address") or not isinstance(loc["address"], str):
        errors.append(f"{loc.get('id', 'unknown')}: missing or invalid address")

    lat = loc.get("latitude")
    if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
        errors.append(f"{loc.get('id', 'unknown')}: invalid latitude {lat}")

    lon = loc.get("longitude")
    if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
        errors.append(f"{loc.get('id', 'unknown')}: invalid longitude {lon}")

    if not loc.get("category") or not isinstance(loc["category"], str):
        errors.append(f"{loc.get('id', 'unknown')}: missing or invalid category")

    services = loc.get("services", [])
    if not isinstance(services, list) or len(services) == 0:
        errors.append(f"{loc.get('id', 'unknown')}: services must be a non-empty array")
    else:
        from scraper.pipeline import NEEDS

        for svc in services:
            if not isinstance(svc, str) or not re.match(r"^[a-z-]+$", svc):
                errors.append(f"{loc.get('id', 'unknown')}: invalid service slug '{svc}'")
            elif svc not in NEEDS:
                errors.append(f"{loc.get('id', 'unknown')}: unknown need '{svc}' (not in curated taxonomy)")
        if len(services) != len(set(services)):
            errors.append(f"{loc.get('id', 'unknown')}: duplicate services found")

    phone = loc.get("phone")
    if phone is not None and (not isinstance(phone, str) or phone == ""):
        warnings.append(f"{loc.get('id', 'unknown')}: phone is not a non-empty string")

    hours = loc.get("hours")
    if hours is not None:
        if not isinstance(hours, dict) or len(hours) == 0:
            errors.append(f"{loc.get('id', 'unknown')}: hours must be a non-empty object")
        else:
            valid, msg = _validate_hours(hours)
            if not valid:
                errors.append(f"{loc.get('id', 'unknown')}: {msg}")

    email = loc.get("email")
    if email is not None and (not isinstance(email, str) or not EMAIL_RE.match(email)):
        warnings.append(f"{loc.get('id', 'unknown')}: invalid email format '{email}'")

    website = loc.get("website")
    if website is not None and (not isinstance(website, str) or not URL_RE.match(website)):
        warnings.append(f"{loc.get('id', 'unknown')}: invalid website format '{website}'")

    return {"errors": errors, "warnings": warnings}


def _validate_hours(hours: dict) -> tuple[bool, str]:
    for day, time_range in hours.items():
        if day == "default":
            continue
        if not isinstance(time_range, str):
            return False, f"hours.{day} must be a string"
        if not TIME_RE.match(time_range):
            return False, f"hours.{day} has invalid format '{time_range}'"
        parts = time_range.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                start_h, start_m = map(int, start.split(":"))
                end_h, end_m = map(int, end.split(":"))
                if end_h < start_h or (end_h == start_h and end_m <= start_m):
                    return False, f"hours.{day}: end time {end} is not after start time {start}"
    if all(h == "closed" for h in hours.values()):
        return False, "at least some days must have hours"
    return True, ""


def validate_clinic(loc: dict, all_ids: List[str]) -> List[str]:
    errors = []
    location_id = loc.get("location_id")
    if location_id and location_id not in all_ids and location_id != "mhu":
        errors.append(f"{loc.get('id', 'unknown')}: location_id '{location_id}' not in existing locations")
    return errors


def validate_services(services_data: dict) -> dict:
    results = {"valid": True, "locations": []}
    all_ids = [loc["id"] for loc in services_data.get("services", []) if loc.get("id")]

    for loc in services_data.get("services", []):
        result = validate_location(loc)
        entry = {"id": loc.get("id", "unknown"), **result}
        results["locations"].append(entry)
        if result["errors"]:
            results["valid"] = False

        clinic_errors = validate_clinic(loc, all_ids)
        if clinic_errors:
            results["locations"].append({"id": loc.get("id", "unknown"), "errors": clinic_errors})
            results["valid"] = False

    return results


def run_validation(services_path: str) -> dict:
    with open(services_path, "r") as f:
        data = json.load(f)
    return validate_services(data)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "src/lib/data/services.json"
    result = run_validation(path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
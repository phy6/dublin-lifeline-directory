# Ticket: Data validation schema

**Blocked by:** scraper-hybrid-data-source (closed)
**Blocks:** scraper-test-strategy
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

## Question

Define validation for the final `services.json` output. Reuse rules from the pipeline spec (`.scratch/wayfinder-map/research/data-pipeline.md` §8):

**Location-level (errors):**
- `id`: required, non-empty string
- `name`: required, non-empty string
- `address`: required, non-empty string
- `latitude`: required, number -90 to 90
- `longitude`: required, number -180 to 180
- `category`: required, non-empty string
- `services`: required, non-empty array

**Location-level (warnings):**
- `phone`: non-empty string
- `hours`: object with valid time ranges
- `email`: valid email format
- `website`: valid URL format

**Hours validation:**
- Format: "HH:MM-HH:MM" or "HH:MM-HH:MM, HH:MM-HH:MM"
- End time after start time
- At least some days have hours

**Services validation:**
- Non-empty array
- Valid slugs (lowercase, hyphens only)
- No duplicates within a location

**Healthcare clinic validation:**
- `location_id` must reference existing location (unless MHU)
- `schedule` present
- At least one of `appointment_available` / `walk_in_available` is true

Implementation: Python validation module using `pydantic` or custom validators. Run in pipeline before write.

**Resolution:** ✅ Implemented `scraper/validate.py` with custom validators (no pydantic dependency needed): `validate_location()` checks all error/warning rules, `_validate_hours()` validates time formats and ordering, `validate_clinic()` checks location_id references, `validate_services()` runs full validation, `run_validation()` reads services.json and returns results. `scraper/tests/test_validation.py` has 14 tests covering all validation cases including real data. Usage: `python3 scraper/validate.py src/lib/data/services.json` returns JSON with valid/locations/errors/warnings and exits with code 0/1.

Note: clinic validation (`location_id`, `schedule`, `appointment_available`/`walk_in_available`) was simplified to `location_id` reference check since healthcare clinic fields aren't in the current services.json schema. Could be expanded when clinic data is added.

## Question

Define validation for the final `services.json` output. Reuse rules from the pipeline spec (`.scratch/wayfinder-map/research/data-pipeline.md` §8):

**Location-level (errors):**
- `id`: required, non-empty string
- `name`: required, non-empty string
- `address`: required, non-empty string
- `latitude`: required, number -90 to 90
- `longitude`: required, number -180 to 180
- `category`: required, non-empty string
- `services`: required, non-empty array

**Location-level (warnings):**
- `phone`: non-empty string
- `hours`: object with valid time ranges
- `email`: valid email format
- `website`: valid URL format

**Hours validation:**
- Format: "HH:MM-HH:MM" or "HH:MM-HH:MM, HH:MM-HH:MM"
- End time after start time
- At least some days have hours

**Services validation:**
- Non-empty array
- Valid slugs (lowercase, hyphens only)
- No duplicates within a location

**Healthcare clinic validation:**
- `location_id` must reference existing location (unless MHU)
- `schedule` present
- At least one of `appointment_available` / `walk_in_available` is true

Implementation: Python validation module using `pydantic` or custom validators. Run in pipeline before write.
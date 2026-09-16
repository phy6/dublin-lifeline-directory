# Ticket: Data validation schema

**Blocked by:** scraper-hybrid-data-source, scraper-output-locations
**Blocks:** scraper-test-strategy

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
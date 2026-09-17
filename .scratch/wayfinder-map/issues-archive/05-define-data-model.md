# 05: Define data model schema

**Label:** `wayfinder:task`
**Assigned to:** phy6 (claimed)
**Blocked by:** 01-research-flyer-data (closed), 02-pwa-offline-strategy (closed), 03-pwa-framework (closed)
**Status:** closed

**Question:** What is the data model for the service directory? Define schemas for locations, services, schedules, and healthcare clinics based on the flyer data and the chosen framework's storage capabilities.

**Acceptance criteria:**

- Location schema (name, address, coordinates, services offered, contact info)
- Service schema (name, category, description)
- Schedule schema (day → hours per location, walk-in vs appointment)
- Healthcare clinic schema (location, day, hours, appointment details)
- Data migration path from flyer JSON to app database
- Output: defined data model schemas and database migration plan

**Resolution:** Complete data model schemas for all four entity types. Coordinates and phone numbers for all 5 locations filled in from web research (`research/data-gap-fill.md`). GP clinic schedules obtained for 3 of 5 locations (Inclusion Health Hub: Mon-Fri 9:30am-12pm appt, 1:30pm-4pm walk-in; Capuchin: Tue/Thu 9-11:30am, 1:30-3pm walk-in; MQI: Mon/Wed/Fri mornings+afternoons). MHU schedule obtained (Tues/Wed/Thu 7pm-10pm at Mendicity and Lighthouse). Full migration path defined. See `research/data-model-schema.md` and `research/data-gap-fill.md`.

**Resolution date:** 2026-09-14

**Status:** closed

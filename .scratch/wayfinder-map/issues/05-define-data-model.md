# 05: Define data model schema

**Label:** `wayfinder:task`
**Type:** Task (AFK)
**Blocked by:** 01-research-flyer-data, 02-research-offline-architecture, 03-research-framework

**Question:** What is the data model for the service directory? Define schemas for locations, services, schedules, and healthcare clinics based on the flyer data and the chosen framework's storage capabilities.

**Acceptance criteria:**
- Location schema (name, address, coordinates, services offered, contact info)
- Service schema (name, category, description)
- Schedule schema (day → hours per location, walk-in vs appointment)
- Healthcare clinic schema (location, day, hours, appointment details)
- Data migration path from flyer JSON to app database
- Output: defined data model schemas and database migration plan

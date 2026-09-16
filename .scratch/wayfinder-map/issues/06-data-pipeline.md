# 06: Set up data pipeline (scraper + storage)

**Assigned to:** phy6 (claimed)
**Blocked by:** None
**Status:** closed
**Resolution date:** 2026-09-14

**Resolution:** ✅ Data pipeline specification complete. Gap-fill research (`research/data-gap-fill.md`) resolved all 4 critical blockers:

1. **Coordinates** filled for all 5 locations (approximate, needs verification)
2. **Phone numbers** filled for all 5 locations
3. **GP clinic schedules** obtained for 3 of 5 (Inclusion Health Hub: Mon-Fri 9:30am-12pm appt, 1:30pm-4pm walk-in; Capuchin: Tue/Thu 9-11:30am, 1:30-3pm walk-in; MQI: Mon/Wed/Fri mornings + afternoons)
4. **MHU schedule** obtained (Tues/Wed/Thu 7pm-10pm at Mendicity and Lighthouse)

Full pipeline specification at `research/data-pipeline.md`. Data model migration path at `research/data-model-schema.md`.

---

**Question:** Build the data pipeline: integrate the existing scraper with the defined data model, set up local storage, and establish the sync mechanism for updating flyer data.

**Research summary:**

- Complete data pipeline specification written to `.scratch/wayfinder-map/research/data-pipeline.md`
- Scraper code does NOT exist in the repo — it is external; pipeline reads `flyer-data.json` as input
- `flyer-data.json` contains 5 Day Support Centres + 5 Free Doctor Clinics from www.primarycaresafetynet.ie (extracted 2026-09-14)
- Existing `services.json` (14 services, v3.1.0) provides the full `ServiceLocation` schema in `src/lib/types.ts`
- Pipeline flow: flyer-data.json → validate → transform (schema mapping, service slug normalization) → enrich (geocode addresses, add contact info) → merge with existing services.json → output
- Local storage: IndexedDB (`dcs-directory` store `services`) + Cache API (`StaleWhileRevalidate` for `services.json`) + localStorage (user preferences)
- Sync mechanism: version-based comparison via `StaleWhileRevalidate`, `metadata.nextSync` field, service worker broadcasts `DATA_UPDATE` messages
- Data validation rules defined for locations, hours, services, and healthcare clinics
- **CRITICAL GAP:** Flyer data is missing phone, email, website, and coordinates for ALL 10 locations

**HITL — Human decisions required BEFORE implementation:**

| #   | Decision                                                                                                    | Impact                                   |
| --- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 1   | **Provide coordinates** (lat/long) for all 5 Day Support Centres and 5 GP Clinic locations                  | HIGH — map functionality depends on this |
| 2   | **Provide phone numbers** for all 10 locations                                                              | HIGH — contact info missing              |
| 3   | **Confirm GP clinic operating hours** (exact times, flyer only says "Mon-Fri with appointment and walk-in") | HIGH — users need clinic hours           |
| 4   | **Confirm MHU schedule** (days and locations visited)                                                       | MEDIUM — MHU is unique service           |
| 5   | **Provide email addresses and websites** for all 10 locations                                               | MEDIUM — contact info missing            |
| 6   | **Verify 5th Day Support Centre identity** (Inclusion Health Hub lacks Day Support Centre details)          | MEDIUM — may be duplicate or separate    |
| 7   | **Choose enrichment method** for contact info (web scraping? manual? API?)                                  | MEDIUM — affects pipeline complexity     |
| 8   | **Confirm doctor clinic `location_id` mapping** to parent Day Support Centres                               | MEDIUM — affects data model integrity    |
| 9   | **Decide sync cadence** (weekly? monthly?)                                                                  | LOW — affects data freshness             |
| 10  | **Define category taxonomy** final list                                                                     | MEDIUM — affects filtering/search        |

**Acceptance criteria:**

- Scraper connected to data model, produces valid JSON output
- Local storage populated with flyer dataset
- Sync mechanism for updates (from flyer/scraper to local cache)
- Data validation (all locations, hours, services verified)
- Output: working data pipeline that produces a populated local database

**⚠️ CANNOT FULLY CLOSE — Human input items 1-4 must be resolved before pipeline can produce complete `services.json`**

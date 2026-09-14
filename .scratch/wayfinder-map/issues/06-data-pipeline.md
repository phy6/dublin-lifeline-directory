# 06: Set up data pipeline (scraper + storage)

**Label:** `wayfinder:task`
**Type:** Task (HITL)
**Blocked by:** 05-define-data-model

**Question:** Build the data pipeline: integrate the existing scraper with the defined data model, set up local storage, and establish the sync mechanism for updating flyer data.

**Acceptance criteria:**

- Scraper connected to data model, produces valid JSON output
- Local storage populated with flyer dataset
- Sync mechanism for updates (from flyer/scraper to local cache)
- Data validation (all locations, hours, services verified)
- Output: working data pipeline that produces a populated local database

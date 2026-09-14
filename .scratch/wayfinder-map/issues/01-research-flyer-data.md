# 01: Research flyer data structure

**Label:** `wayfinder:research`
**Type:** Research (AFK)
**Blocked by:** None (can start immediately)

**Question:** What does the flyer data look like in detail? Extract the full dataset from the flyer — all locations, services, hours, contact info, and healthcare clinic schedules. What fields are present? What's missing?

**Acceptance criteria:**
- All 5 Day Support Centres documented with full details (name, address, hours, services, contact)
- All 5 Free Doctor Clinics documented with schedules (day, time, walk-in vs appointment)
- Mobile Health Unit schedule documented
- Gap analysis: what fields are present vs missing
- Output: a structured JSON/CSV dataset representing the flyer data

---

**Resolution:** ✅ Complete. Full dataset extracted to `research/flyer-data.json`. All 5 Day Support Centres + 5 GP clinics + MHU documented with hours, services, addresses. Gap analysis at `research/gap-analysis.md`.

**Resolution date:** 2026-09-14

---

**Status:** closed

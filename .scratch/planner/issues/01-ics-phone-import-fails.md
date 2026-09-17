# 01: Phone calendar still rejects planner .ics

**What to build:** Diagnose and fix the remaining phone-calendar import failure for planner `.ics` downloads (weekly + once). Strict RFC 5545 pass already shipped (`9505319`: UTC DTSTAMP, trailing CRLF, 75-octet folding, CALSCALE) — user reports mobile import still fails as of 2026-09-17.

**Blocked by:** Needs a real phone + calendar app to reproduce (reporter device). Hypotheses to test with device in hand: floating local DTSTART without VTIMEZONE/TZID (try `TZID=Europe/Dublin` or UTC `Z` times), missing `METHOD:PUBLISH`, `URL.revokeObjectURL` racing the download on mobile browsers, file MIME/handling (`text/calendar` vs download + manual open).

**Status:** needs-triage

- [ ] Reproduce on a real phone, capture exact failure (stall vs error text)
- [ ] Try TZ-aware DTSTART fix, verify on device
- [ ] Re-run unit suite + device retest before closing

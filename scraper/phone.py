"""Deep phone module: every Irish phone-number concern behind one seam.

The extractor (scraper.py), the merge sanitiser (pipeline.py), and the
quarantine gate all cross this interface, so the pattern, the label-strip,
and the "looks dialable" judgement live here — not in callers.
"""

import re
from typing import Optional

from bs4 import BeautifulSoup

# Dublin landlines (01…), Irish mobiles (08x…), freephone/low-call
# (1800/1850/1890…). Separators seen in the wild: spaces, dashes, (01).
PHONE_RE = re.compile(
    r"(?:\+353[\s\-]?)?(?:\(0?1\)|01)[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
    r"|08\d[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
    r"|1(?:800|850|890)[\s\-]?\d{2,3}[\s\-]?\d{2,4}"
)

_LABEL_PREFIX_RE = re.compile(
    r"^(freephone|freecall|tel|telephone|phone|fax|lo-?call)\s*:\s*",
    flags=re.IGNORECASE,
)


def extract_phone(soup: BeautifulSoup) -> Optional[str]:
    """Regex fallback: scan page text for an Irish phone pattern.

    For sites that render the number as plain text with no tel: link or
    phone class (e.g. crosscare.ie).
    """
    page_text = soup.get_text(" ", strip=True)
    m = PHONE_RE.search(page_text)
    if m:
        return m.group(0).strip()
    return None


def sanitize_phone(raw: str) -> str:
    """Strip label prefixes ("Freephone:", "Tel:") and collapse whitespace."""
    cleaned = _LABEL_PREFIX_RE.sub("", raw)
    return re.sub(r"\s+", " ", cleaned).strip()


def looks_like_phone(value: object) -> bool:
    """Shared gate: does this value contain a dialable Irish number?"""
    return isinstance(value, str) and PHONE_RE.search(value) is not None

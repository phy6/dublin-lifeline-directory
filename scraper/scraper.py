import asyncio
import json
import logging
import os
import random
import re
import time
from typing import Optional, Tuple, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from scraper.pipeline import _lookup_slug
from scraper.phone import extract_phone, looks_like_phone
from scraper.validate import URL_RE, EMAIL_RE

logger = logging.getLogger(__name__)


def extract_services(soup: BeautifulSoup) -> List[str]:
    result: List[str] = []
    for script in soup.find_all("script"):
        if script.string and "var servicesData" in script.string:
            s = script.string
            start = s.find("[")
            end = s.rfind("]") + 1
            if start != -1 and end != 0:
                try:
                    return json.loads(s[start:end])
                except (json.JSONDecodeError, ValueError):
                    pass
    desc_div = soup.select_one(".services-description")
    if desc_div and desc_div.string:
        text = desc_div.string
        match = re.search(r"Services:\s*(.+)", text)
        if match:
            return [s.strip() for s in match.group(1).split(",")]
    for h3 in soup.find_all("h3"):
        text = h3.get_text(strip=True)
        if not text:
            continue
        slug = _lookup_slug(text)
        if slug and slug not in result:
            result.append(slug)
    return result


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f)


def extract_field(soup: BeautifulSoup, selectors: List[str], field: str = "") -> Optional[str]:
    for selector in selectors:
        element = soup.select_one(selector)
        if element is not None:
            # For link-backed fields the value lives in href, not text
            # (e.g. <a href="/">HOME</a> must not extract as "HOME").
            if field in ("website", "email") and element.name in ("a", "link"):
                href = (element.get("href") or "").strip()
                if href and href != "#":
                    if field == "email":
                        href = href.removeprefix("mailto:").split("?")[0]
                    if href:
                        return href
                # href missing/unusable: skip to next selector, don't fall
                # back to link text (that's nav chrome).
                continue
            if field == "website" and element.name == "meta":
                content = (element.get("content") or "").strip()
                if content:
                    return content
            text = element.get_text(strip=True)
            if text:
                return text
    # Phone regex fallback: some sites render the number as plain text
    # with no tel: link or phone class. The shared phone module owns the
    # pattern (landlines, mobiles, freephone).
    if field == "phone":
        return extract_phone(soup)
    return None


def parse_hours(raw: str) -> dict:
    """Parse a raw hours string into canonical {day-range: time-range} dict."""
    import re
    text = raw.strip()
    m = re.match(r"^([A-Za-z]+-[A-Za-z]+)\s+(\d{2}:\d{2}-\d{2}:\d{2})$", text)
    if not m:
        return {"default": text}
    return {m.group(1).lower(): m.group(2)}


async def fetch_url(client: httpx.AsyncClient, url: str, timeout: float = 5.0) -> str:
    response = await client.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.text


async def _retry_fetch(
    client: httpx.AsyncClient, url: str, timeout: float = 5.0,
    max_attempts: int = 3, base_delay: float = 2.0
) -> str:
    for attempt in range(max_attempts):
        try:
            return await fetch_url(client, url, timeout=timeout)
        except (httpx.RequestError, httpx.HTTPStatusError):
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                raise
    raise RuntimeError(f"Failed to fetch {url} after {max_attempts} attempts")


class _RateLimiter:
    def __init__(self, interval: float = 6.0, jitter: float = 0.5):
        self.interval = interval
        self.jitter = jitter
        self._last = time.monotonic()

    async def wait(self):
        now = time.monotonic()
        elapsed = now - self._last
        sleep_time = max(0, self.interval - elapsed) + random.uniform(-self.jitter, self.jitter)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        self._last = time.monotonic()


async def fetch_with_fallback(target: dict, docs_dir: str, client: Optional[httpx.AsyncClient] = None) -> Tuple[Optional[str], str]:
    url = target["url"]
    target_id = target["id"]
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(follow_redirects=True)
    try:
        html = await _retry_fetch(client, url)
        return html, "live"
    except Exception as exc:
        # SSL-only fallback: some small-org sites (e.g. aldp.ie) serve a
        # cert chain Python can't verify. Retry once without verification
        # rather than dropping straight to archive/fallback. Other errors
        # (DNS, refused, timeout) go directly to archive.
        if "ssl" not in str(exc).lower() and "certificate" not in str(exc).lower():
            pass
        else:
            try:
                async with httpx.AsyncClient(follow_redirects=True, verify=False) as insecure_client:
                    html = await _retry_fetch(insecure_client, url)
                    logger.warning("Fetched %s with unverified TLS", url)
                    return html, "live"
            except Exception:
                pass
    finally:
        if own_client:
            await client.aclose()
    archive_paths = [
        os.path.join(docs_dir, f"{target_id}.html"),
        os.path.join(docs_dir, f"dublin_lifeline_{target_id}.html"),
    ]
    for path in archive_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read(), "archive"
    return None, "none"


def _get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _norm_host(netloc: str) -> str:
    """Normalize a URL host for comparison: lowercase, strip www."""
    host = (netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _same_host(url_a: str, url_b: str) -> bool:
    return _norm_host(urlparse(url_a).netloc) == _norm_host(urlparse(url_b).netloc)


def _section_heading(el):
    """Nearest h2/h3 owning the element's section.

    Walks up through ancestors, scanning each level's preceding siblings,
    so the heading found is the one heading the element's own section rather
    than whatever heading happens to be nearest in document order (which may
    be unrelated site chrome). Falls back to document-order search.
    """
    node = el
    for _ in range(5):
        parent = getattr(node, "parent", None)
        if parent is None:
            break
        for sib in node.previous_siblings:
            if getattr(sib, "name", None) in ("h2", "h3"):
                text = sib.get_text(strip=True)
                if text:
                    return text
        node = parent
    heading = el.find_previous(["h2", "h3"])
    if heading is not None:
        return heading.get_text(strip=True)
    return ""


def quarantine_junk(result: dict) -> List[str]:
    """Strip chrome-text fields that fail validator format rules.

    Uses the same URL/email patterns as scraper/validate.py, so the gate and
    the validator share one definition of "good data". Offending fields are
    set to None (merge_location drops them) and the reasons returned.
    """
    reasons = []
    website = result.get("website")
    if website is not None and (not isinstance(website, str) or not URL_RE.match(website)):
        reasons.append(f"website not URL-like: {website!r}")
        result["website"] = None
    email = result.get("email")
    if email is not None and (not isinstance(email, str) or not EMAIL_RE.match(email)):
        reasons.append(f"email malformed: {email!r}")
        result["email"] = None
    phone = result.get("phone")
    if phone is not None and not looks_like_phone(phone):
        reasons.append(f"phone not dialable: {phone!r}")
        result["phone"] = None
    # Empty-record gate: a live fetch that yields no address, description,
    # phone, email, website, or services extracted nothing usable (even if
    # nothing was technically "junk"). Quarantine so merge falls back.
    # Empty-record gate (only if no format gate already fired — avoids
    # double-counting a record already quarantined for junk).
    if not reasons and not any(result.get(f) for f in ("address", "description", "phone", "email", "website")) and not result.get("services"):
        reasons.append("empty record: no usable fields extracted")
    return reasons


class DublinLifelineScraper:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.targets = self.config["targets"]
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(config_path))))
        self.docs_dir = os.path.join(project_root, "scraper", "docs")
        self.output_dir = os.path.join(project_root, "scraper", "output")
        self.rate_limiter = _RateLimiter(interval=6.0, jitter=0.5)

    async def fetch_target(self, target: dict) -> dict:
        await self.rate_limiter.wait()
        html, source = await fetch_with_fallback(target, self.docs_dir)
        result = {
            "id": target["id"],
            "name": target["name"],
            "source": source,
            "url": target["url"],
            # Always attached: merge_location() backfills category and
            # carries the confirmed register identity into the output.
            "fallback": target.get("fallback", {}),
        }
        for key in ("rcn", "registered_name"):
            if target.get(key):
                result[key] = target[key]
        if html:
            soup = BeautifulSoup(html, "lxml")
            for field, selectors in target["selectors"].items():
                result[field] = extract_field(soup, selectors, field)
            result["services"] = extract_services(soup)
            # Website defaults to the scraped URL itself (canonical identity).
            # Only a canonical/og:url override replaces it — never nav chrome.
            if not result.get("website"):
                result["website"] = target["url"]
            # Contact-page fallback: if the homepage yielded no contact
            # fields at all and the target declares a contactUrl, re-extract
            # only the missing fields from the contact page (rate-limited).
            if (
                target.get("contactUrl")
                and not any(result.get(f) for f in ("phone", "email", "address", "hours", "description"))
            ):
                await self.rate_limiter.wait()
                try:
                    async with httpx.AsyncClient(follow_redirects=True) as contact_client:
                        contact_html = await _retry_fetch(contact_client, target["contactUrl"])
                    contact_soup = BeautifulSoup(contact_html, "lxml")
                    for field, selectors in target["selectors"].items():
                        if not result.get(field) and field != "website":
                            val = extract_field(contact_soup, selectors, field)
                            if val:
                                result[field] = val
                    result["contactFallback"] = True
                except Exception:
                    pass
            if source == "live":
                reasons = quarantine_junk(result)
                if reasons:
                    logger.warning("Quarantining %s: %s", target["id"], "; ".join(reasons))
                    result["source"] = "quarantined"
                    result["quarantine_reasons"] = reasons
        # No HTML (source "none"): merged output falls back to
        # target["fallback"] in merge_location().
        return result

    async def run(self, targets: Optional[List[str]] = None) -> List[dict]:
        target_list = self.targets
        if targets is not None:
            target_list = [t for t in self.targets if t["id"] in targets]
        tasks = [self.fetch_target(t) for t in target_list]
        results = await asyncio.gather(*tasks)
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, "scraped_output.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        return results

    async def discover_providers(self) -> List[dict]:
        discovery = self.config.get("discovery")
        if not discovery or not discovery.get("urls"):
            logger.info("No discovery URLs configured")
            return []
        discovery_urls = discovery["urls"]
        discovery_selectors = discovery.get("selectors", {})
        default_name_selectors = discovery_selectors.get("name", ["h2 a", "h3 a"])
        interval = discovery.get("interval", 60000) / 1000.0
        max_results = discovery.get("maxResults", 50)
        discovered = []
        seen_urls = set()
        # URL entries may be plain strings (global selectors) or dicts
        # {url, name_selectors?, capture_category?} for site-specific extraction.
        normalized = []
        for entry in discovery_urls:
            if isinstance(entry, str):
                normalized.append({"url": entry})
            else:
                normalized.append(entry)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for idx, entry in enumerate(normalized):
                dir_url = entry["url"]
                name_selectors = entry.get("name_selectors", default_name_selectors)
                capture_category = entry.get("capture_category", False)
                try:
                    html = await _retry_fetch(client, dir_url)
                    soup = BeautifulSoup(html, "lxml")
                    for selector in name_selectors:
                        for el in soup.select(selector):
                            # el may itself be the link (e.g. "h2 a" returns <a>)
                            link = None
                            if el.name == "a" and el.get("href"):
                                link = el
                            elif el.get("href"):
                                link = el
                            else:
                                parent = el.find_parent("a")
                                if parent and parent.get("href"):
                                    link = parent
                                else:
                                    child = el.select_one("a[href]")
                                    if child:
                                        link = child
                            if link is None:
                                continue
                            name = el.get_text(strip=True)
                            if not name or len(name) < 3:
                                continue
                            url = link["href"].strip()
                            if url.startswith(("mailto:", "tel:", "#", "javascript:")):
                                continue
                            if not url.startswith("http"):
                                url = urljoin(dir_url, url)
                            norm = url.rstrip("/").lower()
                            if norm in seen_urls:
                                continue
                            # Skip links back to the directory itself.
                            if _same_host(url, dir_url):
                                continue
                            seen_urls.add(norm)
                            item = {"name": name, "url": url, "discovered_via": dir_url}
                            if capture_category:
                                cat = _section_heading(el)
                                if cat:
                                    item["category"] = cat
                            discovered.append(item)
                            if len(discovered) >= max_results:
                                break
                        if len(discovered) >= max_results:
                            break
                    if idx < len(normalized) - 1:
                        await asyncio.sleep(interval)
                except Exception as e:
                    logger.warning(f"Discovery failed for {dir_url}: {e}")
        logger.info(f"Discovery complete: {len(discovered)} providers found")
        return discovered[:max_results]
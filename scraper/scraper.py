import asyncio
import json
import logging
import os
import random
import re
import time
from typing import Optional, Tuple, List

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_services(soup: BeautifulSoup) -> List[str]:
    for script in soup.find_all("script"):
        if script.string and "var servicesData" in script.string:
            start = script.string.find("[")
            end = script.string.rfind("]") + 1
            if start != -1 and end != 0:
                try:
                    return json.loads(script.string[start:end])
                except (json.JSONDecodeError, ValueError):
                    pass
    desc_div = soup.select_one(".services-description")
    if desc_div and desc_div.string:
        text = desc_div.string
        match = re.search(r"Services:\s*(.+)", text)
        if match:
            return [s.strip() for s in match.group(1).split(",")]
    return []


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f)


def extract_field(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    for selector in selectors:
        element = soup.select_one(selector)
        if element is not None:
            text = element.get_text(strip=True)
            if text:
                return text
    return None


async def fetch_url(client: httpx.AsyncClient, url: str, timeout: float = 5.0) -> str:
    response = await client.get(url, timeout=timeout)
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
        client = httpx.AsyncClient()
    try:
        html = await _retry_fetch(client, url)
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
        }
        if html:
            soup = BeautifulSoup(html, "lxml")
            for field, selectors in target["selectors"].items():
                result[field] = extract_field(soup, selectors)
            result["services"] = extract_services(soup)
        else:
            result["fallback"] = target.get("fallback", {})
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
import argparse
import asyncio
import json
import logging
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import DublinLifelineScraper, load_config
from scraper.pipeline import run_pipeline
from scraper.scraper import extract_services, fetch_with_fallback

logger = logging.getLogger(__name__)

FLYER_TARGET_IDS = [
    "mendicity-institute", "capuchin-day-centre", "lighthouse-cafe",
    "merchants-quay-ireland", "inclusion-health-hub",
    "inclusion-health-hub-gp", "capuchin-day-centre-gp",
    "merchants-quay-ireland-gp", "mendicity-institute-gp", "mobile-health-unit",
]

FLYER_ID_MAP = {
    "mendicity-institute": "mendicity-institution",
    "capuchin-day-centre": "capuchin-day-centre",
    "merchants-quay-ireland": "merchants-quay-ireland",
}


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Dublin Lifeline Scraper CLI")
    parser.add_argument("--targets", help="Comma-separated list of target IDs to scrape")
    parser.add_argument("--flyer-only", action="store_true", help="Only the 10 flyer targets")
    parser.add_argument("--dry-run", action="store_true", help="Show targets without fetching")
    parser.add_argument("--no-fallback", action="store_true", help="Fail if live fetch fails")
    parser.add_argument("--verbose", action="store_true", help="Detailed logging")
    parser.add_argument("--config", default=None, help="Custom config path")
    parser.add_argument("--output", default=None, help="Custom output path")
    parser.add_argument("--discover", action="store_true", help="Discover and scrape all providers")
    return parser.parse_args(args)


def get_targets(config, args):
    if args.flyer_only:
        flyer_ids = {FLYER_ID_MAP.get(tid, tid) for tid in FLYER_TARGET_IDS}
        return [t for t in config["targets"] if t["id"] in flyer_ids]
    if args.targets:
        target_ids = args.targets.split(",")
        return [t for t in config["targets"] if t["id"] in target_ids]
    return config["targets"]


async def run_scraper(scraper, targets, no_fallback):
    results = await scraper.run(targets=[t["id"] for t in targets])
    if no_fallback:
        for r in results:
            if r.get("source") in ("none", "archive"):
                raise RuntimeError(f"Fetch failed for {r['id']} with no fallback allowed (source={r.get('source')})")
    return results


async def run_discovery(scraper, no_fallback):
    from bs4 import BeautifulSoup
    discovered = await scraper.discover_providers()
    logger.info("Discovered %d providers", len(discovered))
    results = []
    for prov in discovered:
        slug = re.sub(r"[^a-z0-9]+", "-", prov["name"].lower()).strip("-") or "discovered"
        target = {"id": slug, "name": prov["name"], "url": prov["url"], "selectors": {}, "fallback": {}}
        html, source = await fetch_with_fallback(target, scraper.docs_dir)
        if no_fallback and source in ("none", "archive"):
            raise RuntimeError(f"Fetch failed for {slug} with no fallback allowed (source={source})")
        result = {"id": slug, "name": prov["name"], "url": prov["url"], "source": source}
        if html:
            soup = BeautifulSoup(html, "lxml")
            for field in ("phone", "address", "description"):
                result[field] = None
            result["services"] = extract_services(soup)
        else:
            result["services"] = []
        results.append(result)
    return results


async def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config_path = args.config or os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "sources.json")
    config = load_config(config_path)

    if getattr(args, "discover", False):
        scraper = DublinLifelineScraper(config_path)
        try:
            results = await run_discovery(scraper, args.no_fallback)
            scraped_path = os.path.join(scraper.output_dir, "scraped_output.json")
            os.makedirs(os.path.dirname(scraped_path), exist_ok=True)
            with open(scraped_path, "w") as f:
                json.dump(results, f, indent=2)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(config_path))))
            flyer_path = os.path.join(project_root, ".scratch", "wayfinder-map", "research", "flyer-data.json")
            output_dir = args.output or os.path.join(project_root, "src", "lib", "data")
            pipeline_result = run_pipeline(scraped_path, flyer_path, output_dir)
            logger.info("Discovery complete. Version: %s", pipeline_result["version"])
            return 0
        except Exception as e:
            logging.error("Discovery failed: %s", e)
            return 1

    targets = get_targets(config, args)

    if args.dry_run:
        logger.info("Dry run mode: %d targets", len(targets))
        for t in targets:
            logger.info("  - %s: %s (%s)", t["id"], t["name"], t["url"])
        return 0

    scraper = DublinLifelineScraper(config_path)

    try:
        results = await run_scraper(scraper, targets, args.no_fallback)
        scraped_path = os.path.join(scraper.output_dir, "scraped_output.json")

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(config_path))))
        flyer_path = os.path.join(project_root, ".scratch", "wayfinder-map", "research", "flyer-data.json")
        output_dir = args.output or os.path.join(project_root, "src", "lib", "data")

        pipeline_result = run_pipeline(scraped_path, flyer_path, output_dir)

        error_count = sum(1 for r in results if r.get("source") == "none")
        logger.info("Summary:")
        logger.info("  Targets scraped: %d", len(results))
        logger.info("  Errors: %d", error_count)
        logger.info("  Version: %s", pipeline_result["version"])

        if error_count > 0 and args.no_fallback:
            return 1
        return 0
    except Exception as e:
        logging.error("Scraper failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
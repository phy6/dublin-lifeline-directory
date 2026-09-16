import argparse
import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scraper import DublinLifelineScraper, load_config
from pipeline import run_pipeline


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Dublin Lifeline Scraper CLI")
    parser.add_argument("--targets", help="Comma-separated list of target IDs to scrape")
    parser.add_argument("--flyer-only", action="store_true", help="Only the 10 flyer targets")
    parser.add_argument("--dry-run", action="store_true", help="Show targets without fetching")
    parser.add_argument("--no-fallback", action="store_true", help="Fail if live fetch fails")
    parser.add_argument("--verbose", action="store_true", help="Detailed logging")
    parser.add_argument("--config", default=None, help="Custom config path")
    parser.add_argument("--output", default=None, help="Custom output path")
    return parser.parse_args(args)


def get_targets(config, args):
    if args.flyer_only:
        return [t for t in config["targets"][:10]]
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


async def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config_path = args.config or os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "sources.json")
    config = load_config(config_path)

    targets = get_targets(config, args)

    if args.dry_run:
        print(f"Dry run mode: {len(targets)} targets")
        for t in targets:
            print(f"  - {t['id']}: {t['name']} ({t['url']})")
        return 0

    scraper = DublinLifelineScraper(config_path)

    try:
        results = await run_scraper(scraper, targets, args.no_fallback)
        scraped_path = os.path.join(scraper.output_dir, "scraped_output.json")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(config_path)))
        flyer_path = os.path.join(base_dir, ".scratch", "wayfinder-map", "research", "flyer-data.json")
        output_dir = args.output or os.path.join(base_dir, "src", "lib", "data")

        pipeline_result = run_pipeline(scraped_path, flyer_path, output_dir)

        error_count = sum(1 for r in results if r.get("source") == "none")
        print(f"\nSummary:")
        print(f"  Targets scraped: {len(results)}")
        print(f"  Errors: {error_count}")
        print(f"  Version: {pipeline_result['version']}")

        if error_count > 0 and args.no_fallback:
            return 1
        return 0
    except Exception as e:
        logging.error(f"Scraper failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

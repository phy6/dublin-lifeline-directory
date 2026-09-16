from scraper.scraper import (
    load_config, extract_field, fetch_with_fallback, DublinLifelineScraper, _RateLimiter, _retry_fetch,
)
from scraper.pipeline import (
    load_flyer_data, _slugify, _lookup_slug, normalize_services, merge_location,
    compute_diff, bump_version, write_services, _get_project_root, run_pipeline,
)
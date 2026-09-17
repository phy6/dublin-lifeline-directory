import argparse
import os
import sys
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scraper.main import parse_args, get_targets
from scraper import load_config


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")


FLYER_TARGET_IDS = [
    "mendicity-institution", "capuchin-day-centre", "lighthouse-cafe",
    "merchants-quay-ireland", "inclusion-health-hub",
    "inclusion-health-hub-gp", "capuchin-day-centre-gp",
    "merchants-quay-ireland-gp", "mendicity-institute-gp", "mobile-health-unit",
]


def test_help_exits_with_usage_info():
    with patch.object(sys, "argv", ["scraper/main.py", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            parse_args()
        assert exc_info.value.code == 0


def test_dry_run_prints_targets_and_exits():
    config = load_config(CONFIG_PATH)
    args = parse_args(["--dry-run"])
    assert args.dry_run is True
    targets = get_targets(config, args)
    assert len(targets) == 13


def test_flyer_only_limits_to_flyer_targets():
    config = load_config(CONFIG_PATH)
    args = parse_args(["--flyer-only"])
    assert args.flyer_only is True
    targets = get_targets(config, args)
    assert len(targets) == 3
    assert all(t["id"] in ["capuchin-day-centre", "merchants-quay-ireland", "mendicity-institution"] for t in targets)


def test_targets_filters_to_specified_subset():
    config = load_config(CONFIG_PATH)
    args = parse_args(["--targets", "capuchin-day-centre,focus-ireland"])
    assert args.targets == "capuchin-day-centre,focus-ireland"
    targets = get_targets(config, args)
    assert len(targets) == 2
    assert all(t["id"] in ["capuchin-day-centre", "focus-ireland"] for t in targets)


def test_no_fallback_sets_flag():
    args = parse_args(["--no-fallback"])
    assert args.no_fallback is True


def test_verbose_enables_detailed_logging():
    args = parse_args(["--verbose"])
    assert args.verbose is True


@pytest.mark.asyncio
async def test_dry_run_returns_0():
    with patch("scraper.main.parse_args", return_value=argparse.Namespace(
        targets=None, flyer_only=True, dry_run=True, no_fallback=False,
        verbose=False, config=None, output=None
    )):
        with patch("scraper.main.load_config") as mock_load:
            mock_load.return_value = {"targets": []}
            with patch("scraper.main.get_targets", return_value=[]):
                from scraper.main import main
                result = await main()
                assert result == 0


def test_all_cli_flags():
    args = parse_args([
        "--targets", "id1,id2",
        "--flyer-only",
        "--dry-run",
        "--no-fallback",
        "--verbose",
        "--config", "/path/to/config.json",
        "--output", "/path/to/output",
    ])
    assert args.targets == "id1,id2"
    assert args.flyer_only is True
    assert args.dry_run is True
    assert args.no_fallback is True
    assert args.verbose is True
    assert args.config == "/path/to/config.json"
    assert args.output == "/path/to/output"


def test_default_args():
    args = parse_args([])
    assert args.config is None
    assert args.targets is None
    assert args.flyer_only is False
    assert args.dry_run is False
    assert args.no_fallback is False
    assert args.verbose is False
    assert args.output is None


@pytest.mark.asyncio
async def test_no_fallback_raises_on_archive_source():
    from scraper.main import run_scraper
    targets = [{"id": "test-id"}]
    mock_scraper = MagicMock()
    mock_scraper.run = AsyncMock(return_value=[{"id": "test-id", "source": "archive"}])
    with pytest.raises(RuntimeError):
        await run_scraper(mock_scraper, targets, no_fallback=True)


@pytest.mark.asyncio
async def test_no_fallback_allows_live_source():
    from scraper.main import run_scraper
    targets = [{"id": "test-id"}]
    mock_scraper = MagicMock()
    mock_scraper.run = AsyncMock(return_value=[{"id": "test-id", "source": "live"}])
    results = await run_scraper(mock_scraper, targets, no_fallback=True)
    assert results[0]["source"] == "live"


@pytest.mark.asyncio
async def test_run_scraper_returns_results():
    from scraper.main import run_scraper
    targets = [{"id": "test-id"}]
    mock_scraper = MagicMock()
    mock_scraper.run = AsyncMock(return_value=[{"id": "test-id", "source": "live"}])
    results = await run_scraper(mock_scraper, targets, False)
    assert len(results) == 1
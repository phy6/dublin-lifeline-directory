"""Diff Charities Register candidates against scraper targets.

Produces a human-review proposal list: which candidates already match a
target, which are near-matches needing confirmation, which are brand-new
orgs, and which existing targets have no register match at all.

Promotion is deliberately manual: the human confirms via a separate
bot-communications project. This script's job is to emit a compact summary
suitable for pasting into a chat message, plus full JSON for the record.

Usage:
    python3 scraper/register_proposals.py --candidates register_candidates.json
    python3 scraper/register_proposals.py --xlsx /tmp/register.xlsx
"""

import argparse
import difflib
import json
import logging
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.fetch_register import _get_project_root, filter_candidates, parse_register

logger = logging.getLogger(__name__)

# Legal-form words that differ between a trading name and the registered name.
LEGAL_SUFFIXES = [
    "company limited by guarantee",
    "limited by guarantee",
    "designated activity company",
    "company",
    "limited",
    "ltd",
    "clg",
    "dac",
    "trust",
    "association",
    "charity",
    "charitable",
    "foundation",
]

NEAR_MATCH_CUTOFF = 0.8


def normalize_name(name: str) -> str:
    """Lowercase, strip punctuation and legal-form words for comparison."""
    text = (name or "").lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    for suffix in LEGAL_SUFFIXES:
        text = re.sub(rf"\b{re.escape(suffix)}\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def candidate_names(candidate: dict) -> list[str]:
    names = [candidate.get("name", "")]
    if candidate.get("aka"):
        names.append(candidate["aka"])
    return [n for n in names if n]


def build_proposals(candidates: list[dict], targets: list[dict]) -> dict:
    """Split candidates into matched / near_matches / new_orgs; targets with
    no register match go into unmatched_targets for review."""
    target_index = {}  # normalized name -> target id
    for target in targets:
        target_index[normalize_name(target.get("name", ""))] = target["id"]

    matched = []
    near_matches = []
    new_orgs = []
    matched_target_ids = set()

    for cand in candidates:
        norm_names = [normalize_name(n) for n in candidate_names(cand)]
        hit = next((target_index[n] for n in norm_names if n in target_index), None)
        if hit:
            matched_target_ids.add(hit)
            matched.append({"target_id": hit, "rcn": cand["rcn"], "name": cand["name"]})
            continue
        best = None
        for norm in norm_names:
            for known, tid in target_index.items():
                ours, theirs = set(norm.split()), set(known.split())
                if ours and theirs and (ours <= theirs or theirs <= ours):
                    best = (norm, known, tid)
                    break
            if best:
                break
            close = difflib.get_close_matches(norm, list(target_index), n=1, cutoff=NEAR_MATCH_CUTOFF)
            if close:
                best = (norm, close[0], target_index[close[0]])
                break
        if best:
            matched_target_ids.add(best[2])
            near_matches.append(
                {
                    "target_id": best[2],
                    "candidate_name": cand["name"],
                    "candidate_rcn": cand["rcn"],
                    "matched_on": best[0],
                }
            )
        else:
            new_orgs.append({"rcn": cand["rcn"], "name": cand["name"], "aka": cand.get("aka")})

    unmatched_targets = [
        {"id": t["id"], "name": t.get("name", "")}
        for t in targets
        if t["id"] not in matched_target_ids
    ]
    return {
        "matched": matched,
        "near_matches": near_matches,
        "new_orgs": new_orgs,
        "unmatched_targets": unmatched_targets,
    }


def summarize(proposals: dict) -> str:
    """Compact multi-line summary sized for a chat message."""
    lines = [
        "Register review: "
        f"{len(proposals['matched'])} matched, "
        f"{len(proposals['near_matches'])} to confirm, "
        f"{len(proposals['new_orgs'])} new, "
        f"{len(proposals['unmatched_targets'])} targets missing."
    ]
    for i, nm in enumerate(proposals["near_matches"][:20], 1):
        lines.append(f"{i}. Is '{nm['candidate_name']}' (RCN {nm['candidate_rcn']}) == {nm['target_id']}? (yes/no)")
    if len(proposals["near_matches"]) > 20:
        lines.append(f"...and {len(proposals['near_matches']) - 20} more in the JSON.")
    if proposals["unmatched_targets"]:
        names = ", ".join(t["id"] for t in proposals["unmatched_targets"])
        lines.append(f"Missing from register cut: {names}")
    return "\n".join(lines)


def load_targets(config_path: str) -> list[dict]:
    with open(config_path) as f:
        return json.load(f)["targets"]


def run(candidates_path: str | None, xlsx_path: str | None, output_path: str) -> dict:
    if xlsx_path:
        rows, _meta = parse_register(xlsx_path)
        candidates = filter_candidates(rows)
    else:
        with open(candidates_path) as f:
            candidates = json.load(f)["candidates"]
    project_root = _get_project_root()
    targets = load_targets(os.path.join(project_root, "scraper", "config", "sources.json"))
    proposals = build_proposals(candidates, targets)
    with open(output_path, "w") as f:
        json.dump(proposals, f, indent=2)
    summary = summarize(proposals)
    logger.info(summary)
    print(summary)
    return proposals


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Propose register candidates for target review")
    parser.add_argument("--candidates", default=None, help="register_candidates.json path")
    parser.add_argument("--xlsx", default=None, help="Parse candidates straight from the register .xlsx")
    parser.add_argument("--output", default=None, help="Proposals JSON output path")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(args)


def main(args=None) -> int:
    parsed = parse_args(args)
    logging.basicConfig(level=logging.DEBUG if parsed.verbose else logging.INFO)
    default_dir = os.path.join(_get_project_root(), "scraper", "output")
    output_path = parsed.output or os.path.join(default_dir, "register_proposals.json")
    candidates_path = parsed.candidates or os.path.join(default_dir, "register_candidates.json")
    if not parsed.xlsx and not os.path.exists(candidates_path):
        logger.error("No candidates file at %s (run fetch_register.py first) or pass --xlsx", candidates_path)
        return 1
    run(candidates_path if not parsed.xlsx else None, parsed.xlsx, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

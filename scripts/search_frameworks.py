"""Search the local SGE framework library.

Example:
    python scripts/search_frameworks.py --query "paid TikTok ad hooks" --top 10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "knowledge" / "frameworks.json"
WORD = re.compile(r"[a-z0-9]+")
STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is", "of", "on", "or", "the", "to", "with"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search local SGE framework knowledge.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to frameworks.json.")
    parser.add_argument("--query", default="", help="Keywords used to rank frameworks.")
    parser.add_argument("--platform", action="append", help="Require a platform; repeatable.")
    parser.add_argument("--knowledge-type", action="append", help="Require a knowledge type; repeatable.")
    parser.add_argument("--use-case", action="append", help="Require a use case; repeatable.")
    parser.add_argument("--min-glorify-relevance", type=float, default=0, metavar="N")
    parser.add_argument("--min-source-count", type=int, default=0, metavar="N")
    parser.add_argument("--top", type=int, default=10, metavar="N")
    return parser.parse_args()


def normalise(value: str) -> str:
    return value.strip().casefold()


def tokens(value: str) -> list[str]:
    return [token for token in WORD.findall(value.casefold()) if token not in STOP_WORDS]


def values(item: dict[str, Any], key: str) -> set[str]:
    raw = item.get(key, [])
    return {normalise(entry) for entry in raw if isinstance(entry, str)} if isinstance(raw, list) else set()


def has_all(actual: set[str], requested: Iterable[str] | None) -> bool:
    return not requested or {normalise(value) for value in requested}.issubset(actual)


def passes_filters(item: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
        has_all(values(item, "platforms"), args.platform)
        and has_all(values(item, "knowledge_types"), args.knowledge_type)
        and has_all(values(item, "use_cases"), args.use_case)
        and item.get("glorify_relevance_score", 0) >= args.min_glorify_relevance
        and item.get("source_article_count", 0) >= args.min_source_count
    )


def example_text(item: dict[str, Any]) -> str:
    examples = item.get("examples", [])
    if not isinstance(examples, list):
        return ""
    return " ".join(
        " ".join(str(example.get(key, "")) for key in ("company", "article_title", "url"))
        for example in examples if isinstance(example, dict)
    )


def fields(item: dict[str, Any]) -> dict[str, tuple[str, int]]:
    return {
        "name": (str(item.get("name", "")), 6),
        "description": (str(item.get("description", "")), 5),
        "why_it_works": (str(item.get("why_it_works", "")), 5),
        "when_to_use": (str(item.get("when_to_use", "")), 4),
        "use_cases": (" ".join(item.get("use_cases", [])), 4),
        "platforms": (" ".join(item.get("platforms", [])), 3),
        "knowledge_types": (" ".join(item.get("knowledge_types", [])), 3),
        "examples": (example_text(item), 2),
    }


def score(item: dict[str, Any], query: str) -> tuple[int, int, list[str]]:
    terms = Counter(tokens(query))
    if not terms:
        return 0, 0, []
    total, distinct_matches, evidence = 0, set(), []
    for field, (text, weight) in fields(item).items():
        counts = Counter(tokens(text))
        matches = []
        for term, requested_count in terms.items():
            if counts[term]:
                total += weight * min(counts[term], requested_count)
                distinct_matches.add(term)
                matches.append(term)
        if query.strip() and query.casefold() in text.casefold():
            total += weight * 3
            matches.append(f'phrase: "{query.strip()}"')
        if matches:
            evidence.append(f"{field}: {', '.join(matches)}")
    return total, len(distinct_matches), evidence


def render(item: dict[str, Any], search_score: int, evidence: list[str]) -> str:
    lines = [
        item.get("name", "Unnamed framework"),
        f"Search score: {search_score}",
        f"Why it matched: {'; '.join(evidence) if evidence else 'metadata filters only'}",
        f"Description: {item.get('description', '')}",
        f"Why it works: {item.get('why_it_works', '')}",
        f"When to use: {item.get('when_to_use', '')}",
        f"Glorify relevance: {item.get('glorify_relevance_score', 'n/a')}/10 | Source articles: {item.get('source_article_count', 0)}",
        "Source examples:",
    ]
    examples = item.get("examples", [])
    if isinstance(examples, list) and examples:
        for example in examples[:3]:
            if isinstance(example, dict):
                company = f" ({example['company']})" if example.get("company") else ""
                lines.append(f"- {example.get('article_title', 'Untitled')}{company}: {example.get('url', '')}")
    else:
        lines.append("- None")
    return "\n".join(lines)


def load_data(path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read framework data: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError("Framework data must be a JSON array.")
    return [item for item in raw if isinstance(item, dict)]


def main() -> int:
    args = parse_args()
    if args.top < 1 or args.min_source_count < 0 or args.min_glorify_relevance < 0:
        print("--top must be positive; minimum filters cannot be negative.", file=sys.stderr)
        return 2
    if not args.data.exists():
        print(f"Data file not found: {args.data}", file=sys.stderr)
        return 2
    try:
        items = load_data(args.data)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    filtered = [item for item in items if passes_filters(item, args)]
    ranked = [(score(item, args.query), item) for item in filtered]
    if args.query.strip():
        ranked = [(result, item) for result, item in ranked if result[0] > 0]
    ranked.sort(key=lambda pair: (pair[0][0], pair[0][1], pair[1].get("source_article_count", 0), pair[1].get("glorify_relevance_score", 0)), reverse=True)
    results = ranked[:args.top]
    print(f"{len(results)} result(s) from {len(filtered)} metadata-matched framework(s).")
    for position, ((search_score, _, evidence), item) in enumerate(results, 1):
        print(f"\n{'=' * 80}\n{position}. {render(item, search_score, evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Hybrid local retrieval for SGE growth frameworks and supporting articles.

Example:
    python scripts/search_knowledge.py --query "TikTok UGC ads for a faith app" --mode hybrid --top 10
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
DEFAULT_ARTICLE_DATA = ROOT / "data" / "sge_articles_enriched.jsonl"
DEFAULT_FRAMEWORK_DATA = ROOT / "knowledge" / "frameworks.json"
WORD = re.compile(r"[a-z0-9]+")
STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is", "of", "on", "or", "the", "to", "with"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrieve local SGE frameworks and supporting articles.")
    parser.add_argument("--query", required=True, help="Growth question or keywords to retrieve against.")
    parser.add_argument("--mode", choices=("framework", "article", "hybrid"), default="hybrid")
    parser.add_argument("--top", type=int, default=10, metavar="N", help="Top results to return per result type.")
    parser.add_argument("--data", type=Path, default=DEFAULT_ARTICLE_DATA, help="Article JSONL input.")
    parser.add_argument("--framework-data", type=Path, default=DEFAULT_FRAMEWORK_DATA, help="Framework JSON input.")
    # Existing article filters are retained. Shared metadata filters apply to both data types.
    parser.add_argument("--platform", action="append", help="Require a platform; repeatable.")
    parser.add_argument("--knowledge-type", action="append", help="Require a knowledge type; repeatable.")
    parser.add_argument("--usable-for", action="append", help="Require a usable_for/use_case value; repeatable.")
    parser.add_argument("--use-case", action="append", help="Alias for --usable-for, useful for framework retrieval.")
    parser.add_argument("--sge-category", help="Require an SGE category (articles only).")
    parser.add_argument("--min-glorify-relevance", type=float, default=0, metavar="N")
    parser.add_argument("--min-source-count", type=int, default=0, metavar="N", help="Frameworks only.")
    return parser.parse_args()


def normalise(value: str) -> str:
    return value.strip().casefold()


def tokens(value: str) -> list[str]:
    return [word for word in WORD.findall(value.casefold()) if word not in STOP_WORDS]


def has_all(actual: Iterable[str], requested: Iterable[str] | None) -> bool:
    actual_values = {normalise(value) for value in actual if isinstance(value, str)}
    return not requested or {normalise(value) for value in requested}.issubset(actual_values)


def requested_use_cases(args: argparse.Namespace) -> list[str]:
    return (args.usable_for or []) + (args.use_case or [])


def join_frameworks(items: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(items, list):
        return ""
    return " ".join(str(item.get(field, "")) for item in items if isinstance(item, dict) for field in fields)


def article_matches_filters(record: dict[str, Any], args: argparse.Namespace) -> bool:
    metadata = record["metadata"]
    return (
        has_all(metadata.get("platform", []), args.platform)
        and has_all(metadata.get("knowledge_type", []), args.knowledge_type)
        and has_all(metadata.get("usable_for", []), requested_use_cases(args))
        and (not args.sge_category or normalise(str(metadata.get("sge_category", ""))) == normalise(args.sge_category))
        and float(metadata.get("glorify_relevance", 0) or 0) >= args.min_glorify_relevance
    )


def framework_matches_filters(item: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
        has_all(item.get("platforms", []), args.platform)
        and has_all(item.get("knowledge_types", []), args.knowledge_type)
        and has_all(item.get("use_cases", []), requested_use_cases(args))
        and float(item.get("glorify_relevance_score", 0) or 0) >= args.min_glorify_relevance
        and int(item.get("source_article_count", 0) or 0) >= args.min_source_count
    )


def weighted_score(fields: dict[str, tuple[str, int]], query: str) -> tuple[int, int, list[str]]:
    query_counts = Counter(tokens(query))
    if not query_counts:
        return 0, 0, []
    score, matched_terms, evidence = 0, set(), []
    for field_name, (text, weight) in fields.items():
        counts = Counter(tokens(text))
        matches = []
        for term, requested_count in query_counts.items():
            if counts[term]:
                score += weight * min(counts[term], requested_count)
                matched_terms.add(term)
                matches.append(term)
        if query.strip() and query.casefold() in text.casefold():
            score += weight * 3
            matches.append(f'phrase: "{query}"')
        if matches:
            evidence.append(f"{field_name}: {', '.join(matches)}")
    return score, len(matched_terms), evidence


def score_article(record: dict[str, Any], query: str) -> tuple[int, int, list[str]]:
    metadata, article = record["metadata"], record["article"]
    # Content patterns remain searchable from the original article layer. A lower
    # weight keeps the specified framework/principle fields dominant.
    fields = {
        "title": (str(article.get("title", "")), 3),
        "article_summary": (str(metadata.get("article_summary", "")), 4),
        "key_principle": (str(metadata.get("key_principle", "")), 5),
        "frameworks": (join_frameworks(metadata.get("frameworks"), ("name", "description", "when_to_use", "example")), 5),
        "content_patterns": (join_frameworks(metadata.get("content_patterns"), ("name", "description", "example")), 2),
    }
    return weighted_score(fields, query)


def score_framework(item: dict[str, Any], query: str) -> tuple[int, int, list[str]]:
    fields = {
        "name": (str(item.get("name", "")), 6),
        "description": (str(item.get("description", "")), 5),
        "why_it_works": (str(item.get("why_it_works", "")), 5),
        "when_to_use": (str(item.get("when_to_use", "")), 4),
        "use_cases": (" ".join(item.get("use_cases", [])), 4),
        "platforms": (" ".join(item.get("platforms", [])), 3),
        "knowledge_types": (" ".join(item.get("knowledge_types", [])), 3),
    }
    return weighted_score(fields, query)


def load_articles(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as source:
        for number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record.get("article"), dict) or not isinstance(record.get("metadata"), dict):
                    raise ValueError("missing article or metadata")
                records.append(record)
            except (json.JSONDecodeError, ValueError) as exc:
                print(f"Warning: skipped invalid article line {number}: {exc}", file=sys.stderr)
    return records


def load_frameworks(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Framework data must be a JSON array.")
    return [item for item in raw if isinstance(item, dict)]


def ranked_articles(records: list[dict[str, Any]], args: argparse.Namespace) -> tuple[list[tuple[tuple[int, int, list[str]], dict[str, Any]]], int]:
    filtered = [record for record in records if article_matches_filters(record, args)]
    ranked = [(score_article(record, args.query), record) for record in filtered]
    ranked = [(result, record) for result, record in ranked if result[0] > 0]
    ranked.sort(key=lambda item: (item[0][0], item[0][1], item[1]["metadata"].get("glorify_relevance", 0)), reverse=True)
    return ranked[:args.top], len(filtered)


def ranked_frameworks(items: list[dict[str, Any]], args: argparse.Namespace) -> tuple[list[tuple[tuple[int, int, list[str]], dict[str, Any]]], int]:
    filtered = [item for item in items if framework_matches_filters(item, args)]
    ranked = [(score_framework(item, args.query), item) for item in filtered]
    ranked = [(result, item) for result, item in ranked if result[0] > 0]
    ranked.sort(key=lambda pair: (pair[0][0], pair[0][1], pair[1].get("glorify_relevance_score", 0), pair[1].get("source_article_count", 0)), reverse=True)
    return ranked[:args.top], len(filtered)


def render_framework(item: dict[str, Any], score: int, evidence: list[str]) -> str:
    lines = [
        item.get("name", "Unnamed framework"),
        f"Search score: {score} | Glorify relevance: {item.get('glorify_relevance_score', 'n/a')}/10 | Source count: {item.get('source_article_count', 0)}",
        f"Why it matched: {'; '.join(evidence)}",
        f"Description: {item.get('description', '')}",
        f"Why it works: {item.get('why_it_works', '')}",
        f"When to use: {item.get('when_to_use', '')}",
        "Source article examples:",
    ]
    examples = item.get("examples", [])
    for example in examples[:3] if isinstance(examples, list) else []:
        if isinstance(example, dict):
            lines.append(f"- {example.get('article_title', 'Untitled')}: {example.get('url', '')}")
    if lines[-1] == "Source article examples:":
        lines.append("- None")
    return "\n".join(lines)


def render_article(record: dict[str, Any], score: int, evidence: list[str]) -> str:
    article, metadata = record["article"], record["metadata"]
    return "\n".join((
        article.get("title", "Untitled"),
        f"URL: {article.get('url', '')}",
        f"Search score: {score} | Glorify relevance: {metadata.get('glorify_relevance', 'n/a')}/10",
        f"Why it matched: {'; '.join(evidence)}",
        f"Extracted lesson: {metadata.get('key_principle', '')}",
        f"Summary: {metadata.get('article_summary', '')}",
    ))


def print_section(title: str, results: list[Any], renderer: Any) -> None:
    print(f"\n{'=' * 80}\n{title}")
    if not results:
        print("No matching results.")
        return
    for position, ((score, _, evidence), item) in enumerate(results, 1):
        print(f"\n{'-' * 80}\n{position}. {renderer(item, score, evidence)}")


def main() -> int:
    args = parse_args()
    if args.top < 1 or args.min_glorify_relevance < 0 or args.min_source_count < 0:
        print("--top must be positive; minimum filters cannot be negative.", file=sys.stderr)
        return 2
    print(f"{'=' * 80}\nQUERY:\n{args.query}")
    if args.mode in ("framework", "hybrid"):
        if not args.framework_data.exists():
            print(f"Framework file not found: {args.framework_data}", file=sys.stderr)
            return 2
        try:
            results, matched = ranked_frameworks(load_frameworks(args.framework_data), args)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Could not load frameworks: {exc}", file=sys.stderr)
            return 2
        print_section(f"TOP FRAMEWORKS ({len(results)} of {matched} metadata-matched)", results, render_framework)
    if args.mode in ("article", "hybrid"):
        if not args.data.exists():
            print(f"Article file not found: {args.data}", file=sys.stderr)
            return 2
        try:
            results, matched = ranked_articles(load_articles(args.data), args)
        except OSError as exc:
            print(f"Could not load articles: {exc}", file=sys.stderr)
            return 2
        print_section(f"SUPPORTING ARTICLES ({len(results)} of {matched} metadata-matched)", results, render_article)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

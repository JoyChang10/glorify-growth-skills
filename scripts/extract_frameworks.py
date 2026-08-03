"""Build a reusable growth-framework library from enriched SGE articles.

The merger is deliberately semantic rather than exact-name based: it normalizes
common growth synonyms (for example, influencer -> creator and acquisition ->
distribution) and combines labels only when their meaningful concepts overlap.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "sge_articles_enriched.jsonl"
DEFAULT_OUTPUT = ROOT / "knowledge" / "frameworks.json"
WORD = re.compile(r"[a-z0-9]+")
GENERIC_WORDS = {"a", "an", "and", "approach", "based", "content", "for", "framework", "guide", "in", "led", "method", "model", "of", "strategy", "system", "tactic", "the", "to", "using", "with"}
SYNONYMS = {
    "ambassador": "creator", "ambassadors": "creator", "influencer": "creator", "influencers": "creator",
    "creator-led": "creator", "creator-driven": "creator", "ugc": "creator",
    "acquisition": "distribution", "promotion": "distribution", "marketing": "distribution",
    "ads": "ad", "advertising": "ad", "advertisement": "ad", "advertisements": "ad",
    "hooks": "hook", "hooking": "hook", "shortform": "short_form", "reels": "short_form",
    "tiktok": "short_form", "instagram": "short_form", "viral": "virality",
    "testing": "test", "experiments": "test", "experimentation": "test",
    "conversions": "conversion", "installs": "install", "downloads": "install",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract reusable SGE growth frameworks.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--min-count", type=int, default=1, metavar="N", help="Only output frameworks appearing more than N articles.")
    parser.add_argument("--checkpoint-every", type=int, default=100, metavar="N")
    return parser.parse_args()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def concept_tokens(value: str) -> frozenset[str]:
    concepts = []
    for token in WORD.findall(value.lower().replace("-", " ")):
        token = SYNONYMS.get(token, token)
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        if token not in GENERIC_WORDS and len(token) > 2:
            concepts.append(token)
    return frozenset(concepts)


def related(left: frozenset[str], right: frozenset[str]) -> bool:
    """Merge only labels with substantive overlap; never based on generic words."""
    if not left or not right:
        return False
    overlap = len(left & right)
    similarity = overlap / len(left | right)
    # A one-concept label must exactly match; broader labels need strong overlap.
    if min(len(left), len(right)) == 1:
        return left == right
    return similarity >= 0.60 or (overlap >= 2 and similarity >= 0.45)


def quality(value: str) -> tuple[int, int]:
    """Prefer specific, readable source text over empty or boilerplate strings."""
    return (int(len(value) >= 45), len(value))


@dataclass
class Cluster:
    name: str
    concepts: frozenset[str]
    descriptions: list[str] = field(default_factory=list)
    why: list[str] = field(default_factory=list)
    when: list[str] = field(default_factory=list)
    examples: dict[str, dict[str, str]] = field(default_factory=dict)
    platforms: set[str] = field(default_factory=set)
    knowledge_types: set[str] = field(default_factory=set)
    use_cases: set[str] = field(default_factory=set)
    relevance_total: int = 0
    relevance_articles: set[str] = field(default_factory=set)
    article_urls: set[str] = field(default_factory=set)

    def add(self, framework: dict[str, Any], record: dict[str, Any]) -> None:
        metadata, article = record["metadata"], record["article"]
        url = str(article.get("url", ""))
        self.descriptions.append(str(framework.get("description", "")).strip())
        self.when.append(str(framework.get("when_to_use", "")).strip())
        principle = str(metadata.get("key_principle", "")).strip()
        if principle:
            self.why.append(principle)
        self.platforms.update(item for item in metadata.get("platform", []) if isinstance(item, str))
        self.knowledge_types.update(item for item in metadata.get("knowledge_type", []) if isinstance(item, str))
        self.use_cases.update(item for item in metadata.get("usable_for", []) if isinstance(item, str))
        if url:
            self.article_urls.add(url)
            if url not in self.relevance_articles:
                self.relevance_total += int(metadata.get("glorify_relevance", 0) or 0)
                self.relevance_articles.add(url)
            companies = metadata.get("companies_mentioned", [])
            company_names = [item.get("name", "") for item in companies if isinstance(item, dict) and item.get("name")]
            self.examples[url] = {"company": ", ".join(company_names), "article_title": str(article.get("title", "")), "url": url}

    def to_output(self) -> dict[str, Any]:
        description = max((item for item in self.descriptions if item), key=quality, default="")
        when = max((item for item in self.when if item), key=quality, default="")
        principles = list(dict.fromkeys(item for item in self.why if item))
        why = " ".join(principles[:2])
        count = len(self.article_urls)
        return {
            "name": self.name,
            "description": description,
            "why_it_works": why,
            "when_to_use": when,
            "examples": sorted(self.examples.values(), key=lambda item: (item["article_title"].casefold(), item["url"])),
            "platforms": sorted(self.platforms),
            "knowledge_types": sorted(self.knowledge_types),
            "use_cases": sorted(self.use_cases),
            "glorify_relevance_score": round(self.relevance_total / count, 1) if count else 0,
            "source_article_count": count,
        }


def add_framework(clusters: list[Cluster], framework: dict[str, Any], record: dict[str, Any]) -> None:
    name = str(framework.get("name", "")).strip()
    concepts = concept_tokens(name)
    if not name or not concepts:
        return
    candidates = [cluster for cluster in clusters if related(concepts, cluster.concepts)]
    if candidates:
        # If several clusters qualify, add to the one with the most semantic overlap.
        cluster = max(candidates, key=lambda item: len(concepts & item.concepts) / len(concepts | item.concepts))
    else:
        cluster = Cluster(name=name, concepts=concepts)
        clusters.append(cluster)
    cluster.add(framework, record)


def checkpoint_path(output: Path) -> Path:
    return output.with_name(output.stem + ".checkpoint.json")


def save_checkpoint(path: Path, processed: int, clusters: list[Cluster]) -> None:
    # A safe checkpoint is intentionally human-readable; a rerun rebuilds from source
    # to avoid stale or partial clusters after data changes.
    atomic_write(path, {"articles_processed": processed, "framework_clusters": len(clusters), "status": "in_progress"})


def progress(current: int, total: int) -> None:
    width = 30
    filled = int(width * current / total) if total else width
    print(f"\rProcessing: [{'#' * filled}{'.' * (width - filled)}] {current}/{total}", end="", flush=True)


def load_records(path: Path) -> list[dict[str, Any]]:
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
                print(f"\nWarning: skipped invalid line {number}: {exc}", file=sys.stderr)
    return records


def main() -> int:
    args = parse_args()
    if args.min_count < 0 or args.checkpoint_every < 1:
        print("--min-count must be non-negative and --checkpoint-every must be positive.", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    records = load_records(args.input)
    clusters: list[Cluster] = []
    for number, record in enumerate(records, 1):
        frameworks = record["metadata"].get("frameworks", [])
        if isinstance(frameworks, list):
            for framework in frameworks:
                if isinstance(framework, dict):
                    add_framework(clusters, framework, record)
        if number % 25 == 0 or number == len(records):
            progress(number, len(records))
        if number % args.checkpoint_every == 0:
            save_checkpoint(checkpoint_path(args.output), number, clusters)
    print()

    output = [cluster.to_output() for cluster in clusters]
    output = [item for item in output if item["source_article_count"] > args.min_count]
    output.sort(key=lambda item: (item["source_article_count"], item["glorify_relevance_score"]), reverse=True)
    atomic_write(args.output, output)
    checkpoint_path(args.output).unlink(missing_ok=True)

    print("\nFramework extraction complete.\n")
    print(f"Articles processed: {len(records)}")
    print(f"Unique frameworks found: {len(output)}")
    print("\nTop frameworks:\n")
    for number, item in enumerate(output[:10], 1):
        print(f"{number}. {item['name']}\n   Articles: {item['source_article_count']}\n   Glorify relevance: {item['glorify_relevance_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

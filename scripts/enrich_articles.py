"""Enrich Social Growth Engineers articles into retrieval-ready JSONL records.

Each output line has the shape ``{"article": {...}, "metadata": {...}}``.
The script is intentionally resumable: URLs already present in the output JSONL
are skipped on the next run. API keys are read from OPENAI_API_KEY (preferred)
or a local key file that is never written to output or logs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "sge_articles_sitemap.json"
DEFAULT_OUTPUT = ROOT / "data" / "sge_articles_enriched.jsonl"
DEFAULT_ERRORS = ROOT / "data" / "sge_articles_enrichment_errors.jsonl"

ALLOWED: dict[str, set[str]] = {
    "sge_category": {"Strategy", "Format", "Trend", "Opinion", "Newcomer", "Case Studies", "Growth Lab"},
    "knowledge_type": {"viral_growth", "content_strategy", "ugc_strategy", "creator_marketing", "paid_ads", "growth_loops", "retention", "community", "positioning", "product_marketing", "conversion", "app_store_growth", "brand_building", "copywriting", "influencer_strategy"},
    "platform": {"TikTok", "Instagram", "YouTube", "Reddit", "App Store", "Google Play", "Email", "Community", "Offline", "Website", "Other"},
    "industry": {"consumer_app", "social_app", "mobile_game", "wearable", "health", "fitness", "wellness", "faith", "education", "ecommerce", "saas", "creator_economy", "media", "marketplace", "other"},
    "growth_stage": {"pre_launch", "early_growth", "scaling", "mature", "unknown"},
    "growth_problem": {"user_acquisition", "brand_awareness", "content_creation", "organic_growth", "paid_growth", "conversion", "retention", "community_building", "creator_distribution", "market_positioning"},
    "metrics_affected": {"views", "engagement", "followers", "click_through_rate", "conversion_rate", "install_rate", "retention_rate", "revenue", "brand_awareness"},
    "usable_for": {"content_ideation", "ugc_script_generation", "tiktok_analysis", "instagram_analysis", "paid_ad_analysis", "competitor_analysis", "trend_analysis", "growth_experiment", "landing_page_copy", "email_copy", "community_management"},
}

SCHEMA: dict[str, Any] = {
    "name": "sge_article_metadata",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["sge_category", "knowledge_type", "platform", "industry", "growth_stage", "growth_problem", "frameworks", "key_principle", "article_summary", "companies_mentioned", "content_patterns", "metrics_affected", "usable_for", "evergreen_score", "glorify_relevance", "confidence_score"],
        "properties": {
            "sge_category": {"type": "string", "enum": sorted(ALLOWED["sge_category"])},
            "knowledge_type": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["knowledge_type"])}},
            "platform": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["platform"])}},
            "industry": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["industry"])}},
            "growth_stage": {"type": "string", "enum": sorted(ALLOWED["growth_stage"])},
            "growth_problem": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["growth_problem"])}},
            "frameworks": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["name", "description", "when_to_use", "example"], "properties": {key: {"type": "string"} for key in ("name", "description", "when_to_use", "example")}}},
            "key_principle": {"type": "string"},
            "article_summary": {"type": "string"},
            "companies_mentioned": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["name", "role", "lesson"], "properties": {key: {"type": "string"} for key in ("name", "role", "lesson")}}},
            "content_patterns": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["name", "description", "example"], "properties": {key: {"type": "string"} for key in ("name", "description", "example")}}},
            "metrics_affected": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["metrics_affected"])}},
            "usable_for": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED["usable_for"])}},
            "evergreen_score": {"type": "integer", "minimum": 1, "maximum": 10},
            "glorify_relevance": {"type": "integer", "minimum": 1, "maximum": 10},
            "confidence_score": {"type": "integer", "minimum": 1, "maximum": 100},
        },
    },
}

SYSTEM_PROMPT = """You are a growth strategist analyzing Social Growth Engineers articles.
Extract reusable growth knowledge, not a mere summary. Explain why each framework
works and make it useful to a consumer-app growth team. Assess relevance to
Glorify Ring: faith technology, wearables, mobile apps, TikTok/Instagram growth,
and UGC. Use only the enum values in the supplied response schema. Do not infer
facts that are not supported by the article."""


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--errors", type=Path, default=DEFAULT_ERRORS)
    p.add_argument("--api-key-file", type=Path, default=ROOT / "socialgrowthengineers_api.txt")
    p.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    p.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    p.add_argument("--limit", type=int, help="Maximum number of not-yet-enriched articles to process.")
    p.add_argument("--start", type=int, default=0, help="Zero-based source offset, useful for controlled batches.")
    p.add_argument("--max-content-chars", type=int, default=24000)
    p.add_argument("--retries", type=int, default=4)
    p.add_argument("--dry-run", action="store_true", help="Validate input and show the work queue without calling the API.")
    return p


def api_key(key_file: Path) -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key and key_file.exists():
        key = key_file.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY or provide a file with the API key via --api-key-file.")
    return key


def completed_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    urls: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if line.strip():
                try:
                    urls.add(json.loads(line)["article"]["url"])
                except (json.JSONDecodeError, KeyError, TypeError) as exc:
                    raise RuntimeError(f"Invalid output record at {path}:{line_number}") from exc
    return urls


def validate_article(article: Any, index: int) -> dict[str, str]:
    if not isinstance(article, dict) or not all(isinstance(article.get(k), str) and article[k].strip() for k in ("url", "title", "content")):
        raise ValueError(f"Input article {index} must contain non-empty string url, title, and content.")
    return {key: article[key].strip() for key in ("url", "title", "content")}


def enrich(article: dict[str, str], key: str, args: argparse.Namespace) -> dict[str, Any]:
    content = article["content"][: args.max_content_chars]
    payload = {"model": args.model, "temperature": 0, "response_format": {"type": "json_schema", "json_schema": SCHEMA}, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Title:\n{article['title']}\n\nContent:\n{content}"}]}
    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            response = requests.post(endpoint, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=payload, timeout=90)
            response.raise_for_status()
            metadata = json.loads(response.json()["choices"][0]["message"]["content"])
            return {"article": article, "metadata": metadata}
        except (requests.RequestException, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == args.retries:
                break
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"API request failed after {args.retries + 1} attempts: {last_error}")


def main() -> int:
    args = parser().parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Input must be a JSON array of articles.")
        articles = [validate_article(article, i) for i, article in enumerate(raw)]
        done = completed_urls(args.output)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    queued = [article for article in articles[args.start:] if article["url"] not in done]
    if args.limit is not None:
        queued = queued[: args.limit]
    print(f"Source articles: {len(articles)} | completed: {len(done)} | queued: {len(queued)}")
    if args.dry_run or not queued:
        return 0

    try:
        key = api_key(args.api_key_file)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for number, article in enumerate(queued, 1):
        try:
            record = enrich(article, key, args)
            with args.output.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"[{number}/{len(queued)}] enriched {article['url']}")
        except Exception as exc:  # keep the batch running and preserve the failure for retry.
            error = {"article": article, "error": str(exc)}
            with args.errors.open("a", encoding="utf-8") as f:
                f.write(json.dumps(error, ensure_ascii=False) + "\n")
            print(f"[{number}/{len(queued)}] failed {article['url']}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

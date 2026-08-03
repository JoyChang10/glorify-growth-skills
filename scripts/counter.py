import json
from pathlib import Path

articles = Path(__file__).resolve().parent.parent / 'data' / 'sge_articles_sitemap.json'

with open(articles, 'r', encoding='utf-8') as f:
    articles = json.load(f)

print(f"Total articles in JSON: {len(articles)}")

articles_enriched = Path(__file__).resolve().parent.parent / 'data' / 'sge_articles_enriched.jsonl'

# Read line by line for JSONL format
with open(articles_enriched, 'r', encoding='utf-8') as f:
    articles_enriched = [json.loads(line) for line in f if line.strip()]

print(f"Total articles in JSONL: {len(articles_enriched)}")
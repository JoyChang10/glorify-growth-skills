# Social Growth Engineers Knowledge System

Turn Social Growth Engineers (SGE) articles into a local growth knowledge base for Glorify Ring. The project enriches articles, extracts reusable growth frameworks, and retrieves both frameworks and supporting article evidence for content planning and creator briefs.

Everything used for retrieval is local JSON. The search tools do not use embeddings, a vector database, or an API.

## What is included

```text
data/
  sge_articles_sitemap.json          # Raw scraped SGE article records
  sge_articles_enriched.jsonl        # Article records plus structured growth metadata
knowledge/
  frameworks.json                    # Reusable, aggregated growth frameworks
scripts/
  enrich_articles.py                 # Enrich raw articles with structured metadata
  extract_frameworks.py              # Build the framework library
  search_knowledge.py                # Hybrid framework + article retriever
  search_frameworks.py               # Framework-only retriever
skills/
  content-strategy-planner/          # Campaign and content-plan skill
  creative-brief-generator/          # Creator-ready brief and script skill
prompts/
  enrichment_prompt.txt              # Original enrichment prompt
config/
  sge_metadata.json                  # Metadata schema reference
```

## Setup

Requires Python 3.10 or later.

```powershell
git clone <YOUR_REPOSITORY_URL>
cd <REPOSITORY_FOLDER>

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file only if you will run article enrichment:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

Never commit `.env` or an API-key file. Use `.env.example` as the safe template when one is available.

## Data and publishing choices

The enriched dataset and raw sitemap data contain scraped SGE article content. Before making this repository public, confirm that you have permission to redistribute that content and that doing so complies with the source site’s terms.

For a private repository, it is practical to version the local knowledge base:

```text
data/sge_articles_sitemap.json
data/sge_articles_enriched.jsonl
knowledge/frameworks.json
```

For a public repository, consider publishing only the code, schema, prompts, and skills, then document an approved process for supplying the data separately.

## Workflows

### 1. Enrich articles

This is the only workflow that calls an LLM API. It reads raw article records and writes resumable JSONL output.

```powershell
python scripts/enrich_articles.py --limit 10
```

Run without `--limit` only after checking a small batch:

```powershell
python scripts/enrich_articles.py
```

Default input and outputs:

```text
data/sge_articles_sitemap.json
data/sge_articles_enriched.jsonl
data/sge_articles_enrichment_errors.jsonl
```

### 2. Extract reusable frameworks

Build `knowledge/frameworks.json` from the enriched article data. The extractor semantically normalizes related framework names, aggregates source examples, and saves output atomically.

```powershell
python scripts/extract_frameworks.py
```

Keep only frameworks appearing in more than two articles:

```powershell
python scripts/extract_frameworks.py --min-count 2
```

### 3. Search frameworks and articles together

Use hybrid mode to retrieve reusable principles first and supporting SGE articles second:

```powershell
python scripts/search_knowledge.py `
  --query "TikTok UGC faith wearable pre-order campaign" `
  --mode hybrid `
  --platform TikTok `
  --min-glorify-relevance 6 `
  --top 10
```

Modes:

```text
--mode framework   # Framework principles only
--mode article     # Supporting SGE articles only
--mode hybrid      # Both; default
```

Useful filters:

```text
--platform TikTok
--knowledge-type ugc_strategy
--usable-for ugc_script_generation
--use-case paid_ad_analysis
--sge-category Trend
--min-glorify-relevance 7
--min-source-count 3
```

### 4. Search the framework library only

```powershell
python scripts/search_frameworks.py `
  --query "paid TikTok ad hooks and conversion" `
  --platform TikTok `
  --use-case paid_ad_analysis `
  --min-glorify-relevance 6 `
  --top 10
```

## Codex skills

Clone this repository before installing either skill. The skills retrieve local
frameworks and article evidence from this project, so installing only a skill
folder is not enough.

The repository keeps the source versions of both Glorify skills under `skills/`:

- `content-strategy-planner`: answers “What content should we make?”
- `creative-brief-generator`: answers “How exactly do we make this video?”


### Install the skills in Codex (Windows)

1. Clone the repository and install dependencies using the [Setup](#setup) steps.
2. Copy the complete skill folders into Codex's global skills directory:

```powershell
Copy-Item `
  ".\skills\content-strategy-planner" `
  "E:\Codex\.codex\skills\content-strategy-planner" `
  -Recurse -Force

Copy-Item `
  ".\skills\creative-brief-generator" `
  "E:\Codex\.codex\skills\creative-brief-generator" `
  -Recurse -Force
```

3. Restart or refresh Codex so both skills appear in the skill menu.
4. Open the cloned repository as the active Codex workspace before invoking a skill. This lets it access:

```text
data/sge_articles_enriched.jsonl
knowledge/frameworks.json
scripts/search_knowledge.py
```

Invoke either skill in Codex:

```text
$content-strategy-planner
Create a four-week TikTok and Instagram pre-order content plan for Glorify Ring.
```

```text
$creative-brief-generator
Turn this Glorify Ring idea into a creator-ready 30-second TikTok/Reel script: ...
```

### Update installed skills

Keep the repository copy as the source of truth. To get the latest version,
pull the repository, rerun the two copy commands above, then refresh Codex:

```powershell
git pull
```

## Security

Do not store API keys in source code, prompts, JSON data, or committed files. Use environment variables or a local `.env` file excluded by `.gitignore`.

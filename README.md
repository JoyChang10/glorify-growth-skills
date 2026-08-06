# Social Growth Engineers Knowledge System

Turn Social Growth Engineers (SGE) articles into a local growth knowledge base for Glorify Ring. The project enriches articles, extracts reusable growth frameworks, and retrieves both frameworks and supporting article evidence for content planning and creator briefs.

Everything used for retrieval is local JSON. The search tools do not use embeddings, a vector database, or an API.

## Setup

Requires Python 3.10 or later.

```powershell
git clone <YOUR_REPOSITORY_URL>
cd <REPOSITORY_FOLDER>

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Codex skills

Clone this repository before installing a skill. The skills retrieve local
frameworks and article evidence from this project, so installing only a skill
folder is not enough.

The repository keeps the source versions of the Glorify skills under `skills/`:

### Four-skill workflow

1. `content-strategy-planner` — decide what content to make.
2. `content-brief-generator` — turn an idea into a creator-ready video.
3. `content-improvement-advisor` — improve an existing creative.
4. `campaign-growth-strategist` — decide what to change, scale, or stop after a test.

- `content-strategy-planner`: answers “What content should we make?”
- `content-brief-generator`: answers “How exactly do we make this video?”


`content-improvement-advisor` answers: "How can we improve this existing content?"

`campaign-growth-strategist` answers: "What did we learn from this test, and what should we change, scale, or stop?"

### Install the skills in Codex (Windows)

1. Clone the repository and install dependencies using the [Setup](#setup) steps.
2. Copy the complete skill folders into Codex's global skills directory:

```powershell
Copy-Item `
  ".\skills\content-strategy-planner" `
  "E:\Codex\.codex\skills\content-strategy-planner" `
  -Recurse -Force

Copy-Item `
  ".\skills\content-brief-generator" `
  "E:\Codex\.codex\skills\content-brief-generator" `
  -Recurse -Force

Copy-Item `
  ".\skills\content-improvement-advisor" `
  "E:\Codex\.codex\skills\content-improvement-advisor" `
  -Recurse -Force

Copy-Item `
  ".\skills\campaign-growth-strategist" `
  "E:\Codex\.codex\skills\campaign-growth-strategist" `
  -Recurse -Force
```

3. Restart or refresh Codex so the skills appear in the skill menu.
4. Open the cloned repository as the active Codex workspace before invoking a skill. This lets it access:

```text
data/sge_articles_enriched.jsonl
knowledge/frameworks.json
scripts/search_knowledge.py
```

Invoke a skill in Codex:

```text
$content-strategy-planner
Create a four-week TikTok and Instagram pre-order content plan for Glorify Ring.
```

```text
$content-brief-generator
Turn this Glorify Ring idea into a creator-ready 30-second TikTok/Reel script: ...

$content-improvement-advisor
Review this Glorify Ring TikTok script and improve its hook, story, product integration, CTA, and test plan: ...

$campaign-growth-strategist
Review these Glorify Ring TikTok test results and recommend what to scale, iterate, or stop: ...
```
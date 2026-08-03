---
name: content-strategy-planner
description: Create evidence-backed TikTok and Instagram content strategies for the Glorify Ring growth team when they need concepts, scripts, formats, creator direction, or a campaign plan from a blank slate. Use for pre-order, acquisition, awareness, launch, and testing plans that should retrieve local Social Growth Engineers frameworks and article examples before making recommendations.
---

# Glorify Content Strategy Planner

Create a practical short-form content plan grounded in local SGE knowledge. Use framework results as reusable principles and article results as evidence or execution examples; never present either as a guarantee.

## Prepare

Read [glorify-context.md](glorify-context.md) and [output-template.md](output-template.md). Read [examples.md](examples.md) when the brief is close to the included audience, goal, or capacity.

Extract or infer: campaign goal, target audience, platform, product message, campaign duration, posting capacity, available creators, and production constraints.

Ask only for a missing item that would materially change the plan. Otherwise proceed with an **Assumptions** note. Default to one clear product benefit per video, platform-native vertical video, and a lightweight test-and-learn plan.

## Retrieve local SGE knowledge

Run the repository’s hybrid retriever from the project root; use no API, embedding, or vector database.

1. Run one primary query based on the product, audience, goal, and platform.
2. Run 2–3 focused queries to cover hooks/formats, creator or UGC execution, and testing/distribution. Add relevant filters where supported.
3. Retrieve both framework principles and supporting articles each time (`--mode hybrid`).

Example commands:

```powershell
python scripts/search_knowledge.py --query "TikTok UGC ads for a faith wearable pre-order campaign" --mode hybrid --platform TikTok --min-glorify-relevance 6 --top 8
python scripts/search_knowledge.py --query "short-form video hooks product demo conversion" --mode hybrid --min-glorify-relevance 6 --top 8
python scripts/search_knowledge.py --query "creator UGC strategy faith consumer app" --mode hybrid --min-glorify-relevance 6 --top 8
python scripts/search_knowledge.py --query "content testing distribution and paid amplification" --mode hybrid --min-glorify-relevance 6 --top 8
```

Prefer results that match the audience, platform, goal, and constraints. Record framework names and article titles/URLs actually used. Treat weakly related results as inspiration only, not evidence.

## Build the plan

1. State the objective, audience insight, and one falsifiable strategic hypothesis.
2. Turn 3–5 retrieved principles into distinct content pillars. Assign each pillar a job in the funnel.
3. Specify formats and ten shootable concepts. Give each concept three genuinely different first-second hooks, a CTA, and a simple execution note.
4. Adapt concepts to the Glorify Ring’s faith-focused wearable context without making unverified product, health, or outcome claims.
5. Build a weekly plan that respects the stated capacity. Reuse a pillar or format only with a deliberate variation in hook, creator angle, proof, or CTA.
6. Define a testing matrix. Choose metrics by campaign goal: for pre-orders, prioritize qualified clicks, landing-page conversion, cost per pre-order (when paid), and pre-orders; track views, hold rate, and engagement as diagnostic metrics.
7. Close with the exact SGE frameworks and supporting source articles used.

## Quality bar

- Distinguish evidence, recommendation, assumption, and hypothesis.
- Use article examples to explain execution patterns, not to copy scripts or creative wholesale.
- Do not claim a format will go viral, guarantee conversion, or imply faith outcomes.
- Keep hooks specific to the audience’s situation; avoid generic “stop scrolling” language unless supported by a clear creative reason.
- Make every concept feasible under the stated creator and production constraints.

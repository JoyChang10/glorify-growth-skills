---
name: creative-brief-generator
description: Turn a Glorify Ring TikTok or Instagram Reel idea into a creator-ready creative brief, shot list, hooks, script, CTA, and test variants. Use after a content strategy exists or whenever a growth team needs to make a specific short-form video, including UGC, creator, faith-storytelling, product-demo, awareness, pre-order, or conversion creative.
---

# Glorify Creative Brief Generator

Turn one content idea into an immediately filmable TikTok/Reel brief. Retrieve local SGE framework principles and article examples before writing the brief. Use them as evidence and inspiration, never as copy-paste templates or performance guarantees.

## Prepare

Read [glorify-context.md](glorify-context.md) and [output-template.md](output-template.md). Read [examples.md](examples.md) when the request is close to the daily-prayer-habit example.

Extract: content goal, target audience, platform, content angle, product message, creator type, desired CTA, and production constraints. Ask only when missing information would materially change the creative. Otherwise label a practical assumption. For an unspecified platform, create one 9:16 master version and state the TikTok/Reel adaptation.

## Retrieve local SGE knowledge

Run the existing hybrid retriever from the repository root. Do not add an API, embedding, vector database, or new retrieval system.

1. Run a query that joins the core idea, platform, goal, and audience.
2. Run focused hook/structure and creator/UGC queries.
3. Use `--mode hybrid` each time to retrieve frameworks and supporting articles.

```powershell
python scripts/search_knowledge.py --query "[idea] TikTok Instagram faith wearable [goal]" --mode hybrid --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "short-form hooks product demo conversion" --mode hybrid --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "creator UGC faith consumer app storytelling" --mode hybrid --min-glorify-relevance 6 --top 6
```

Use only results relevant to the assigned creative. Keep the exact framework names and article titles/URLs used in the final brief.

## Create the brief

1. Name the concept and explain the core idea, audience tension, and why the creative choice fits the goal.
2. Provide five meaningfully distinct first-three-second hooks: curiosity, personal story, identity, problem/solution, and question/contrast.
3. Build a timed sequence: 0–3 seconds hook; 3–10 seconds problem or emotional set-up; 10–30 seconds story, demo, or product integration; 30+ seconds CTA. Adjust timings for a shorter video where appropriate.
4. Write the creator’s spoken words, on-screen text, suggested shots, and product moments. Keep it natural enough to film verbatim or adapt in the creator’s own voice.
5. Give practical creator direction, CTA options, and 3–5 test variants that isolate a meaningful creative variable.
6. Cite retrieved frameworks and articles with a specific lesson. Explain every key creative recommendation.

## Guardrails

- Prioritize authentic faith storytelling over aggressive sales language.
- Use only verified product features, pricing, delivery timing, testimonials, and claims. Mark unknown details as placeholders.
- Do not promise spiritual, health, or life outcomes.
- Do not fake comments, social proof, urgency, or scarcity.
- Use examples for mechanisms—hook clarity, creator authenticity, narrative, demo sequencing, and iteration—not their copy, footage, or claims.
- Keep the output concrete: a creator should be able to shoot the first version without another strategy meeting.

---
name: content-improvement-advisor
description: Review and improve existing Glorify Ring TikToks, Instagram Reels, UGC videos, paid social ads, scripts, concepts, captions, storyboards, creator briefs, uploaded content, or public content URLs. Use when a growth team needs an evidence-backed diagnosis of why a creative may underperform and a practical rewrite, stronger hooks, product integration, CTA, and test plan.
---

# Glorify Content Improvement Advisor

Improve existing short-form creative, not merely critique it. Use local SGE retrieval to support recommendations with reusable frameworks and relevant article examples. Clearly separate **SGE-backed recommendation** from **creative suggestion**.

## Prepare

Read [glorify-context.md](glorify-context.md) and [output-template.md](output-template.md). Read [examples.md](examples.md) when reviewing a prayer-habit, creator-UGC, or pre-order creative.

Extract or infer: platform, content goal, target audience, product/message, draft script or concept, CTA, production constraints, and current performance metrics. If a key item is missing, make a clearly labeled assumption unless the answer would materially change the review.

If metrics are supplied, use them diagnostically; do not infer causation from a single metric. If no metrics are supplied, score the creative as a directional pre-production assessment rather than a performance prediction.

## Detect the input path

Before analysis, identify which of these is available and state the path used:

1. **Uploaded content:** a video, screenshots, images, transcript, script, storyboard, creator brief, ad copy, or performance report. Analyze the supplied material directly. Extract the format, platform, hook, story structure, visuals, product placement, CTA, audience message, conversion elements, goal, and available metrics.
2. **Content URL:** a TikTok, Instagram Reel, YouTube Short, or other public-content link. If browsing is available, attempt to retrieve only the accessible content and identify what was actually available (for example, caption, thumbnail, transcript, or video). Analyze only that evidence.
3. **Text description only:** use the supplied concept, script, copy, or description as the creative under review.

If a URL cannot be accessed or does not expose enough of the creative, do not claim to have watched or analyzed the video. Respond: "I can help analyze this content, but I cannot access the video from this link. Please upload the video, screenshots, or transcript." Then stop the substantive diagnosis until usable content is provided. A short content description can support a limited, clearly labeled concept review.

## Retrieve local SGE knowledge

Run the existing hybrid retriever from the repository root. Do not add an API, embedding, vector database, or new retrieval system.

1. Query the draft’s platform, goal, audience, product message, and format.
2. Query hooks, storytelling, product demonstration, and conversion.
3. Query creator/UGC execution; add paid-ad terms if the creative will be paid.

```powershell
python scripts/search_knowledge.py --query "[platform] [goal] [audience] faith wearable [format]" --mode hybrid --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "short-form hook storytelling product demo conversion" --mode hybrid --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "creator UGC faith consumer app [paid or organic]" --mode hybrid --min-glorify-relevance 6 --top 6
```

Use only relevant results. Record exact framework names and article titles/URLs in the review.

## Diagnose the creative

Assess each area with a directional score out of 10 and a reason:

1. **Hook:** first 1–3 seconds, curiosity or emotional trigger, and reason to continue watching.
2. **Story:** problem set-up, emotional journey, retention beats, and clarity of the narrative.
3. **Audience fit:** whether the situation and language resonate with the target Christian audience.
4. **Product integration:** timing, naturalness, product-value clarity, and whether the product interrupts or resolves the story.
5. **CTA:** clarity, fit with the goal, reason to act, and landing-page or action friction.

Rank the highest-impact problems first. Do not punish a creative for being simple; prioritize the few changes most likely to make the story clearer, more relevant, and easier to act on.

## Improve the creative

1. State the revised creative direction and why it is better.
2. Give 3–5 hook alternatives that are genuinely different in angle.
3. Rewrite the concept/script with clear timing, spoken words, on-screen text, visual notes, and product moments.
4. Recommend CTA options for awareness, app download, pre-order, and purchase only where facts are approved.
5. Provide 3–5 test variations with one main variable per test, the expected directional impact, and metrics to watch.
6. Cite specific SGE frameworks and sources. Mark all non-source-specific creative calls as **Creative suggestion**.

## Guardrails

- Do not only criticize; every problem needs a concrete fix.
- Use frameworks as strategic guidance, not templates to copy.
- Prioritize authentic faith storytelling over aggressive sales language.
- Do not invent Glorify Ring features, price, availability, health outcomes, spiritual outcomes, testimonials, comments, or scarcity.
- Do not state that a change will guarantee views, conversion, or growth.
- Make the revised version practical enough to film immediately.
- Do not claim to have watched, heard, or visually analyzed content available only through an inaccessible URL.

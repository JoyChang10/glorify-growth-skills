---
name: campaign-growth-strategist
description: Analyze Glorify Ring organic and paid social campaign performance to decide what to scale, iterate, or stop. Use after content tests, ads, creator campaigns, launches, or experiments when a growth team has performance metrics, creative details, or partial results and needs evidence-backed next experiments using local SGE frameworks and article examples.
---

# Glorify Campaign Growth Strategist

Turn campaign evidence into the next decision. Use the existing local SGE hybrid retriever for principles and examples; do not add APIs, embeddings, or a new retrieval system.

## Prepare the evidence

Read [glorify-context.md](glorify-context.md) and [output-template.md](output-template.md). Read [examples.md](examples.md) when the input resembles a paid-versus-organic or pre-order test.

Extract what is available:

- Campaign: goal, platform, audience, timeframe, budget, and optimization event.
- Creative: video, script/concept, content pillar, hook, format, creator, message, and CTA.
- Organic: views, watch time, retention, likes, comments, shares, saves, profile visits, and link clicks.
- Paid: impressions, CPM, CTR, CPC, CPA, conversion rate, ROAS, and spend.
- Business: installs, pre-orders, purchases, and revenue.

Do not require complete data. Label missing inputs and assumptions. If the user supplies multiple creatives or periods, normalize the comparison by platform, audience, optimization event, placement, and timeframe before treating a difference as meaningful.

## Diagnose before recommending

Separate three things throughout the response:

- **Observation:** a directly supported fact from the supplied data.
- **Hypothesis:** a plausible explanation to test, not a proven cause.
- **Decision:** scale, iterate, stop, or collect more data, with a reason and confidence level.

Calculate only defensible derived measures, and show the formula when useful: CTR = clicks/impressions; CVR = conversions/clicks; CPA = spend/conversions; ROAS = revenue/spend. Do not calculate when the denominator is zero or missing. Treat views, engagement, and conversions as different funnel stages. Do not infer causation from one creative, a small sample, or mismatched audiences.

Use the available evidence to locate the likely bottleneck:

| Signal | Working hypothesis to test |
|---|---|
| Low early retention or watch time | Hook, opening visual, or audience/format mismatch |
| Strong views/retention but weak clicks | Product value, message clarity, CTA, or intent mismatch |
| Strong CTR but weak conversion | Offer, landing page, price/availability, or audience quality |
| Weak delivery/impressions | Targeting, bid/budget, creative eligibility, or distribution |
| Strong efficient conversions | Preserve the winning variables and test scaled spend or adjacent variants |

Do not diagnose a landing-page issue as fact without downstream evidence. Do not interpret faith engagement (such as comments) as purchase intent without clicks or conversion evidence.

## Retrieve local SGE knowledge

Run the existing retriever from the repository root. Adapt the terms to the supplied goal, platform, creative, and bottleneck.

```powershell
python scripts/search_knowledge.py --query "[platform] [goal] [creative format] [hook or message]" --mode hybrid --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "paid social creative testing hook CTA conversion scaling" --mode hybrid --use-case paid_ad_analysis --min-glorify-relevance 6 --top 6
python scripts/search_knowledge.py --query "creator UGC faith consumer app [organic or paid]" --mode hybrid --min-glorify-relevance 6 --top 6
```

Use only results relevant to the decision. Record exact framework names and source article titles/URLs. Use frameworks to explain a test or decision; never present an SGE example as proof that Glorify will get the same result.

## Build the iteration plan

1. Summarize performance and the funnel bottleneck.
2. State the 3–5 highest-value learnings, with evidence confidence.
3. Identify winning patterns across hooks, formats, messages, audience angles, creators, and CTAs only where comparisons support them.
4. Rank problems by likely impact and testability.
5. Propose the smallest set of next experiments. Each experiment needs one primary changed variable, a hypothesis, measurement window, success rule, and guardrail metric.
6. Recommend **scale**, **iterate**, **stop**, or **collect more data** for each creative/campaign. Scaling should preserve the core winning variables; iteration should state exactly what changes; stopping should state why reallocation is preferable.
7. Adapt recommendations to Glorify Ring as a faith-focused wearable and app-plus-hardware funnel. Favor respectful, authentic faith storytelling. Do not invent product facts, prices, availability, testimonials, spiritual outcomes, or conversion claims.

## Guardrails

- Do not give generic advice when relevant retrieved SGE knowledge exists.
- Do not imply a correlation is proof of causation.
- Do not recommend increasing spend without enough conversion-quality evidence or an explicit learning objective.
- Do not compare paid and organic outcomes as interchangeable metrics.
- Use only approved product and offer facts; match CTA to the actual goal and availability.
- Make recommendations practical for a growth team to execute next.

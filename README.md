# Circular Economy Concept Generator

A Flask app that generates tailored circular economy business model concepts for organizations, using a combination of web research, RAG knowledge bases, and LLM-driven ideation.

## Research Agent: Observations and Known Limitations

### The Observation

When researching **Cape Cod Chips (Amplify Snack Brands)**, the original Claude-native `web_search` tool surfaced a specific and recent detail: a partnership with **Ahold Delhaize** on a regenerative agriculture pilot (December 2024). The current Tavily-based pipeline does not reliably surface this level of specificity — partner names, joint pilots, and dated announcements tend to be underrepresented in results.

This matters because Q4 of the research framework is explicitly an *exclusion filter*: what has the organization already announced? Missing existing programs leads the concept generator to propose things the client has already done, which undermines workshop credibility.

Q1 — What does the organization make or do?
Cape Cod makes premium kettle-cooked potato chips (Classic, Less Fat, Waves, Multipacks) via small-batch frying. Owned by Campbell's Company through the 2018 Snyder's-Lance acquisition. Production is consolidating from Hyannis (closing April 2026) into three plants in WI, NC, and PA.

Q2 — Where does waste, inefficiency, or end-of-life live in their value chain?
Three clear hotspots: (1) chip bags are multilayer metallized film — not curbside recyclable, essentially unrecoverable at scale; (2) potato processing generates 15–40% peel/reject waste by mass plus spent frying oil; (3) Scope 3 agricultural emissions from potato farming are large and barely addressed (0.5% reduction toward a 25% target).

Q3 — What pressure is driving the need to change?
Seven US states now have packaging EPR laws (Oregon went live July 2025, California SB 54 escalating). Frito-Lay already has compostable bags in market. Campbell's SBTi-approved targets are tied to executive compensation. Retail partners (Ahold Delhaize) are already running sustainability pilots with them directly.

Q4 — What circular territory have they already explored?
Kettle Brand bag redesign cut plastic 43%. Multipacks moved to curbside-recyclable paperboard cartons. How2Recycle labels on all eligible packaging. At the Salem OR Kettle plant: potato waste to dairy feed, spent oil to biodiesel. December 2024: a 1,000-acre regenerative agriculture pilot with Ahold Delhaize, explicitly named Cape Cod chips as the output. No compostable or recyclable chip bag for Cape Cod specifically yet.

Q5 — What does a successful outcome look like?
A curbside-recyclable or certified compostable chip bag. Scaled regenerative potato sourcing beyond the pilot. Full potato processing waste diversion across all plants. EPR compliance without competitive cost disadvantage.

### Root Cause: One-Shot vs. Adaptive Search

Claude's built-in `web_search` tool is **iterative and adaptive** — it issues multiple searches, evaluates what it finds, and decides whether to dig deeper or pivot to a different angle before synthesizing. This allows it to follow threads: finding a partner name in one result and then searching for that specific partnership.

The Tavily pipeline is **one-shot**: the query planner generates 3–5 queries upfront with no visibility into what those queries return. There is no mechanism to detect a gap and issue a follow-up search. All search planning happens before any results are seen.

### Improvements Applied (Options 1 and 2)

**Option 1 — Sonnet query planner:** Upgraded the query planner model from `claude-haiku-4-5` to `claude-sonnet-4-6`. Sonnet generates more targeted and diverse query sets, including angle coverage (ESG filings, trade press, partner announcements) that Haiku sometimes collapsed into near-duplicate queries.

**Option 2 — Tavily advanced depth:** Upgraded `search_depth` from `"basic"` to `"advanced"`. Advanced depth causes Tavily to crawl linked pages from top results rather than returning only top-level snippets, improving the chance of surfacing partnership announcements and sustainability report details buried in subpages.

The query planner prompt was also updated to explicitly request queries targeting:
- Retail or supply chain partnerships related to sustainability
- Publicly announced circular economy pilots

### Option 3 — Agentic Reflect-then-Search Loop (implemented)

After round 1, a dedicated **reflector** LLM (`prompts/reflector_prompt.md`) receives all collected results and returns one of two JSON decisions:

```json
{"action": "done"}
{"action": "search_again", "queries": ["specific query 1", "specific query 2"]}
```

If `search_again`, up to 3 targeted follow-up queries run against Tavily, deduplicated against prior URLs, and the reflector fires again on the updated results. This loop repeats up to `MAX_ROUNDS = 3` total rounds — meaning the reflector can fire twice before synthesis is forced. The Python code falls back to `done` if the reflector returns malformed output, so it can never block synthesis.

This makes the research pipeline a genuine **Observe → Reflect → Plan → Act** loop rather than a fixed sequence. The reflector is prompted to return `done` for obscure or private organizations where further searching is unlikely to help, keeping latency low for the common case.

### Option 4 — Parent Company Search Expansion (implemented)

The query planner now identifies whether the organization is a subsidiary and generates **two separate query sets**: one for the brand, one for the parent company. Both run in round 1 and their results are merged before the reflector sees them.

This directly addresses the root cause of the Cape Cod / Ahold Delhaize miss: that article was indexed under Campbell's (the parent), not Cape Cod. The parent query pass surfaces ESG reports, supply chain partnerships, and regenerative agriculture pilots announced at the corporate level but applicable to the brand.

The interpreter is told the parent company name and instructed to note when a commitment comes from the parent level rather than the brand directly.

## Architecture

See [docs/architecture.md](docs/architecture.md) for full sequence and model interaction diagrams.

### Research Pipeline (agentic loop)

1. **Query Planning** — `claude-sonnet-4-6` reads `prompts/query_planner_prompt.md` and returns a JSON object with separate `brand_queries` (3–5) and `parent_queries` (2–4), plus the parent company name if one is identified.
2. **Round 1 Search** — Brand queries run first, then parent queries (if a parent was found). All results are merged and deduplicated by URL.
3. **Reflect** — `claude-sonnet-4-6` reads `prompts/reflector_prompt.md` and decides: `done` or `search_again` with 2–3 targeted follow-up queries. Fires up to twice (`MAX_ROUNDS = 3`).
4. **Follow-up Search** (conditional, up to 2 rounds) — Targeted queries run if gaps are found; results merge with prior rounds, deduplicated. Reflector fires again on the updated pool.
5. **Interpretation** — `claude-sonnet-4-6` reads `prompts/interpreter_prompt.md` and synthesizes all results into a `<research>` XML block with 5 structured answers and confidence ratings. Parent company name is injected into the user message.

### Concept Generation

Structured answers from research (or from the manual survey path) are passed to `claude-sonnet-4-6` with `prompts/system_prompt.md` and three RAG knowledge bases:
- Consumer Packaging Reuse cases
- Food Waste and Upcycling cases
- B2B Asset Sharing cases

### Visualization

Each concept can optionally generate a prototype image via `gemini-2.5-flash-image`, using a structured prompt built from `prompts/image_prompt.md` and concept-specific fields.

## Setup

Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
TAVILY_API_KEY=...
SECRET_KEY=...
FLASK_DEBUG=true
```

Install dependencies and run:

```bash
uv sync
uv run flask run
```

Test API connectivity:

```bash
uv run python test_apis.py
```
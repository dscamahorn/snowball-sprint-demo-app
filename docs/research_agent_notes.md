# Research Agent: Observations and Design Notes

These notes record why the research agent is built the way it is. They were written while comparing the Tavily-based pipeline against Claude's built-in web search on a real example.

## The observation

When researching **Cape Cod Chips (Amplify Snack Brands)**, the original Claude-native `web_search` tool surfaced a specific and recent detail: a partnership with **Ahold Delhaize** on a regenerative agriculture pilot (December 2024). The first Tavily-based pipeline did not reliably surface this level of specificity. Partner names, joint pilots, and dated announcements tended to be underrepresented in results.

This matters because question 4 of the research framework is explicitly an exclusion filter: what has the organization already announced? Missing existing programs leads the concept generator to propose things the client has already done, which undermines workshop credibility.

### Reference answers from the Claude web search run

**Q1. What does the organization make or do?**
Cape Cod makes premium kettle-cooked potato chips (Classic, Less Fat, Waves, Multipacks) via small-batch frying. Owned by Campbell's Company through the 2018 Snyder's-Lance acquisition. Production is consolidating from Hyannis (closing April 2026) into three plants in WI, NC, and PA.

**Q2. Where does waste, inefficiency, or end-of-life live in their value chain?**
Three clear hotspots: (1) chip bags are multilayer metallized film, not curbside recyclable and essentially unrecoverable at scale; (2) potato processing generates 15 to 40 percent peel and reject waste by mass plus spent frying oil; (3) Scope 3 agricultural emissions from potato farming are large and barely addressed (0.5 percent reduction toward a 25 percent target).

**Q3. What pressure is driving the need to change?**
Seven US states now have packaging EPR laws (Oregon went live July 2025, California SB 54 escalating). Frito-Lay already has compostable bags in market. Campbell's SBTi-approved targets are tied to executive compensation. Retail partners (Ahold Delhaize) are already running sustainability pilots with them directly.

**Q4. What circular territory have they already explored?**
Kettle Brand bag redesign cut plastic 43 percent. Multipacks moved to curbside-recyclable paperboard cartons. How2Recycle labels on all eligible packaging. At the Salem, Oregon Kettle plant: potato waste to dairy feed, spent oil to biodiesel. December 2024: a 1,000-acre regenerative agriculture pilot with Ahold Delhaize, explicitly naming Cape Cod chips as the output. No compostable or recyclable chip bag for Cape Cod specifically yet.

**Q5. What does a successful outcome look like?**
A curbside-recyclable or certified compostable chip bag. Scaled regenerative potato sourcing beyond the pilot. Full potato processing waste diversion across all plants. EPR compliance without competitive cost disadvantage.

## Root cause: one-shot versus adaptive search

Claude's built-in web search is iterative and adaptive. It issues multiple searches, evaluates what it finds, and decides whether to dig deeper or pivot before synthesizing. That lets it follow threads: finding a partner name in one result and then searching for that specific partnership.

The first Tavily pipeline was one-shot. The query planner generated three to five queries up front with no visibility into what those queries returned. There was no mechanism to detect a gap and issue a follow-up search.

## Improvements applied

**Sonnet query planner.** The planner moved from `claude-haiku-4-5` to `claude-sonnet-4-6`. Sonnet generates more targeted and diverse query sets, including angle coverage (ESG filings, trade press, partner announcements) that Haiku sometimes collapsed into near-duplicate queries. The planner prompt also asks explicitly for retail or supply chain sustainability partnerships and publicly announced circular economy pilots.

**Tavily advanced depth.** `search_depth` moved from `basic` to `advanced`. Advanced depth makes Tavily crawl linked pages from top results rather than returning only top-level snippets.

**Reflect-then-search loop.** After round one, a reflector prompt (`prompts/reflector_prompt.md`) receives the collected results and returns one of two JSON decisions:

```json
{"action": "done"}
{"action": "search_again", "queries": ["specific query 1", "specific query 2"]}
```

On `search_again`, up to three targeted follow-up queries run against Tavily, deduplicated against prior URLs. The total number of rounds is capped by `MAX_SEARCH_ROUNDS` in `app/research_agent.py` (currently 2, so the reflector fires once). The code falls back to `done` if the reflector returns malformed output, so it can never block synthesis. The reflector is prompted to return `done` for obscure or private organizations where further searching is unlikely to help.

**Parent company expansion.** The query planner identifies whether the organization is a subsidiary and generates two query sets: one for the brand, one for the parent. Both run in round one and are merged before the reflector sees them. This directly addresses the Cape Cod miss: the Ahold Delhaize article was indexed under Campbell's, the parent. The interpreter is told the parent company name and asked to note when a commitment comes from the parent level rather than the brand.

# Product Requirements: Circular Concept

## Purpose

Help a workshop facilitator or sustainability lead go from "here is an organization" to "here are several prototype-ready circular economy concepts" in one sitting. The concepts must be grounded in real case studies and must not repeat things the organization has already done.

## Users

- A consultant or facilitator preparing a circular economy workshop for a client.
- A sustainability or innovation lead exploring options for their own organization.

## Core requirements

1. Capture the five framing questions (what they make, where waste lives, what pressure drives change, what they have already tried, what success looks like), either by hand or by researching the organization on the web.
2. Let the user review and edit every answer before generation, with a visible confidence rating on research-drafted answers.
3. Generate between one and eight structured concepts, each with a mechanic, target user, prototype sentence, assumptions to test, and cited case studies from the knowledge bases.
4. Show progress while the model works, since generation can take minutes.
5. Optionally illustrate any concept as a single image in the Terra visual style.
6. Follow the Terra design system and be usable with a keyboard and screen reader.

## Out of scope for now

- User accounts, saving sessions, or sharing results by link.
- Editing the knowledge bases from the UI.
- Running more than one server worker (results are cached in process memory).

## Milestones

Each milestone ends with something that runs and can be seen working.

### Completed

- [x] **M1. Survey to concepts.** Five-step survey, review page, single blocking call to Claude, concepts page with accordion and favorites.
- [x] **M2. Structured output.** System prompt returns `<response>` XML; parser replaces regex splitting; assumptions and citations rendered as lists.
- [x] **M3. Knowledge bases.** Three RAG files (consumer packaging reuse, food waste upcycling, B2B asset sharing) appended to every request, with a controlled vocabulary registry for authoring.
- [x] **M4. Research agent.** Plan, search, reflect, interpret loop over Tavily and Claude, streaming search progress to the home page, pre-filling the review page with confidence badges.
- [x] **M5. Streaming generation.** Per-concept progress bars driven by server-sent events; results handed to the concepts page through an in-memory cache.
- [x] **M6. Visualize prototype.** Gemini image generation from structured image fields plus a style reference picture.
- [x] **M7. Analytics.** Optional PostHog product events and AI observability behind one switch.
- [x] **M8. Standards alignment (September 2026).** Code rewritten for readability (spelled-out names, named constants, no comprehensions or tuple returns, docstrings everywhere), routes split by flow, JavaScript moved to `static/js` in plain style, ARIA on every interactive element, Prettier and ESLint configured, dev container added, docs rewritten, em-dashes removed.

### Next

- [ ] **M9. Python tests.** Add pytest with unit tests for `parser.py`, `research_agent.py` helpers, `form_helpers.py`, and `result_cache.py`, plus route tests using Flask's test client. Deliverable: `uv run pytest` passes and is documented in the README.
- [ ] **M10. Research progress detail.** Show the actual search queries streaming in on the home page overlay instead of only the cycling messages. Deliverable: the overlay lists each query as it runs.
- [ ] **M11. Export.** Download the generated concepts as Markdown or PDF for the workshop deck. Deliverable: an Export button on the concepts page.

## Open decisions

- Whether to keep the no-JavaScript fallback route `/generate`, which renders the concepts page without progress feedback. It costs little and is kept for now.
- Whether the GitHub repository should be private, per the global standard. This is the owner's call; see the README for the command.

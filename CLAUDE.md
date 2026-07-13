# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the dev server:**
```bash
uv run flask run
```
`FLASK_DEBUG=true` is set in `.env` — hot reload is active.

**Install / sync dependencies:**
```bash
uv sync
```

**Test API connectivity:**
```bash
uv run python test_apis.py
```

**One-off dependency add:**
```bash
uv add <package>
```

There are no lint or test commands configured beyond `test_apis.py`.

## Architecture

Flask app structured as a package (`app/`) with Jinja2 templates. No blueprints, no database. State lives only in the Flask session (cookie-backed, keyed by `SECRET_KEY`).

**Package layout:**
- `app/__init__.py` — Flask factory (`create_app()`), exports `app` instance for `flask run`
- `app/routes.py` — all route handlers; imports path constants from `config.py`
- `app/parser.py` — `_parse_llm_output()`, isolated from Flask
- `config.py` — env var loading and `Path` constants for all file locations
- `app/templates/` — Jinja2 templates
- `app/static/` — static assets (CSS, JS)

**Request flow:**
1. `/` → `index.html` — landing page with Begin button
2. `/survey` → `survey.html` — 5-step Alpine.js typeform; answers stored in `session["answers"]`
3. `/submit` (POST) → `review.html` — user reviews and edits answers inline; sets concept count (1–8)
4. `/generate` (POST) → calls Anthropic API → parses output → `concepts.html`
5. `/start-over` → clears session, redirects to `/`

**LLM output parsing (`app/parser.py`):**
The Anthropic response is structured plain text delimited by `---` separators. The parser:
- Extracts **profile analysis** via regex for `**Profile analysis:**`, with a fallback to text before the first `---` or `###`
- Strips any trailing citation bullet lines from the profile block
- Splits on `\n+---+\n+` to get per-concept sections (each has a `### Concept N: Title` header)
- Extracts named fields with `**Field name:**` regex per section (case-insensitive)
- Captures **themes** (closing summary) from the final section after the last concept

Returns `(profile, themes, concepts)` — all three are passed to `concepts.html`.

**System prompt and RAG:**
- `prompts/system_prompt.md` — the full system prompt loaded from disk on every `/generate` call
- `knowledge/RAG_consumer_packaging_reuse.xml` — consumer packaging reuse cases, appended to every user message
- `knowledge/RAG_food_waste_upcycling.xml` — food waste and upcycling cases, appended to every user message
- `knowledge/rag_registry_circular_economy.md` — controlled vocabulary and schema reference (not sent to LLM; used for authoring consistency)

All files are read at request time (no caching), so edits take effect immediately without restarting Flask.

## Frontend Stack

All frontend dependencies are loaded via CDN — no build step:
- **Tailwind CSS** Play CDN with custom Terra color tokens configured inline in `base.html`
- **DaisyUI v4** (`daisyui@4/dist/full.min.css`) — must load *before* Tailwind
- **Alpine.js 3.x** — drives survey step logic, inline editing on review page, favorites/accordion on concepts page
- **HTMX 2.0.4** — available but minimally used

## Design System (Terra)

Defined in `instructions/DESIGN.md`. Key tokens used throughout templates:
- `terra-green` (#4a7c59) — actions, headings, interactive states
- `terra-cream` (#faf6f0) — page background
- `terra-amber` (#705c30) — accent labels, badges
- `terra-muted` (#8a8278) — secondary text
- `terra-border` (#ddd8d0) — card and input borders
- `shadow-terra` — `0 4px 20px rgba(46,50,48,0.06)`
- Typography: Literata (serif, headlines) + Nunito Sans (body)
- All buttons/cards use `rounded-[12px]`; inputs use cream background with green focus ring

## Environment Variables

See `.env.example`. Required in `.env`:
```
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...       # not used in main app flow; only in test_apis.py
SECRET_KEY=...           # Flask session signing key
FLASK_DEBUG=true
```

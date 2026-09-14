# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. The global rules in `~/.claude/CLAUDE.md` apply in full; this file only adds what is specific to this project.

## Commands

**Run the dev server:**
```bash
uv run flask run
```
`FLASK_DEBUG=true` in `.env` turns on hot reload. `FLASK_RUN_PORT=5050` in `.env` picks the port; 5000 is avoided because macOS reserves it for AirPlay Receiver. Open http://127.0.0.1:5050.

**Install or sync dependencies:**
```bash
uv sync
```

**Test API connectivity:**
```bash
uv run python test_apis.py
```

**Add a Python dependency:**
```bash
uv add <package>
```

**Deploy to the droplet** (needs `deploy.env`, copied from `deploy.env.example`, and the 1Password SSH agent):
```bash
./deploy.sh
```
Pulls `main` on the droplet, runs `uv sync`, restarts the `circular-concept` systemd service, and checks `/health`. One-time droplet setup is `server/setup-site.sh`; gunicorn, systemd, and Apache config live in `server/`.

**Lint and format the browser JavaScript** (needs `npm install` first, which the dev container does automatically):
```bash
npm run lint
npm run format
```

There is no Python test suite yet. `test_apis.py` only checks that the three external APIs answer.

## Architecture

Flask app structured as a package (`app/`) with Jinja2 templates and small Alpine.js components. No database. Per-visitor state lives in the Flask session cookie (signed with `SECRET_KEY`); results too large for the cookie wait briefly in an in-memory cache.

**Top level:**
- `config.py`: loads `.env`, and holds every model name, tunable limit, and file path. Change settings here, not in the modules.
- `app/__init__.py`: Flask factory `create_app()`, exports the `app` object that `flask run` imports.
- `test_apis.py`: connectivity check for Anthropic, Gemini, and Tavily.

**Routes (`app/routes*.py`):** `routes.py` only calls the three register functions.
- `routes_pages.py`: home, survey, review, start over, `/ping`, `/health`.
- `routes_research.py`: `/research-stream`, the research agent's server-sent events stream.
- `routes_concepts.py`: `/generate` (no-JavaScript fallback), `/generate-stream`, `/concepts`, `/visualize`.

**Supporting modules (`app/`):**
- `llm.py`: concept generation calls to Claude, blocking and streaming.
- `research_agent.py`: plan, search, reflect, interpret loop using Claude and Tavily.
- `image_gen.py`: builds the image prompt and calls Gemini for the prototype picture.
- `parser.py`: turns the `<response>` XML from Claude into a dictionary of concepts.
- `rag.py`: loads the three knowledge files into one labeled string.
- `analytics.py`: PostHog capture layer; every function is a no-op when analytics are off.
- `result_cache.py`: `ResultCache` plus the two shared instances the routes use.
- `server_sent_events.py`: SSE formatting and the streaming Flask response.
- `form_helpers.py`: reads survey answers and the concept count out of a form.

**Frontend (`app/templates/`, `app/static/js/`):** each page's Alpine component lives in its own file under `static/js` and is loaded from that page's `{% block scripts %}`. `sse_reader.js` is shared by the home and review pages. Templates pass server data to the components through small inline `<script>` blocks using the `tojson` filter.

**Request flow:**
1. `/` shows two paths: research an organization, or take the survey.
2. Research path: `POST /research-stream` streams progress, stores the drafted answers in `research_result_cache`, then the browser goes to `/review`, which moves them into the session.
3. Survey path: `/survey` (5 steps) posts to `/submit`, which saves answers to the session and redirects to `/review`.
4. `/review`: edit answers, pick a concept count (bounded by `config.MIN_CONCEPT_COUNT` and `MAX_CONCEPT_COUNT`), then `POST /generate-stream` streams per-concept progress and stores the parsed result in `concept_result_cache`.
5. `/concepts` takes the cached result (read once) and renders the accordion. `POST /visualize` returns a base64 PNG for one concept.
6. `/start-over` clears the session.

**Why generators appear in this code:** streaming requires the route to hand chunks to the browser as they arrive. `stream_concepts()`, `stream_research_org()`, and the inner `*_events()` functions in the routes use `yield` for that reason and say so in their docstrings. Everywhere else, plain functions that return lists or dictionaries are used.

**Why the app must run with one worker:** the two result caches live in process memory. With more than one gunicorn worker, a result stored by one worker is invisible to the next request. `server/gunicorn.conf.py` sets one worker with several threads, which share memory, so the caches keep working while several visitors are served at once.

## Prompts and knowledge

- `prompts/system_prompt.md`: concept generator system prompt. Tells Claude to answer in `<response>` XML.
- `prompts/query_planner_prompt.md`, `reflector_prompt.md`, `interpreter_prompt.md`: the three research agent prompts.
- `prompts/image_prompt.md`: Gemini image prompt with `[PLACEHOLDER]` tokens; everything from `### Integration Mapping` onward is developer notes and is stripped before sending.
- `knowledge/RAG_*.xml`: three case study knowledge bases appended to every concept request.
- `knowledge/rag_registry_circular_economy.md`: controlled vocabulary for authoring the XML files (not sent to the model).
- `knowledge/image_reference.jpg`: style reference sent to Gemini with every image request.

All prompt and knowledge files are read from disk at request time, so edits take effect without restarting Flask. Two prompt lines intentionally contain an em-dash character because they tell the model not to use one.

## Frontend stack

Loaded from CDNs in `base.html`, no build step:
- Tailwind CSS Play CDN with the Terra color tokens configured inline.
- DaisyUI v4 (`daisyui@4/dist/full.min.css`), loaded before Tailwind.
- Alpine.js 3.x, loaded with `defer` so the component functions in `static/js` exist first.

Prettier and ESLint (flat config in `eslint.config.js`) cover `app/static/js` only. Vite is deliberately not used because there is nothing to bundle.

## Design system (Terra)

Defined in `docs/DESIGN.md`. Tokens used throughout the templates:
- `terra-green` (#4a7c59): actions, headings, interactive states
- `terra-cream` (#faf6f0): page background; `terra-cream-dark` (#f0ebe2) for hover fills
- `terra-amber` (#705c30): accent labels, badges
- `terra-muted` (#8a8278): secondary text
- `terra-border` (#ddd8d0): card and input borders
- `shadow-terra`: `0 4px 20px rgba(46,50,48,0.06)`
- Typography: Literata (serif headlines) and Nunito Sans (body)
- Buttons and cards use `rounded-[12px]`; inputs use a cream background with a green focus ring

Every interactive element carries ARIA attributes (labels on inputs, `aria-expanded` on the accordion, `aria-pressed` on toggles, `aria-live` on streaming status). Keep that up when adding UI.

## Environment variables

See `.env.example`. Required in `.env`:
```
ANTHROPIC_API_KEY=...    # all Claude calls
GEMINI_API_KEY=...       # prototype image generation
TAVILY_API_KEY=...       # web search for the research agent
SECRET_KEY=...           # Flask session signing key
FLASK_DEBUG=true
FLASK_RUN_PORT=5050
```
Optional PostHog analytics: `POSTHOG_ENABLED=true`, `POSTHOG_API_KEY`, `POSTHOG_HOST`.

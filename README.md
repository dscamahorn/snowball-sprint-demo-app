# Circular Concept

A Flask app that generates tailored circular economy business model concepts for an organization. It combines an optional web research agent, three case study knowledge bases (RAG), Claude for ideation, and Gemini for a prototype illustration of each concept.

## How it works

1. **Start** on the home page. Either enter an organization name and let the research agent draft the five survey answers, or take the five-question survey yourself.
2. **Review** the answers, edit anything, and pick how many concepts to generate (1 to 8).
3. **Generate.** Claude reads the answers plus the knowledge bases and streams back structured concepts. The page shows per-concept progress while it works.
4. **Explore** the concepts as an accordion, mark favorites, and optionally click "Visualize Prototype" to have Gemini draw the loop.

See [docs/architecture.md](docs/architecture.md) for the sequence diagram and model interaction map, and [docs/research_agent_notes.md](docs/research_agent_notes.md) for why the research agent is built the way it is. Milestones live in [PRD.md](PRD.md).

## Setup

**Recommended: open in the dev container.** Open the folder in VS Code and choose "Reopen in Container". The container installs Python dependencies with `uv sync` and JavaScript tooling with `npm install` on first build. Everything (editing, terminal, Flask, Claude Code) runs inside the container.

**Configure keys.** Copy `.env.example` to `.env` and fill in:

| Variable | Required | Used for |
|---|---|---|
| `ANTHROPIC_API_KEY` | yes | all Claude calls (research agent and concept generation) |
| `GEMINI_API_KEY` | yes | prototype image generation |
| `TAVILY_API_KEY` | yes | web search for the research agent |
| `SECRET_KEY` | yes | signing the Flask session cookie; any long random string |
| `FLASK_DEBUG` | no | `true` turns on hot reload for local development |
| `FLASK_RUN_PORT` | no | dev server port, `5050` because macOS reserves 5000 for AirPlay Receiver |
| `POSTHOG_ENABLED` | no | `true` turns on PostHog analytics and AI observability |
| `POSTHOG_API_KEY` | no | PostHog project key, only read when analytics are enabled |
| `POSTHOG_HOST` | no | PostHog host, defaults to `https://us.i.posthog.com` |

**Without the container**, install [uv](https://docs.astral.sh/uv/) and run `uv sync` from the project root. Node is only needed if you want to run Prettier and ESLint.

## Run locally

```bash
uv run flask run
```

Then open http://127.0.0.1:5050. Check that the API keys are seen with http://127.0.0.1:5050/health.

The server uses port 5050 instead of Flask's default 5000 because macOS reserves 5000 for AirPlay Receiver, which answers with a blank page.

Test connectivity to the three external services:

```bash
uv run python test_apis.py
```

Lint and format the browser JavaScript:

```bash
npm run lint
npm run format
```

## Deploy

The app is served with gunicorn in production. It must run with a single worker because generated results are handed between requests through an in-memory cache:

```bash
uv run gunicorn --workers 1 --bind 0.0.0.0:8000 app:app
```

Set the same environment variables as in `.env` on the host, with `FLASK_DEBUG` left unset and a real `SECRET_KEY`.

## Project layout

```
app/
  __init__.py           Flask factory
  routes.py             wires the three route modules
  routes_pages.py       home, survey, review, health
  routes_research.py    research agent stream
  routes_concepts.py    concept generation, concepts page, visualize
  llm.py                Claude concept generation (blocking and streaming)
  research_agent.py     plan, search, reflect, interpret loop
  image_gen.py          Gemini image prompt and call
  parser.py             XML reply to concept dictionaries
  rag.py                loads the knowledge files
  analytics.py          PostHog capture layer
  result_cache.py       in-memory hand-off between requests
  server_sent_events.py SSE helpers
  form_helpers.py       reads form fields
  templates/            Jinja2 pages
  static/js/            one Alpine.js component per page
config.py               settings, model names, limits, file paths
prompts/                prompt files sent to the models
knowledge/              RAG case study files and the image style reference
docs/                   design system, architecture, research notes
```

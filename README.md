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

## Deploying

The live site is https://circular.workshopper.ai, a DigitalOcean droplet. Apache answers on ports 80 and 443 and forwards every request to gunicorn, which runs the Flask app as a systemd service. Everything for the droplet lives in [server/](server/).

One-time, on the droplet: clone the repo into `/var/www/circular.workshopper.ai`, copy `.env.example` to `.env` and fill in the keys, then run from that folder:

```bash
sh server/setup-site.sh circular.workshopper.ai you@example.com
```

It installs Apache and certbot, installs uv and the Python dependencies, installs the `circular-concept` gunicorn systemd service, installs the Apache virtual host, and requests the HTTPS certificate. It also retires the earlier hand-made setup: the `flask_subdomain` service that ran the app from `/var/www/circular-concept` is stopped, and the domain's old virtual host files are kept under a backup name. Set the Cloudflare A record to DNS only first so certbot can reach the droplet directly.

The first time, move the existing clone instead of cloning again so the `.env` with the keys comes along. The virtual environment has to be rebuilt after a move because it contains absolute paths; the setup script does that:

```bash
mv /var/www/circular-concept /var/www/circular.workshopper.ai
rm -rf /var/www/circular.workshopper.ai/.venv
cd /var/www/circular.workshopper.ai
```

Every time after that, from the container's terminal or from the Mac itself. VS Code passes the Mac's SSH agent into the container, so the Mac's `~/.zshrc` must point `SSH_AUTH_SOCK` at 1Password's agent socket (1Password's documented one-liner); otherwise the container gets Apple's empty agent and the droplet refuses the connection.

```bash
cp deploy.env.example deploy.env   # once; check the host, user, and app folder
./deploy.sh
```

It pulls `main` on the droplet, syncs Python dependencies, restarts the gunicorn service, and checks the live `/health` page. The `.env` file with the API keys stays on the droplet and is never copied. Details: [PRD.md](PRD.md) Deployment section and the diagram in [docs/architecture.md](docs/architecture.md).

Gunicorn runs with one worker process and several threads (see [server/gunicorn.conf.py](server/gunicorn.conf.py)). One process is required because generated results are handed between requests through an in-memory cache; threads let that one process serve several visitors at once.

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
server/                 droplet setup script, gunicorn config, systemd unit, Apache vhost
deploy.sh               ships main to the droplet (reads deploy.env)
```

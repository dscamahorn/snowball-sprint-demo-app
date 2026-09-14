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

## Deployment

The app runs on one DigitalOcean droplet at https://circular.workshopper.ai. The pieces:

- **Repository** cloned directly at `/var/www/circular.workshopper.ai` on the droplet. Unlike dodge.scamahorn.me there is no `app` and `public_html` split, because Apache serves no built files for this site. `.env` with the API keys and `SECRET_KEY` lives there and is never copied by the deploy script. The droplet hosts several other sites, so the setup script only ever touches Apache files named after this domain.
- **gunicorn** serves the Flask app on `127.0.0.1:8000` as the `circular-concept` systemd service. One worker process (the result caches are in memory) with eight threads (so one visitor's long stream does not block the others). Settings in `server/gunicorn.conf.py`.
- **Apache** answers on ports 80 and 443, serves `app/static` straight from disk, and proxies every other request to gunicorn. The proxy timeout is raised to 600 seconds so the research and generation streams are not cut off. Virtual host template in `server/apache-site.conf`.
- **certbot** provides the Let's Encrypt certificate and the HTTP to HTTPS redirect.
- **DNS** at Cloudflare, A record pointing at the droplet's IP, set to DNS only.

`server/setup-site.sh` does the one-time install. `deploy.sh` on the Mac or in the dev container does every later update: pull `main`, `uv sync`, restart the service, check `/health`. SSH uses the key held in 1Password's agent.

History: before September 2026 the app ran from `/var/www/circular-concept` as a hand-made `flask_subdomain` service on the same port, with the first commit of the repo. The setup script retires that service and replaces the domain's virtual host files, keeping backups. Worth doing later: a non-root user for the service.

## Open decisions

- Whether to keep the no-JavaScript fallback route `/generate`, which renders the concepts page without progress feedback. It costs little and is kept for now.
- Repository visibility: decided September 2026. This repo stays public, as an intentional exception to the private-by-default standard.

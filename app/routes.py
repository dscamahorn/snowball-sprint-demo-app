"""Wires every route module onto the Flask app.

The routes are split by flow so each file stays short:
  routes_pages.py     plain pages: home, survey, review, start over, health
  routes_research.py  the research agent stream
  routes_concepts.py  concept generation, the concepts page, and visualization
"""

from app.routes_concepts import register_concept_routes
from app.routes_pages import register_page_routes
from app.routes_research import register_research_routes


def register_routes(app):
    """Attach all route handlers to the app. Called once from create_app()."""
    register_page_routes(app)
    register_research_routes(app)
    register_concept_routes(app)

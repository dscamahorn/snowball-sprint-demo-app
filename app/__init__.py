"""Creates the Flask app. `flask run` imports the `app` object defined at the bottom."""

import uuid

from flask import Flask, session

import config
from app import analytics


def create_app():
    """Build and configure the Flask application."""
    flask_app = Flask(__name__, template_folder="templates", static_folder="static")
    flask_app.secret_key = config.SECRET_KEY

    # Flask runs @before_request functions before every request. This one gives
    # each visitor a random id, stored in their session cookie, so analytics can
    # tell visitors apart without knowing who they are.
    @flask_app.before_request
    def ensure_distinct_id():
        """Give every visitor a random id in their session cookie."""
        session.setdefault("distinct_id", str(uuid.uuid4()))

    # A context processor adds variables to every template automatically, so
    # base.html can read the PostHog settings without each route passing them.
    @flask_app.context_processor
    def inject_analytics_settings():
        """Make the PostHog settings available to every template."""
        return {
            "distinct_id": session.get("distinct_id"),
            "posthog": analytics.client_config(),
        }

    # Imported here rather than at the top of the file because the route
    # modules import from this package, and importing them before the package
    # is set up would create a circular import.
    from app.routes import register_routes
    register_routes(flask_app)

    return flask_app


app = create_app()

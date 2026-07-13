import uuid

from flask import Flask, session
import config
from app import analytics


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = config.SECRET_KEY

    @app.before_request
    def _ensure_distinct_id():
        session.setdefault("distinct_id", str(uuid.uuid4()))

    @app.context_processor
    def _inject_analytics():
        return {
            "distinct_id": session.get("distinct_id"),
            "posthog":     analytics.client_config(),
        }

    from app.routes import register_routes
    register_routes(app)

    return app


app = create_app()
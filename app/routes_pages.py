"""Plain page routes: home, survey, review, start over, and health checks."""

from flask import jsonify, redirect, render_template, request, session, url_for

import config
from app import analytics
from app.form_helpers import read_answers_from_form
from app.result_cache import research_result_cache

# Everything the app stores in the session cookie for one run through the flow.
FLOW_SESSION_KEYS = ["answers", "org_name", "answer_confidences", "stream_key", "research_key"]


def clear_flow_session():
    """Forget the current run so the user starts fresh."""
    for session_key in FLOW_SESSION_KEYS:
        session.pop(session_key, None)


def register_page_routes(app):
    """Attach the page routes to the app.

    Flask requires the @app.route decorator to connect a URL to a function,
    which is why each handler is defined inside this function.
    """

    @app.route("/")
    def index():
        """Home page with the research and survey paths."""
        return render_template("index.html")

    @app.route("/survey")
    def survey():
        """The five-step survey, pre-filled with any answers already in the session."""
        existing_answers = session.get("answers", {})
        return render_template("survey.html", existing=existing_answers)

    @app.route("/begin-survey")
    def begin_survey():
        """Clear the previous run and send the user to the survey."""
        analytics.capture_event(session.get("distinct_id"), "begin survey")
        clear_flow_session()
        return redirect(url_for("survey"))

    @app.route("/submit", methods=["POST"])
    def submit():
        """Save the survey answers and move to the review page."""
        # The survey form posts here. Save the answers and move to the review page.
        session["answers"] = read_answers_from_form(request.form)
        session.pop("org_name", None)
        session.pop("answer_confidences", None)
        return redirect(url_for("review"))

    @app.route("/review")
    def review():
        """Show the answers for editing. Picks up research results if any are waiting."""
        # When the research agent just finished, its result is waiting in the
        # cache under the key stored in the session. Move it into the session.
        research_key = session.get("research_key")
        arrived_from_research = False
        if research_key and research_result_cache.contains(research_key):
            research_data = research_result_cache.take(research_key)
            session["answers"] = research_data["answers"]
            session["org_name"] = research_data["org_name"]
            session["answer_confidences"] = research_data["confidences"]
            session.pop("research_key", None)
            arrived_from_research = True

        answers = session.get("answers")
        if not answers:
            return redirect(url_for("index"))

        analytics.capture_event(
            session.get("distinct_id"),
            "review",
            {"from_research": arrived_from_research},
        )
        return render_template(
            "review.html",
            answers=answers,
            org_name=session.get("org_name"),
            confidences=session.get("answer_confidences", {}),
            min_concept_count=config.MIN_CONCEPT_COUNT,
            max_concept_count=config.MAX_CONCEPT_COUNT,
            default_concept_count=config.DEFAULT_CONCEPT_COUNT,
        )

    @app.route("/start-over")
    def start_over():
        """Clear the session and return to the home page."""
        clear_flow_session()
        return redirect(url_for("index"))

    @app.route("/ping")
    def ping():
        """Tiny liveness check that returns plain text."""
        return "pong: server is alive"

    @app.route("/health")
    def health():
        """JSON health check that also reports which API keys are configured."""
        return jsonify({
            "status": "ok",
            "anthropic_key_set": bool(config.ANTHROPIC_API_KEY),
            "gemini_key_set": bool(config.GEMINI_API_KEY),
            "tavily_key_set": bool(config.TAVILY_API_KEY),
        })

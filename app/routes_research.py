"""The research agent route: streams progress to the browser while it works."""

import uuid

from flask import jsonify, request, session

from app import analytics
from app.research_agent import stream_research_org
from app.result_cache import research_result_cache
from app.server_sent_events import format_sse_event, make_sse_response


def register_research_routes(app):
    """Attach the research route to the app."""

    @app.route("/research-stream", methods=["POST"])
    def research_stream():
        """Run the research agent for an organization and stream its progress as SSE."""
        org_name = request.form.get("org_name", "").strip()
        industry = request.form.get("industry", "").strip()
        if not org_name:
            return jsonify({"error": "Organization name is required"}), 400

        # The finished result is stored under this key; the review page picks it up.
        research_key = str(uuid.uuid4())
        session["research_key"] = research_key

        distinct_id = session.get("distinct_id")
        trace_id = str(uuid.uuid4())
        analytics.capture_event(distinct_id, "research", {"org_name": org_name, "industry": industry})

        def research_events():
            """Generator: forwards the agent's progress as SSE messages."""
            try:
                for event in stream_research_org(org_name, industry, distinct_id, trace_id):
                    if event["type"] == "search":
                        yield format_sse_event({"type": "search", "query": event["query"]})
                    elif event["type"] == "result":
                        research_result_cache.store(research_key, event["data"])
                        yield format_sse_event({"type": "done"})
            except Exception as error:
                # The stream has already started, so we cannot send an HTTP error
                # code. Any failure (network, API, parsing) is reported as an
                # error event for the page to display instead.
                yield format_sse_event({"type": "error", "message": str(error)})

        return make_sse_response(research_events())

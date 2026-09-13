"""Helpers for server-sent events (SSE).

SSE is a simple way for the server to push a stream of small messages to the
browser over one long-lived HTTP response. Each message is a line that starts
with "data: " followed by a blank line. The browser reads them as they arrive,
which is how the loading screens show live progress.
"""

import json

from flask import Response, stream_with_context

# These headers stop proxies and browsers from buffering the stream, so each
# event reaches the page as soon as it is sent.
SSE_RESPONSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


def format_sse_event(payload: dict) -> str:
    """Turn a dictionary into one SSE message string."""
    return "data: " + json.dumps(payload) + "\n\n"


def make_sse_response(event_generator) -> Response:
    """Wrap a generator of SSE message strings in a streaming Flask response.

    stream_with_context keeps the Flask request context (including the session)
    available while the generator is still producing events.
    """
    return Response(
        stream_with_context(event_generator),
        mimetype="text/event-stream",
        headers=SSE_RESPONSE_HEADERS,
    )

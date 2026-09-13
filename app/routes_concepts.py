"""Concept generation routes, the concepts page, and the visualize action."""

import base64
import uuid

from flask import jsonify, redirect, render_template, request, session, url_for

import config
from app import analytics
from app.form_helpers import read_answers_from_form, read_concept_count_from_form
from app.image_gen import build_image_prompt, call_gemini_image
from app.llm import generate_concepts, stream_concepts
from app.parser import parse_concept_output
from app.rag import load_rag_context
from app.result_cache import concept_result_cache
from app.server_sent_events import format_sse_event, make_sse_response

# The model wraps each concept in these tags. Counting them as the reply
# streams in tells us how many concepts have started and finished.
CONCEPT_OPEN_TAG_START = '<concept number="'
CONCEPT_CLOSE_TAG = "</concept>"


def register_concept_routes(app):
    """Attach the concept routes to the app."""

    @app.route("/generate", methods=["POST"])
    def generate():
        """Fallback for browsers without JavaScript: wait for the whole reply, then render."""
        answers = read_answers_from_form(request.form)
        concept_count = read_concept_count_from_form(request.form)

        distinct_id = session.get("distinct_id")
        trace_id = str(uuid.uuid4())
        analytics.capture_event(distinct_id, "generate concepts", {"n_concepts": concept_count})

        try:
            system_prompt = config.load_text_file(config.SYSTEM_PROMPT_FILE)
            rag_context = load_rag_context()
            llm_text = generate_concepts(
                answers, concept_count, system_prompt, rag_context, distinct_id, trace_id
            )
        except Exception as error:
            # Any failure (missing file, network, API) shows the error page
            # instead of a crash, with the message so the user can report it.
            return render_template("error.html", message=str(error)), 500

        parsed = parse_concept_output(llm_text)
        return render_template(
            "concepts.html",
            profile_analysis=parsed["profile_analysis"],
            themes=parsed["themes"],
            concepts=parsed["concepts"],
            n_concepts=concept_count,
        )

    @app.route("/generate-stream", methods=["POST"])
    def generate_stream():
        """Main path: stream progress events while the model writes, then signal done."""
        answers = read_answers_from_form(request.form)
        concept_count = read_concept_count_from_form(request.form)
        session["answers"] = answers

        # The parsed result is stored under this key; the concepts page picks it up.
        stream_key = str(uuid.uuid4())
        session["stream_key"] = stream_key

        distinct_id = session.get("distinct_id")
        trace_id = str(uuid.uuid4())
        analytics.capture_event(distinct_id, "generate concepts", {"n_concepts": concept_count})

        def concept_events():
            """Generator: watches the streamed reply and reports each concept's start and end."""
            try:
                system_prompt = config.load_text_file(config.SYSTEM_PROMPT_FILE)
                rag_context = load_rag_context()
            except OSError as error:
                # A prompt or knowledge file could not be read from disk.
                yield format_sse_event({"type": "error", "message": str(error)})
                return

            accumulated_text = ""
            concept_starts_reported = 0
            concept_ends_reported = 0

            try:
                text_chunks = stream_concepts(
                    answers, concept_count, system_prompt, rag_context, distinct_id, trace_id
                )
                for text_chunk in text_chunks:
                    accumulated_text += text_chunk

                    # Report every new opening tag we have not announced yet.
                    concept_starts_seen = accumulated_text.count(CONCEPT_OPEN_TAG_START)
                    while concept_starts_reported < concept_starts_seen:
                        concept_starts_reported += 1
                        yield format_sse_event({"type": "concept_start", "number": concept_starts_reported})

                    # Same for closing tags.
                    concept_ends_seen = accumulated_text.count(CONCEPT_CLOSE_TAG)
                    while concept_ends_reported < concept_ends_seen:
                        concept_ends_reported += 1
                        yield format_sse_event({"type": "concept_end", "number": concept_ends_reported})
            except Exception as error:
                # The stream has already started, so an HTTP error code is not
                # possible. Any API or network failure becomes an error event.
                yield format_sse_event({"type": "error", "message": str(error)})
                return

            parsed = parse_concept_output(accumulated_text)
            concept_result_cache.store(stream_key, {
                "profile_analysis": parsed["profile_analysis"],
                "themes": parsed["themes"],
                "concepts": parsed["concepts"],
                "n_concepts": concept_count,
            })
            yield format_sse_event({"type": "done"})

        return make_sse_response(concept_events())

    @app.route("/concepts")
    def concepts():
        """Show the concepts that the stream route left in the cache."""
        stream_key = session.get("stream_key")
        if not stream_key or not concept_result_cache.contains(stream_key):
            return redirect(url_for("index"))

        result = concept_result_cache.take(stream_key)
        return render_template(
            "concepts.html",
            profile_analysis=result["profile_analysis"],
            themes=result["themes"],
            concepts=result["concepts"],
            n_concepts=result["n_concepts"],
        )

    @app.route("/visualize", methods=["POST"])
    def visualize():
        """Draw a prototype image for one concept and return it as a data URL."""
        request_data = request.get_json(silent=True)
        if request_data is None:
            request_data = {}
        image_fields = request_data.get("image_fields")
        if not image_fields:
            return jsonify({"error": "No image fields provided"}), 400

        prompt = build_image_prompt(image_fields)
        if prompt is None:
            return jsonify({"error": "Could not parse prototype sentence"}), 422

        distinct_id = session.get("distinct_id")
        trace_id = str(uuid.uuid4())
        analytics.capture_event(distinct_id, "generate visual", {"concept": request_data.get("title")})

        try:
            png_bytes = call_gemini_image(prompt, distinct_id, trace_id)
        except Exception as error:
            # Gemini errors and refusals are reported back to the page as JSON.
            return jsonify({"error": str(error)}), 500

        # Browsers can show an image straight from a base64 "data URL", which
        # saves us from having to store the file anywhere.
        png_base64 = base64.b64encode(png_bytes).decode("utf-8")
        return jsonify({"image": "data:image/png;base64," + png_base64})

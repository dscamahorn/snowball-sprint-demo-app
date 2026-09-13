"""PostHog analytics and AI observability, behind a single on/off switch.

Every analytics call in the app goes through this module so the callers never
have to check whether analytics are turned on. When POSTHOG_ENABLED is false
in .env, or the PostHog key is missing, every function here does nothing.
"""

import atexit

from posthog import Posthog

import config

ENABLED = bool(config.POSTHOG_ENABLED and config.POSTHOG_API_KEY)

# One shared PostHog client for the whole process, or None when analytics
# are switched off.
posthog_client = None
if ENABLED:
    posthog_client = Posthog(config.POSTHOG_API_KEY, host=config.POSTHOG_HOST)
    # PostHog sends events in batches in the background. Flushing on exit
    # makes sure the last few events are delivered before the process ends.
    atexit.register(posthog_client.flush)


def capture_event(distinct_id, event_name, properties=None):
    """Record a product event such as "begin survey". Does nothing when analytics are off."""
    if posthog_client is None or not distinct_id:
        return
    if properties is None:
        properties = {}
    posthog_client.capture(distinct_id=distinct_id, event=event_name, properties=properties)


def capture_ai_generation(
    distinct_id,
    trace_id,
    model,
    provider,
    input_messages,
    output_messages,
    input_tokens,
    output_tokens,
    latency_seconds,
    is_stream=False,
):
    """Record one model call as a PostHog "$ai_generation" event.

    PostHog's AI observability feature expects property names that start with
    "$ai_", which is why the keys below look unusual.
    """
    if posthog_client is None or not distinct_id:
        return

    properties = {
        "$ai_trace_id": trace_id,
        "$ai_model": model,
        "$ai_provider": provider,
        "$ai_input": input_messages,
        "$ai_output_choices": output_messages,
        "$ai_input_tokens": input_tokens,
        "$ai_output_tokens": output_tokens,
        "$ai_latency": latency_seconds,
    }
    if is_stream:
        properties["$ai_stream"] = True

    posthog_client.capture(distinct_id=distinct_id, event="$ai_generation", properties=properties)


def client_config() -> dict:
    """Settings the browser-side PostHog snippet needs. Handed to every template."""
    posthog_key = config.POSTHOG_API_KEY
    if posthog_key is None:
        posthog_key = ""
    return {
        "enabled": ENABLED,
        "key": posthog_key,
        "host": config.POSTHOG_HOST,
    }

"""PostHog analytics + AI observability — the single guarded capture layer.

Every capture in the app goes through here so callers never branch on the
on/off state themselves. Analytics are master-switched by POSTHOG_ENABLED (and
require POSTHOG_API_KEY); when off, every function is a no-op that touches no
network.
"""
import atexit

from posthog import Posthog

import config

ENABLED = bool(config.POSTHOG_ENABLED and config.POSTHOG_API_KEY)

_client = None
if ENABLED:
    _client = Posthog(config.POSTHOG_API_KEY, host=config.POSTHOG_HOST)
    atexit.register(_client.flush)


def capture(distinct_id, event, properties=None):
    """Capture a product event. No-op when analytics are disabled."""
    if not _client or not distinct_id:
        return
    _client.capture(distinct_id=distinct_id, event=event, properties=properties or {})


def capture_ai_generation(
    distinct_id,
    *,
    trace_id,
    model,
    provider,
    input,
    output,
    input_tokens,
    output_tokens,
    latency,
    **extra,
):
    """Manually capture a `$ai_generation` event (PostHog AI observability).

    Uses the documented manual-capture API directly — no SDK wrapper. `extra`
    passes through any additional `$ai_*` properties (e.g. `$ai_stream`).
    """
    if not _client or not distinct_id:
        return
    properties = {
        "$ai_trace_id":      trace_id,
        "$ai_model":         model,
        "$ai_provider":      provider,
        "$ai_input":         input,
        "$ai_output_choices": output,
        "$ai_input_tokens":  input_tokens,
        "$ai_output_tokens": output_tokens,
        "$ai_latency":       latency,
        **extra,
    }
    _client.capture(distinct_id=distinct_id, event="$ai_generation", properties=properties)


def client_config():
    """Config the frontend snippet needs, exposed to templates."""
    return {
        "enabled": ENABLED,
        "key":     config.POSTHOG_API_KEY or "",
        "host":    config.POSTHOG_HOST,
    }

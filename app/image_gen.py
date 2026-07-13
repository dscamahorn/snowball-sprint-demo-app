import base64
import time

from google import genai
from google.genai import types

import config
from app import analytics

# Read once at module load — 521 KB JPEG, no need to hit disk on every request.
_REF_IMAGE_BYTES = config.IMAGE_REFERENCE_FILE.read_bytes()

_MODEL = "gemini-3.1-flash-image-preview"


def call_gemini_image(prompt: str, distinct_id: str | None = None, trace_id: str | None = None) -> bytes:
    """
    Calls the Gemini image generation model and returns raw PNG bytes.
    Passes the style reference image alongside the text prompt.
    Raises on API error or if no image part is found in the response.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    start = time.perf_counter()
    response = client.models.generate_content(
        model=_MODEL,
        contents=[
            types.Part.from_bytes(data=_REF_IMAGE_BYTES, mime_type="image/jpeg"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
        ),
    )
    latency = time.perf_counter() - start
    usage = getattr(response, "usage_metadata", None)
    analytics.capture_ai_generation(
        distinct_id,
        trace_id=trace_id,
        model=_MODEL,
        provider="gemini",
        input=[{"role": "user", "content": prompt}],
        output=[{"role": "assistant", "content": "<image>"}],
        input_tokens=getattr(usage, "prompt_token_count", None),
        output_tokens=getattr(usage, "candidates_token_count", None),
        latency=latency,
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data
    raise ValueError(
        "Gemini returned no image — the model may have refused the prompt or "
        "returned a text-only response. Check the prompt for policy violations."
    )


def build_image_prompt(image_fields: dict) -> str | None:
    """
    Loads image_prompt.md, strips the developer-only Integration Mapping section,
    substitutes the pre-parsed image fields, and returns the final prompt string.
    Returns None if any required field is missing.
    """
    required = ("loop_name_caps", "narrative_1", "narrative_2", "narrative_3", "narrative_4")
    if not all(image_fields.get(k) for k in required):
        return None

    raw      = config.load_file(config.IMAGE_PROMPT_FILE)
    template = raw.split("### Integration Mapping")[0].rstrip()

    return (
        template
        .replace("[LOOP_NAME_CAPS]",   image_fields["loop_name_caps"])
        .replace("[NARRATIVE_1_TEXT]", image_fields["narrative_1"])
        .replace("[NARRATIVE_2_TEXT]", image_fields["narrative_2"])
        .replace("[NARRATIVE_3_TEXT]", image_fields["narrative_3"])
        .replace("[NARRATIVE_4_TEXT]", image_fields["narrative_4"])
    )
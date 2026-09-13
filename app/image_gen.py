"""Builds the image prompt and asks Gemini to draw a prototype picture for a concept."""

import time

from google import genai
from google.genai import types

import config
from app import analytics

# Tells Gemini to decide for itself how much "thinking" to do before drawing.
# The Gemini SDK uses -1 to mean "choose the budget dynamically".
GEMINI_DYNAMIC_THINKING_BUDGET = -1

# Each placeholder that appears in image_prompt.md, mapped to the key of the
# concept field whose text replaces it.
PROMPT_PLACEHOLDERS = {
    "[LOOP_NAME_CAPS]": "loop_name_caps",
    "[NARRATIVE_1_TEXT]": "narrative_1",
    "[NARRATIVE_2_TEXT]": "narrative_2",
    "[NARRATIVE_3_TEXT]": "narrative_3",
    "[NARRATIVE_4_TEXT]": "narrative_4",
}

# The prompt file ends with notes for developers. Everything from this heading
# onward is cut off before the prompt is sent to the model.
DEVELOPER_NOTES_HEADING = "### Integration Mapping"


def build_image_prompt(image_fields: dict):
    """Fill the image prompt template with this concept's text.

    Returns the finished prompt string, or None if any required field is empty.
    """
    for field_key in PROMPT_PLACEHOLDERS.values():
        if not image_fields.get(field_key):
            return None

    prompt_file_text = config.load_text_file(config.IMAGE_PROMPT_FILE)
    prompt_template = prompt_file_text.split(DEVELOPER_NOTES_HEADING)[0].rstrip()

    prompt = prompt_template
    for placeholder, field_key in PROMPT_PLACEHOLDERS.items():
        prompt = prompt.replace(placeholder, image_fields[field_key])
    return prompt


def call_gemini_image(prompt: str, distinct_id: str, trace_id: str) -> bytes:
    """Send the prompt plus the style reference image to Gemini and return PNG bytes.

    Raises ValueError if Gemini answers without an image, for example when it
    refuses the prompt.
    """
    reference_image_bytes = config.IMAGE_REFERENCE_FILE.read_bytes()
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    start_time = time.perf_counter()
    response = client.models.generate_content(
        model=config.GEMINI_IMAGE_MODEL,
        contents=[
            types.Part.from_bytes(data=reference_image_bytes, mime_type="image/jpeg"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            thinking_config=types.ThinkingConfig(thinking_budget=GEMINI_DYNAMIC_THINKING_BUDGET),
        ),
    )
    latency_seconds = time.perf_counter() - start_time

    # Token counts are optional in Gemini's reply, so check before reading them.
    input_tokens = None
    output_tokens = None
    usage_metadata = response.usage_metadata
    if usage_metadata is not None:
        input_tokens = usage_metadata.prompt_token_count
        output_tokens = usage_metadata.candidates_token_count

    analytics.capture_ai_generation(
        distinct_id=distinct_id,
        trace_id=trace_id,
        model=config.GEMINI_IMAGE_MODEL,
        provider="gemini",
        input_messages=[{"role": "user", "content": prompt}],
        output_messages=[{"role": "assistant", "content": "<image>"}],
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_seconds=latency_seconds,
    )

    # The reply is a list of parts. The image, if any, is the part with inline data.
    response_parts = response.candidates[0].content.parts
    for part in response_parts:
        if part.inline_data is not None:
            return part.inline_data.data

    raise ValueError(
        "Gemini returned no image. The model may have refused the prompt or "
        "replied with text only. Check the prompt for policy problems."
    )

import time

import anthropic as anthropic_sdk
import config
from app import analytics

_MODEL = "claude-sonnet-4-6"


def _build_user_message(answers: dict, n_concepts: int, rag_context: str) -> str:
    return f"""**Question 1: What does the organization make or do?**
{answers["q1"]}

**Question 2: Where does waste, inefficiency, or end-of-life live in their value chain?**
{answers["q2"]}

**Question 3: What pressure is driving the need to change?**
{answers["q3"]}

**Question 4: What circular territory have they already explored?**
{answers["q4"]}

**Question 5: What does a successful outcome look like for them?**
{answers["q5"]}

---

**Number of concepts to generate:** {n_concepts}

**RAG context:**

{rag_context}
"""


def call_anthropic(
    answers: dict, n_concepts: int, system_prompt: str, rag_context: str,
    distinct_id: str | None = None, trace_id: str | None = None,
) -> str:
    user_message = _build_user_message(answers, n_concepts, rag_context)
    client = anthropic_sdk.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    start = time.perf_counter()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    latency = time.perf_counter() - start
    text = response.content[0].text
    analytics.capture_ai_generation(
        distinct_id,
        trace_id=trace_id,
        model=_MODEL,
        provider="anthropic",
        input=[{"role": "user", "content": user_message}],
        output=[{"role": "assistant", "content": text}],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency=latency,
    )
    return text


def stream_anthropic(
    answers: dict, n_concepts: int, system_prompt: str, rag_context: str,
    distinct_id: str | None = None, trace_id: str | None = None,
):
    """Generator that yields raw text chunks from the Anthropic streaming API."""
    user_message = _build_user_message(answers, n_concepts, rag_context)
    client = anthropic_sdk.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    start = time.perf_counter()
    with client.messages.stream(
        model=_MODEL,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            yield text
        final = stream.get_final_message()

    analytics.capture_ai_generation(
        distinct_id,
        trace_id=trace_id,
        model=_MODEL,
        provider="anthropic",
        input=[{"role": "user", "content": user_message}],
        output=[{"role": "assistant", "content": final.content[0].text}],
        input_tokens=final.usage.input_tokens,
        output_tokens=final.usage.output_tokens,
        latency=time.perf_counter() - start,
        **{"$ai_stream": True},
    )
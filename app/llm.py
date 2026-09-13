"""Talks to Claude to generate circular economy concepts.

Two entry points do the same job in different ways. generate_concepts() waits
for the whole reply before returning it. stream_concepts() hands back text a
piece at a time as it arrives, so the browser can show live progress.
"""

import time

import anthropic

import config
from app import analytics

# Upper bound on the length of the model's reply. Eight concepts with every
# field filled in can run long, so this is generous.
CONCEPT_GENERATION_MAX_TOKENS = 8192


def build_user_message(answers: dict, concept_count: int, rag_context: str) -> str:
    """Assemble the user message: the five answers, the concept count, and the RAG cases."""
    answer_1 = answers["q1"]
    answer_2 = answers["q2"]
    answer_3 = answers["q3"]
    answer_4 = answers["q4"]
    answer_5 = answers["q5"]

    user_message = f"""**Question 1: What does the organization make or do?**
{answer_1}

**Question 2: Where does waste, inefficiency, or end-of-life live in their value chain?**
{answer_2}

**Question 3: What pressure is driving the need to change?**
{answer_3}

**Question 4: What circular territory have they already explored?**
{answer_4}

**Question 5: What does a successful outcome look like for them?**
{answer_5}

---

**Number of concepts to generate:** {concept_count}

**RAG context:**

{rag_context}
"""
    return user_message


def create_anthropic_client():
    """Create a client for the Anthropic API using the key from .env."""
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def generate_concepts(
    answers: dict,
    concept_count: int,
    system_prompt: str,
    rag_context: str,
    distinct_id: str,
    trace_id: str,
) -> str:
    """Ask Claude for the concepts and return the full reply text once it is finished."""
    user_message = build_user_message(answers, concept_count, rag_context)
    client = create_anthropic_client()

    start_time = time.perf_counter()
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=CONCEPT_GENERATION_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    latency_seconds = time.perf_counter() - start_time

    response_text = response.content[0].text

    analytics.capture_ai_generation(
        distinct_id=distinct_id,
        trace_id=trace_id,
        model=config.CLAUDE_MODEL,
        provider="anthropic",
        input_messages=[{"role": "user", "content": user_message}],
        output_messages=[{"role": "assistant", "content": response_text}],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_seconds=latency_seconds,
    )
    return response_text


def stream_concepts(
    answers: dict,
    concept_count: int,
    system_prompt: str,
    rag_context: str,
    distinct_id: str,
    trace_id: str,
):
    """Ask Claude for the concepts and hand back the reply text piece by piece.

    This is a generator function: each "yield" sends one chunk of text to the
    caller while the model is still writing. A generator is required here
    because the route needs to forward chunks to the browser as they arrive,
    rather than waiting for the whole reply.
    """
    user_message = build_user_message(answers, concept_count, rag_context)
    client = create_anthropic_client()

    start_time = time.perf_counter()
    # The Anthropic SDK requires the "with" block for streaming so it can close
    # the connection cleanly when the stream ends.
    with client.messages.stream(
        model=config.CLAUDE_MODEL,
        max_tokens=CONCEPT_GENERATION_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text_chunk in stream.text_stream:
            yield text_chunk
        final_message = stream.get_final_message()
    latency_seconds = time.perf_counter() - start_time

    analytics.capture_ai_generation(
        distinct_id=distinct_id,
        trace_id=trace_id,
        model=config.CLAUDE_MODEL,
        provider="anthropic",
        input_messages=[{"role": "user", "content": user_message}],
        output_messages=[{"role": "assistant", "content": final_message.content[0].text}],
        input_tokens=final_message.usage.input_tokens,
        output_tokens=final_message.usage.output_tokens,
        latency_seconds=latency_seconds,
        is_stream=True,
    )

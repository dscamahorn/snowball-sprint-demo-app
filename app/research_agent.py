import json
import time
import xml.etree.ElementTree as ET

import anthropic
from tavily import TavilyClient

import config
from app import analytics

_anthropic = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
_tavily    = TavilyClient(api_key=config.TAVILY_API_KEY)

MAX_ROUNDS = 2
_MODEL     = "claude-sonnet-4-6"


def _capture(distinct_id, trace_id, user_content, response, latency):
    """Emit a $ai_generation for one research-agent Anthropic call."""
    analytics.capture_ai_generation(
        distinct_id,
        trace_id=trace_id,
        model=_MODEL,
        provider="anthropic",
        input=[{"role": "user", "content": user_content}],
        output=[{"role": "assistant", "content": response.content[0].text}],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency=latency,
    )


def stream_research_org(org_name: str, industry: str, distinct_id: str | None = None, trace_id: str | None = None):
    """
    Agentic research loop with parent company expansion. Yields event dicts:
      {"type": "status", "message": "..."}   — phase transitions
      {"type": "search", "query": "..."}     — each Tavily search issued
      {"type": "result", "data": {...}}       — final parsed answers (last event)
    Raises on unrecoverable error.
    """
    # Phase 1: plan queries for brand and parent (if known)
    yield {"type": "status", "message": "Planning search queries…"}
    plan = _plan_queries(org_name, industry, distinct_id, trace_id)
    brand_queries  = plan["brand_queries"]
    parent_name    = plan["parent"]
    parent_queries = plan["parent_queries"]

    seen_urls   = set()
    all_results = []

    # Round 1: brand queries
    for query in brand_queries:
        yield {"type": "search", "query": query}
        for result in _tavily_search(query):
            url = result.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                all_results.append(result)

    # Round 1: parent queries (if a parent was identified)
    if parent_name and parent_queries:
        yield {"type": "status", "message": f"Searching {parent_name} (parent company)…"}
        for query in parent_queries:
            yield {"type": "search", "query": query}
            for result in _tavily_search(query):
                url = result.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)

    # Reflect: let the LLM decide whether to search again (at most MAX_ROUNDS total)
    current_round = 1
    while current_round < MAX_ROUNDS:
        yield {"type": "status", "message": "Reviewing findings for gaps…"}
        decision = _reflect_on_results(org_name, all_results, distinct_id, trace_id)

        if decision["action"] == "done":
            break

        # search_again: run targeted follow-up queries
        yield {"type": "status", "message": "Searching for additional details…"}
        for query in decision["queries"]:
            yield {"type": "search", "query": query}
            for result in _tavily_search(query):
                url = result.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)

        current_round += 1

    # Synthesize all collected results
    yield {"type": "status", "message": "Synthesizing findings…"}
    data = _interpret_results(org_name, parent_name, all_results, distinct_id, trace_id)
    yield {"type": "result", "data": data}


def _plan_queries(org_name: str, industry: str, distinct_id=None, trace_id=None) -> dict:
    """
    Returns {"brand_queries": [...], "parent": str|None, "parent_queries": [...]}.
    """
    system = config.load_file(config.QUERY_PLANNER_PROMPT_FILE)
    user_content = f"Organization: {org_name}"
    if industry:
        user_content += f"\nIndustry/Sector: {industry}"

    start = time.perf_counter()
    response = _anthropic.messages.create(
        model=_MODEL,
        max_tokens=768,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    _capture(distinct_id, trace_id, user_content, response, time.perf_counter() - start)
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        plan = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Query planner returned invalid JSON: {e}") from e

    brand_queries = plan.get("brand_queries", [])
    if not isinstance(brand_queries, list) or not brand_queries:
        raise ValueError("Query planner returned no brand_queries")

    parent = plan.get("parent") or None
    if isinstance(parent, str) and parent.lower() in ("null", "none", ""):
        parent = None

    parent_queries = plan.get("parent_queries", []) if parent else []

    return {
        "brand_queries":  brand_queries[:5],
        "parent":         parent,
        "parent_queries": parent_queries[:4],
    }


def _reflect_on_results(org_name: str, results: list[dict], distinct_id=None, trace_id=None) -> dict:
    """
    Returns {"action": "done"} or {"action": "search_again", "queries": [...]}.
    Falls back to {"action": "done"} on any parsing failure — never blocks synthesis.
    Input is capped at 20 results to keep reflector latency and cost bounded;
    the interpreter always receives the full result set.
    """
    system = config.load_file(config.REFLECTOR_PROMPT_FILE)
    formatted    = _format_results(results[:20]) if results else "No search results were returned."
    user_content = f"Organization: {org_name}\n\nCurrent search results:\n{formatted}"

    start = time.perf_counter()
    response = _anthropic.messages.create(
        model=_MODEL,
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    _capture(distinct_id, trace_id, user_content, response, time.perf_counter() - start)
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        decision = json.loads(text)
        if decision.get("action") not in ("done", "search_again"):
            raise ValueError("Unexpected action value")
        if decision["action"] == "search_again":
            queries = decision.get("queries", [])
            if not isinstance(queries, list) or not queries:
                raise ValueError("search_again returned no queries")
            decision["queries"] = queries[:3]
        return decision
    except (json.JSONDecodeError, ValueError):
        return {"action": "done"}


def _tavily_search(query: str) -> list[dict]:
    response = _tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5,
    )
    return response.get("results", [])


def _format_results(results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.get('title', 'No title')}\n"
            f"URL: {r.get('url', '')}\n"
            f"{r.get('content', '').strip()}"
        )
    return "\n\n".join(parts)


def _interpret_results(org_name: str, parent_name: str | None, results: list[dict], distinct_id=None, trace_id=None) -> dict:
    # Blocks the worker thread for the duration of the Anthropic call (~5–10s).
    # Safe with --workers 1; revisit if worker count is raised.
    system       = config.load_file(config.INTERPRETER_PROMPT_FILE)
    formatted    = _format_results(results) if results else "No search results were returned."
    user_content = f"Organization: {org_name}"
    if parent_name:
        user_content += f"\nParent Company: {parent_name}"
    user_content += f"\n\nSearch Results:\n{formatted}"

    start = time.perf_counter()
    response = _anthropic.messages.create(
        model=_MODEL,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    _capture(distinct_id, trace_id, user_content, response, time.perf_counter() - start)
    return _parse_research_output(response.content[0].text.strip(), org_name)


def _parse_research_output(text: str, org_name: str) -> dict:
    start = text.find("<research>")
    end   = text.find("</research>")
    if start == -1 or end == -1:
        raise ValueError("Interpreter output did not contain a <research> block")

    root = ET.fromstring(text[start : end + len("</research>")])

    answers     = {}
    confidences = {}
    for key in ("q1", "q2", "q3", "q4", "q5"):
        el = root.find(key)
        if el is not None:
            answers[key]     = (el.text or "").strip()
            confidences[key] = el.get("confidence", "medium")
        else:
            answers[key]     = ""
            confidences[key] = "low"

    return {"answers": answers, "confidences": confidences, "org_name": org_name}
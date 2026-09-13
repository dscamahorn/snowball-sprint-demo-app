"""Researches an organization on the web and drafts the five survey answers.

The flow has four phases:
  1. Plan: Claude writes a set of web search queries for the brand, and a
     second set for its parent company if it has one.
  2. Search: each query runs through Tavily, a web search API for AI apps.
  3. Reflect: Claude looks at the results, and if it sees gaps it asks for
     one more round of targeted searches.
  4. Interpret: Claude writes the five survey answers from everything found,
     with a confidence rating on each.
"""

import json
import time
import xml.etree.ElementTree as ElementTree

import anthropic
from tavily import TavilyClient

import config
from app import analytics

# How many search rounds may run in total. Round 1 always runs; the reflector
# may add follow-up rounds until this cap is reached.
MAX_SEARCH_ROUNDS = 2

# Caps on how many queries the planner and reflector may hand back.
MAX_BRAND_QUERIES = 5
MAX_PARENT_QUERIES = 4
MAX_FOLLOW_UP_QUERIES = 3

# The reflector only sees the first results so its call stays quick and cheap.
# The interpreter always sees everything.
MAX_RESULTS_SHOWN_TO_REFLECTOR = 20

# How many web pages Tavily returns for each query.
TAVILY_RESULTS_PER_QUERY = 5

# Reply length limits for each Claude call. The planner and reflector return
# short JSON; the interpreter writes five paragraphs.
QUERY_PLANNER_MAX_TOKENS = 768
REFLECTOR_MAX_TOKENS = 256
INTERPRETER_MAX_TOKENS = 2048

SURVEY_ANSWER_KEYS = ["q1", "q2", "q3", "q4", "q5"]

# Confidence used when the interpreter leaves the rating off, and when it
# skips a question entirely.
DEFAULT_CONFIDENCE = "medium"
MISSING_ANSWER_CONFIDENCE = "low"

CODE_FENCE = "```"


def stream_research_org(org_name: str, industry: str, distinct_id: str, trace_id: str):
    """Run the whole research flow, reporting progress as it goes.

    This is a generator function: each "yield" sends one progress event to the
    route, which forwards it to the browser. That is why it cannot be a plain
    function that returns at the end. Events are dictionaries:
      {"type": "status", "message": "..."}  a phase change
      {"type": "search", "query": "..."}    one web search being run
      {"type": "result", "data": {...}}     the finished answers (always last)
    Any unrecoverable problem is raised as an exception for the route to handle.
    """
    yield {"type": "status", "message": "Planning search queries..."}
    plan = plan_queries(org_name, industry, distinct_id, trace_id)
    brand_queries = plan["brand_queries"]
    parent_name = plan["parent"]
    parent_queries = plan["parent_queries"]

    # Results from every round are pooled here. seen_urls stops the same page
    # from being counted twice when two queries return it.
    seen_urls = set()
    all_results = []

    # Round 1, part one: the brand itself.
    for query in brand_queries:
        yield {"type": "search", "query": query}
        search_results = search_web(query)
        add_new_results(search_results, seen_urls, all_results)

    # Round 1, part two: the parent company, when the planner found one.
    if parent_name and parent_queries:
        yield {"type": "status", "message": "Searching " + parent_name + " (parent company)..."}
        for query in parent_queries:
            yield {"type": "search", "query": query}
            search_results = search_web(query)
            add_new_results(search_results, seen_urls, all_results)

    # Follow-up rounds: let Claude decide whether the results have gaps.
    current_round = 1
    while current_round < MAX_SEARCH_ROUNDS:
        yield {"type": "status", "message": "Reviewing findings for gaps..."}
        decision = reflect_on_results(org_name, all_results, distinct_id, trace_id)
        if decision["action"] == "done":
            break

        yield {"type": "status", "message": "Searching for additional details..."}
        for query in decision["queries"]:
            yield {"type": "search", "query": query}
            search_results = search_web(query)
            add_new_results(search_results, seen_urls, all_results)
        current_round += 1

    yield {"type": "status", "message": "Synthesizing findings..."}
    research_data = interpret_results(org_name, parent_name, all_results, distinct_id, trace_id)
    yield {"type": "result", "data": research_data}


def add_new_results(search_results: list, seen_urls: set, all_results: list):
    """Append results whose URL has not been seen before, and remember their URLs."""
    for search_result in search_results:
        result_url = search_result.get("url", "")
        if result_url not in seen_urls:
            seen_urls.add(result_url)
            all_results.append(search_result)


def ask_claude(system_prompt: str, user_content: str, max_tokens: int, distinct_id: str, trace_id: str) -> str:
    """Make one Claude call, record it for analytics, and return the reply text."""
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    start_time = time.perf_counter()
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    latency_seconds = time.perf_counter() - start_time

    response_text = response.content[0].text
    analytics.capture_ai_generation(
        distinct_id=distinct_id,
        trace_id=trace_id,
        model=config.CLAUDE_MODEL,
        provider="anthropic",
        input_messages=[{"role": "user", "content": user_content}],
        output_messages=[{"role": "assistant", "content": response_text}],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_seconds=latency_seconds,
    )
    return response_text.strip()


def strip_code_fence(text: str) -> str:
    """Remove a Markdown code fence if the model wrapped its JSON in one."""
    if not text.startswith(CODE_FENCE):
        return text
    # Drop the opening fence line (which may say ```json), then the closing fence.
    first_line_break = text.find("\n")
    without_opening = text[first_line_break + 1 :]
    closing_fence_index = without_opening.rfind(CODE_FENCE)
    if closing_fence_index == -1:
        return without_opening.strip()
    return without_opening[:closing_fence_index].strip()


def plan_queries(org_name: str, industry: str, distinct_id: str, trace_id: str) -> dict:
    """Ask Claude which web searches to run.

    Returns a dictionary with "brand_queries" (list), "parent" (name or None),
    and "parent_queries" (list, empty when there is no parent).
    """
    system_prompt = config.load_text_file(config.QUERY_PLANNER_PROMPT_FILE)
    user_content = "Organization: " + org_name
    if industry:
        user_content += "\nIndustry/Sector: " + industry

    reply_text = ask_claude(system_prompt, user_content, QUERY_PLANNER_MAX_TOKENS, distinct_id, trace_id)
    reply_text = strip_code_fence(reply_text)

    try:
        plan = json.loads(reply_text)
    except json.JSONDecodeError as decode_error:
        # The planner is told to return only JSON; anything else is a real failure.
        raise ValueError("Query planner returned invalid JSON: " + str(decode_error)) from decode_error

    brand_queries = plan.get("brand_queries", [])
    if not isinstance(brand_queries, list) or len(brand_queries) == 0:
        raise ValueError("Query planner returned no brand_queries")

    # The planner sometimes writes the word "null" instead of a JSON null.
    parent_name = plan.get("parent")
    if isinstance(parent_name, str):
        if parent_name.strip().lower() in ["", "null", "none"]:
            parent_name = None
    else:
        parent_name = None

    parent_queries = []
    if parent_name:
        parent_queries = plan.get("parent_queries", [])

    return {
        "brand_queries": brand_queries[:MAX_BRAND_QUERIES],
        "parent": parent_name,
        "parent_queries": parent_queries[:MAX_PARENT_QUERIES],
    }


def reflect_on_results(org_name: str, results: list, distinct_id: str, trace_id: str) -> dict:
    """Ask Claude whether the results are good enough or need another search round.

    Returns {"action": "done"} or {"action": "search_again", "queries": [...]}.
    Any problem reading the reply falls back to "done" so research always finishes.
    """
    system_prompt = config.load_text_file(config.REFLECTOR_PROMPT_FILE)
    if len(results) == 0:
        formatted_results = "No search results were returned."
    else:
        formatted_results = format_results(results[:MAX_RESULTS_SHOWN_TO_REFLECTOR])
    user_content = "Organization: " + org_name + "\n\nCurrent search results:\n" + formatted_results

    reply_text = ask_claude(system_prompt, user_content, REFLECTOR_MAX_TOKENS, distinct_id, trace_id)
    reply_text = strip_code_fence(reply_text)

    try:
        decision = json.loads(reply_text)
        if decision.get("action") not in ["done", "search_again"]:
            raise ValueError("Unexpected action value")
        if decision["action"] == "search_again":
            follow_up_queries = decision.get("queries", [])
            if not isinstance(follow_up_queries, list) or len(follow_up_queries) == 0:
                raise ValueError("search_again returned no queries")
            decision["queries"] = follow_up_queries[:MAX_FOLLOW_UP_QUERIES]
        return decision
    except (json.JSONDecodeError, ValueError):
        # Malformed reflector output should never block the rest of the flow.
        return {"action": "done"}


def search_web(query: str) -> list:
    """Run one web search through Tavily and return its list of result dictionaries."""
    tavily_client = TavilyClient(api_key=config.TAVILY_API_KEY)
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=TAVILY_RESULTS_PER_QUERY,
    )
    return response.get("results", [])


def format_results(results: list) -> str:
    """Lay out search results as numbered blocks of title, URL, and page text."""
    formatted_blocks = []
    result_number = 1
    for search_result in results:
        title = search_result.get("title", "No title")
        url = search_result.get("url", "")
        content = search_result.get("content", "").strip()
        block = "[" + str(result_number) + "] " + title + "\nURL: " + url + "\n" + content
        formatted_blocks.append(block)
        result_number += 1
    return "\n\n".join(formatted_blocks)


def interpret_results(org_name: str, parent_name, results: list, distinct_id: str, trace_id: str) -> dict:
    """Ask Claude to write the five survey answers from all the search results."""
    system_prompt = config.load_text_file(config.INTERPRETER_PROMPT_FILE)
    if len(results) == 0:
        formatted_results = "No search results were returned."
    else:
        formatted_results = format_results(results)

    user_content = "Organization: " + org_name
    if parent_name:
        user_content += "\nParent Company: " + parent_name
    user_content += "\n\nSearch Results:\n" + formatted_results

    reply_text = ask_claude(system_prompt, user_content, INTERPRETER_MAX_TOKENS, distinct_id, trace_id)
    return parse_research_output(reply_text, org_name)


def parse_research_output(reply_text: str, org_name: str) -> dict:
    """Read the interpreter's <research> XML into answers and confidence ratings."""
    open_tag = "<research>"
    close_tag = "</research>"
    start_index = reply_text.find(open_tag)
    end_index = reply_text.find(close_tag)
    if start_index == -1 or end_index == -1:
        raise ValueError("Interpreter output did not contain a <research> block")

    research_xml = reply_text[start_index : end_index + len(close_tag)]
    root_element = ElementTree.fromstring(research_xml)

    answers = {}
    confidences = {}
    for answer_key in SURVEY_ANSWER_KEYS:
        answer_element = root_element.find(answer_key)
        if answer_element is None:
            answers[answer_key] = ""
            confidences[answer_key] = MISSING_ANSWER_CONFIDENCE
        else:
            answer_text = answer_element.text
            if answer_text is None:
                answer_text = ""
            answers[answer_key] = answer_text.strip()
            confidences[answer_key] = answer_element.get("confidence", DEFAULT_CONFIDENCE)

    return {"answers": answers, "confidences": confidences, "org_name": org_name}

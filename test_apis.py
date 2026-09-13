"""Quick connectivity check for the three external APIs the app uses.

Run with: uv run python test_apis.py
Each check is skipped when its key is missing from .env, so you can test
whichever services you have set up so far.
"""

import anthropic
from google import genai
from tavily import TavilyClient

import config

# Small, cheap models are enough to prove the connection works.
ANTHROPIC_TEST_MODEL = "claude-haiku-4-5-20251001"
GEMINI_TEST_MODEL = "gemini-2.5-flash"
TEST_MAX_TOKENS = 64


def test_anthropic():
    """Send a one-line prompt to Claude and print the reply."""
    if not config.ANTHROPIC_API_KEY:
        print("ANTHROPIC: key not set, skipping")
        return
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_TEST_MODEL,
        max_tokens=TEST_MAX_TOKENS,
        messages=[{"role": "user", "content": "Say 'Anthropic API works!' and nothing else."}],
    )
    reply_text = message.content[0].text
    print("ANTHROPIC: " + reply_text)


def test_gemini():
    """Send a one-line prompt to Gemini and print the reply."""
    if not config.GEMINI_API_KEY:
        print("GEMINI: key not set, skipping")
        return
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_TEST_MODEL,
        contents="Say 'Gemini API works!' and nothing else.",
    )
    reply_text = response.text.strip()
    print("GEMINI: " + reply_text)


def test_tavily():
    """Run one tiny web search through Tavily and print the first result title."""
    if not config.TAVILY_API_KEY:
        print("TAVILY: key not set, skipping")
        return
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    response = client.search(query="circular economy", max_results=1)
    results = response.get("results", [])
    if len(results) == 0:
        print("TAVILY: OK, search returned no results")
        return
    first_title = results[0].get("title", "(no title)")
    print("TAVILY: OK, got result: " + first_title)


test_anthropic()
test_gemini()
test_tavily()

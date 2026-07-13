import os
from dotenv import load_dotenv

load_dotenv()

def test_anthropic():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC: key not set, skipping")
        return
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[{"role": "user", "content": "Say 'Anthropic API works!' and nothing else."}],
    )
    print(f"ANTHROPIC: {msg.content[0].text}")

def test_gemini():
    from google import genai
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("GEMINI: key not set, skipping")
        return
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say 'Gemini API works!' and nothing else.",
    )
    print(f"GEMINI: {response.text.strip()}")

def test_tavily():
    from tavily import TavilyClient
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        print("TAVILY: key not set, skipping")
        return
    client = TavilyClient(api_key=key)
    response = client.search(query="circular economy", max_results=1)
    results = response.get("results", [])
    if results:
        print(f"TAVILY: OK — got result: {results[0].get('title', '(no title)')}")
    else:
        print("TAVILY: OK — search returned no results")

test_anthropic()
test_gemini()
test_tavily()

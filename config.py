import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent


def load_file(path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY")
TAVILY_API_KEY    = os.environ.get("TAVILY_API_KEY")
SECRET_KEY        = os.environ.get("SECRET_KEY", "dev-change-this-in-production")

POSTHOG_API_KEY = os.environ.get("POSTHOG_API_KEY")
POSTHOG_HOST    = os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com")
POSTHOG_ENABLED = os.environ.get("POSTHOG_ENABLED", "false").lower() == "true"

PROMPT_FILE                = ROOT / "prompts" / "system_prompt.md"
IMAGE_PROMPT_FILE          = ROOT / "prompts" / "image_prompt.md"
IMAGE_REFERENCE_FILE       = ROOT / "knowledge" / "image_reference.jpg"
QUERY_PLANNER_PROMPT_FILE  = ROOT / "prompts" / "query_planner_prompt.md"
INTERPRETER_PROMPT_FILE    = ROOT / "prompts" / "interpreter_prompt.md"
REFLECTOR_PROMPT_FILE      = ROOT / "prompts" / "reflector_prompt.md"
DESIGN_FILE                = ROOT / "docs"    / "DESIGN.md"
CPR_RAG                    = ROOT / "knowledge" / "RAG_consumer_packaging_reuse.xml"
FWU_RAG                    = ROOT / "knowledge" / "RAG_food_waste_upcycling.xml"
BAS_RAG                    = ROOT / "knowledge" / "RAG_b2b_asset_sharing.xml"

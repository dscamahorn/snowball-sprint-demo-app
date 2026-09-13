# Central place for settings: API keys read from .env, model names, tunable
# limits, and the path to every file the app reads from disk.
# Change a value here and every module that imports config picks it up.

import os
from pathlib import Path

from dotenv import load_dotenv

# Read the .env file in the project root and copy its values into the
# process environment so os.environ.get() can find them below.
load_dotenv()

PROJECT_ROOT = Path(__file__).parent


# --- API keys and secrets ---------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# Flask signs the session cookie with this key. The fallback value is only
# for local development and must be replaced in .env for a real deployment.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-this-in-production")

# PostHog analytics. Both the on/off switch and the key must be set before
# the app sends any analytics events.
POSTHOG_API_KEY = os.environ.get("POSTHOG_API_KEY")
POSTHOG_HOST = os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com")
posthog_enabled_setting = os.environ.get("POSTHOG_ENABLED", "false")
POSTHOG_ENABLED = posthog_enabled_setting.lower() == "true"


# --- Model names ------------------------------------------------------------

# Used for every Claude call: query planning, reflection, interpretation,
# and concept generation.
CLAUDE_MODEL = "claude-sonnet-4-6"

# Used to draw the prototype visualization image.
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"


# --- Concept count limits ---------------------------------------------------

# The review page lets the user pick how many concepts to generate.
MIN_CONCEPT_COUNT = 1
MAX_CONCEPT_COUNT = 8
DEFAULT_CONCEPT_COUNT = 3


# --- File locations ---------------------------------------------------------

PROMPTS_DIRECTORY = PROJECT_ROOT / "prompts"
KNOWLEDGE_DIRECTORY = PROJECT_ROOT / "knowledge"

# Prompts sent to the models. Read from disk on every request so edits take
# effect without restarting the server.
SYSTEM_PROMPT_FILE = PROMPTS_DIRECTORY / "system_prompt.md"
IMAGE_PROMPT_FILE = PROMPTS_DIRECTORY / "image_prompt.md"
QUERY_PLANNER_PROMPT_FILE = PROMPTS_DIRECTORY / "query_planner_prompt.md"
INTERPRETER_PROMPT_FILE = PROMPTS_DIRECTORY / "interpreter_prompt.md"
REFLECTOR_PROMPT_FILE = PROMPTS_DIRECTORY / "reflector_prompt.md"

# Style reference picture handed to Gemini alongside the image prompt.
IMAGE_REFERENCE_FILE = KNOWLEDGE_DIRECTORY / "image_reference.jpg"

# RAG knowledge bases: real case studies appended to every concept request.
CONSUMER_PACKAGING_RAG_FILE = KNOWLEDGE_DIRECTORY / "RAG_consumer_packaging_reuse.xml"
FOOD_WASTE_RAG_FILE = KNOWLEDGE_DIRECTORY / "RAG_food_waste_upcycling.xml"
B2B_ASSET_SHARING_RAG_FILE = KNOWLEDGE_DIRECTORY / "RAG_b2b_asset_sharing.xml"


def load_text_file(file_path) -> str:
    """Read a whole text file from disk and return it as one string."""
    with open(file_path, "r", encoding="utf-8") as text_file:
        return text_file.read()

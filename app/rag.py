"""Loads the RAG knowledge files and joins them into one block of text.

RAG stands for retrieval-augmented generation. We hand the model a set of
real case studies alongside the user's answers so the concepts it proposes
are grounded in things that have actually worked for other organizations.
"""

import config


def load_rag_context() -> str:
    """Read all three knowledge files and return them as one labeled string."""
    consumer_packaging_cases = config.load_text_file(config.CONSUMER_PACKAGING_RAG_FILE)
    food_waste_cases = config.load_text_file(config.FOOD_WASTE_RAG_FILE)
    b2b_asset_sharing_cases = config.load_text_file(config.B2B_ASSET_SHARING_RAG_FILE)

    # Each section gets a label so the model knows which domain it is reading.
    rag_context = (
        "[Consumer Packaging Reuse]\n" + consumer_packaging_cases + "\n\n"
        "[Food Waste and Upcycling]\n" + food_waste_cases + "\n\n"
        "[B2B Asset Sharing Platforms]\n" + b2b_asset_sharing_cases
    )
    return rag_context

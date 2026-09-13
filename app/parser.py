"""Turns the XML the concept generator returns into plain Python dictionaries.

The system prompt tells Claude to wrap its whole answer in a <response> block.
This module finds that block, parses it, and pulls out the profile analysis,
the closing summary, and one dictionary per concept for the concepts page.
"""

import xml.etree.ElementTree as ElementTree

RESPONSE_OPEN_TAG = "<response>"
RESPONSE_CLOSE_TAG = "</response>"


def get_child_text(parent_element, tag_name) -> str:
    """Return the trimmed text of a child tag, or an empty string if it is missing."""
    if parent_element is None:
        return ""
    child_text = parent_element.findtext(tag_name)
    if child_text is None:
        return ""
    return child_text.strip()


def parse_assumptions(concept_element) -> list[str]:
    """Collect the <assumption> entries of one concept as a list of strings."""
    assumptions = []
    for assumption_element in concept_element.findall("assumptions/assumption"):
        if assumption_element.text:
            assumptions.append(assumption_element.text.strip())
    return assumptions


def parse_citations(concept_element) -> list[dict]:
    """Collect the <citation> entries of one concept, each as a small dictionary."""
    citations = []
    for citation_element in concept_element.findall("citations/citation"):
        citation = {
            "company": get_child_text(citation_element, "company"),
            "case_id": get_child_text(citation_element, "case_id"),
            "rationale": get_child_text(citation_element, "rationale"),
        }
        citations.append(citation)
    return citations


def parse_image_fields(concept_element) -> dict:
    """Pull out the pieces of text the image prompt needs for this concept."""
    image_element = concept_element.find("prototype_image")
    # get_child_text handles a missing <prototype_image> by returning "".
    image_fields = {
        "loop_name_caps": get_child_text(image_element, "loop_name"),
        "narrative_1": get_child_text(image_element, "narrative_1"),
        "narrative_2": get_child_text(image_element, "narrative_2"),
        "narrative_3": get_child_text(image_element, "narrative_3"),
        "narrative_4": get_child_text(image_element, "narrative_4"),
    }
    return image_fields


def parse_concept(concept_element) -> dict:
    """Convert one <concept> element into the dictionary the template expects."""
    concept_number_text = concept_element.get("number", "0")
    concept = {
        "number": int(concept_number_text),
        "title": get_child_text(concept_element, "title"),
        "mechanic": get_child_text(concept_element, "mechanic"),
        "user": get_child_text(concept_element, "target_user"),
        "value_chain": get_child_text(concept_element, "value_chain_inefficiency"),
        "pressure": get_child_text(concept_element, "pressure_addressed"),
        "description": get_child_text(concept_element, "description"),
        "prototype": get_child_text(concept_element, "prototype_sentence"),
        "image_fields": parse_image_fields(concept_element),
        "verdict": get_child_text(concept_element, "prototype_verdict"),
        "alignment": get_child_text(concept_element, "outcome_alignment"),
        "assumptions": parse_assumptions(concept_element),
        "analogues": parse_citations(concept_element),
    }
    return concept


def get_concept_number(concept) -> int:
    """Sort key so concepts can be ordered by their number."""
    return concept["number"]


def parse_concept_output(llm_text) -> dict:
    """Parse the model's full reply into profile analysis, themes, and concepts.

    Always returns a dictionary with the keys "profile_analysis", "themes", and
    "concepts". If the reply cannot be parsed, "profile_analysis" holds an error
    message and "concepts" is an empty list so the page still renders.
    """
    result = {
        "profile_analysis": "",
        "themes": "",
        "concepts": [],
    }

    # Find just the <response>...</response> block, ignoring any chatter around it.
    start_index = llm_text.find(RESPONSE_OPEN_TAG)
    end_index = llm_text.find(RESPONSE_CLOSE_TAG)
    if start_index == -1 or end_index == -1:
        result["profile_analysis"] = "Could not locate <response> block in LLM output."
        return result
    response_xml = llm_text[start_index : end_index + len(RESPONSE_CLOSE_TAG)]

    try:
        root_element = ElementTree.fromstring(response_xml)
    except ElementTree.ParseError as parse_error:
        # The model occasionally emits a bare "&" or "<" that is not valid XML.
        result["profile_analysis"] = "XML parse error: " + str(parse_error)
        return result

    result["profile_analysis"] = get_child_text(root_element, "profile_analysis")
    result["themes"] = get_child_text(root_element, "summary")

    concepts = []
    for concept_element in root_element.findall("concepts/concept"):
        concepts.append(parse_concept(concept_element))
    concepts.sort(key=get_concept_number)
    result["concepts"] = concepts

    return result

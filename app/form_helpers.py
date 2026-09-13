"""Small helpers for reading the survey form fields out of a Flask request."""

import config

SURVEY_ANSWER_KEYS = ["q1", "q2", "q3", "q4", "q5"]


def read_answers_from_form(form) -> dict:
    """Read the five survey answers from a submitted form, trimmed of whitespace."""
    answers = {}
    for answer_key in SURVEY_ANSWER_KEYS:
        answer_text = form.get(answer_key, "")
        answers[answer_key] = answer_text.strip()
    return answers


def read_concept_count_from_form(form) -> int:
    """Read how many concepts the user asked for, kept inside the allowed range."""
    concept_count_text = form.get("n_concepts", str(config.DEFAULT_CONCEPT_COUNT))
    try:
        concept_count = int(concept_count_text)
    except ValueError:
        # Someone edited the hidden field to something that is not a number.
        concept_count = config.DEFAULT_CONCEPT_COUNT

    if concept_count < config.MIN_CONCEPT_COUNT:
        concept_count = config.MIN_CONCEPT_COUNT
    if concept_count > config.MAX_CONCEPT_COUNT:
        concept_count = config.MAX_CONCEPT_COUNT
    return concept_count

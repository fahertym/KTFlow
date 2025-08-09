from __future__ import annotations

"""Rule-based sentence tagging for Knowledge Topology layers.

Returns a single label from {"S", "L", "R", "St", "G", "M", "UNK"} for an
input sentence. Priority (highest wins): M > G > St > R > L > S > UNK.
"""

import re
from typing import Literal

KTLabel = Literal["S", "L", "R", "St", "G", "M", "UNK"]


def _has(patterns: list[str], s_lower: str) -> bool:
    return any(p in s_lower for p in patterns)


def _has_regex(regexes: list[str], text: str) -> bool:
    return any(re.search(rx, text, flags=re.IGNORECASE) for rx in regexes)


def _is_bare_term_list(s: str) -> bool:
    """Heuristic: detect sentences that are mostly comma-separated terms.

    Looks for a colon introducing a list or multiple commas with short tokens
    and few verbs.
    """
    s_lower = s.lower()
    if ":" in s_lower and "," in s_lower:
        return True
    if s.count(",") >= 2 and len(s) < 160:
        # If there are many commas and no obvious verbs, treat as list
        if not re.search(r"\b(is|are|was|were|be|am|being|been|do|does|did|has|have|had)\b", s_lower):
            return True
    return False


def tag_sentence_rules(s: str) -> KTLabel:
    """Tag a sentence into a KT layer using simple rules.

    Parameters
    ----------
    s: str
        Sentence text.

    Returns
    -------
    KTLabel
        One of: "S", "L", "R", "St", "G", "M", "UNK".
    """
    if not s or not s.strip():
        return "UNK"

    s_lower = s.strip().lower()

    # M: Meta (assumptions/reframing)
    if _has([
        "assume", "assumption", "assumptions", "what if", "reframe",
        "hidden", "bias", "perspective", "premise", "underlying",
        "frame", "meta",
    ], s_lower):
        return "M"

    # G: Generative (principles/transfer)
    if _has([
        "in general", "the principle", "principle of", "the rule",
        "applies to", "can be applied", "generalize", "generalise",
        "transfer to", "in other domains",
    ], s_lower):
        return "G"

    # St: Structural (systems/feedbacks)
    if _has([
        "overall", "system works", "integrat", "feedback", "loop",
        "component", "components", "interact", "structure", "subsystem",
        "dynamics", "flows", "flow of", "architecture",
    ], s_lower):
        return "St"

    # R: Relational (causal/associative links)
    if _has([
        "because", "therefore", "thus", "hence", "affects", "causes",
        "leads to", "results in", "due to", "impact", "impacts",
        "affect", "drives",
    ], s_lower) or _has_regex([r"\bif\b.*\bthen\b"], s):
        return "R"

    # L: Literal (definitions)
    if _has([
        "means", "is defined as", "defined as", "refers to",
        "is a ", "is an ", "is the ",
    ], s_lower):
        return "L"

    # S: Symbol (form/terms)
    if _has([
        "what is", "list", "term", "terms",
    ], s_lower) or _is_bare_term_list(s):
        return "S"

    return "UNK"

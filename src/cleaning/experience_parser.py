"""HireTrends Experience Requirement Parser.

Extracts minimum and maximum years of required experience from job descriptions
and title strings using contextual regular expressions.
"""

import re
from typing import Any, Dict, Optional, Tuple

EXPERIENCE_PATTERNS = [
    # Range: "3 to 5 years", "3-5 years", "3 - 5 yrs", "3–5 years"
    (
        re.compile(
            r"\b(\d{1,2})\s*(?:to|-|–)\s*(\d{1,2})\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of\s+(?:relevant\s+)?experience)?\b",
            re.IGNORECASE,
        ),
        "range",
    ),
    # Minimum with plus or wording: "5+ years", "5 plus years", "minimum 5 years", "at least 5 yrs"
    (
        re.compile(
            r"\b(?:minimum|at\s+least|min\.?)\s*(\d{1,2})\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of\s+(?:relevant\s+)?experience)?\b",
            re.IGNORECASE,
        ),
        "min_plus",
    ),
    (
        re.compile(
            r"\b(\d{1,2})\s*(?:\+|plus)\s*(?:years?|yrs?)(?:\s+of\s+(?:relevant\s+)?experience)?\b",
            re.IGNORECASE,
        ),
        "min_plus",
    ),
    # Exact / Single year phrase: "3 years of experience", "2 years experience"
    (
        re.compile(
            r"\b(\d{1,2})\s*(?:years?|yrs?)\s+of\s+(?:relevant\s+)?experience\b",
            re.IGNORECASE,
        ),
        "exact",
    ),
    (
        re.compile(
            r"\b(\d{1,2})\s*(?:years?|yrs?)\s+experience\b",
            re.IGNORECASE,
        ),
        "exact",
    ),
    # Fresh graduate / Entry level phrases
    (
        re.compile(
            r"\b(fresh\s+graduates?|freshers?|no\s+experience\s+required|entry[\s\-]?level)\b",
            re.IGNORECASE,
        ),
        "fresh",
    ),
]


def parse_experience(
    text: Optional[str],
) -> Dict[str, Any]:
    """Parse experience requirements from unstructured text.

    Args:
        text: Free-text job description or title.

    Returns:
        {
            "experience_text": str | None,
            "experience_min_years": float | None,
            "experience_max_years": float | None
        }
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "experience_text": None,
            "experience_min_years": None,
            "experience_max_years": None,
        }

    for pattern, ptype in EXPERIENCE_PATTERNS:
        match = pattern.search(text)
        if match:
            matched_phrase = match.group(0).strip()

            if ptype == "range":
                min_yr = float(match.group(1))
                max_yr = float(match.group(2))
                # Sanity check: min <= max and reasonable career bounds
                if min_yr <= max_yr <= 35:
                    return {
                        "experience_text": matched_phrase,
                        "experience_min_years": min_yr,
                        "experience_max_years": max_yr,
                    }

            elif ptype in ("min_plus", "exact"):
                val = float(match.group(1))
                if val <= 35:
                    return {
                        "experience_text": matched_phrase,
                        "experience_min_years": val,
                        "experience_max_years": None,
                    }

            elif ptype == "fresh":
                return {
                    "experience_text": matched_phrase,
                    "experience_min_years": 0.0,
                    "experience_max_years": 1.0,
                }

    # Missing experience: preserve as null, never invent
    return {
        "experience_text": None,
        "experience_min_years": None,
        "experience_max_years": None,
    }

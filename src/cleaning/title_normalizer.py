"""HireTrends Job Title Normalization Engine.

Standardizes job titles by expanding abbreviations, normalizing spacing/capitalization,
and identifying seniority levels while strictly preserving specializations.
"""

import re
from typing import Any, Dict, Optional, Tuple

SENIORITY_PATTERNS = [
    (
        "Executive / Director",
        re.compile(r"\b(chief|cxo|cto|cio|ciso|ceo|director|head of|vp|vice president)\b", re.IGNORECASE),
    ),
    (
        "Lead / Principal",
        re.compile(r"\b(principal|staff|lead|team lead|tech lead|architect|specialist)\b", re.IGNORECASE),
    ),
    (
        "Senior",
        re.compile(r"\b(senior|sr\.?|snr\.?|lead senior)\b", re.IGNORECASE),
    ),
    (
        "Mid-Level",
        re.compile(r"\b(intermediate|mid[\s\-]?level|experienced)\b", re.IGNORECASE),
    ),
    (
        "Junior / Entry-Level",
        re.compile(r"\b(junior|jr\.?|associate|entry[\s\-]?level|fresh|trainee|apprentice|intern|internship)\b", re.IGNORECASE),
    ),
]

# Title token replacements for standardization
ABBREVIATION_REPLACEMENTS = [
    (re.compile(r"\bSr\.(?=\s|$)|(?<=\b)Sr\b", re.IGNORECASE), "Senior"),
    (re.compile(r"\bSnr\.(?=\s|$)|(?<=\b)Snr\b", re.IGNORECASE), "Senior"),
    (re.compile(r"\bJr\.(?=\s|$)|(?<=\b)Jr\b", re.IGNORECASE), "Junior"),
    (re.compile(r"\bDev\b", re.IGNORECASE), "Developer"),
    (re.compile(r"\bDevs\b", re.IGNORECASE), "Developers"),
    (re.compile(r"\bEngr?\.(?=\s|$)|(?<=\b)Engr?\b", re.IGNORECASE), "Engineer"),
    (re.compile(r"\bAdmin\.(?=\s|$)|(?<=\b)Admin\b", re.IGNORECASE), "Administrator"),
    (re.compile(r"\bMgr\.(?=\s|$)|(?<=\b)Mgr\b", re.IGNORECASE), "Manager"),
    (re.compile(r"\bTech\.(?=\s|$)|(?<=\b)Tech\b", re.IGNORECASE), "Technical"),
    (re.compile(r"\bSoft\.(?=\s|$)|(?<=\b)Soft\b", re.IGNORECASE), "Software"),
    (re.compile(r"\bFullstack\b", re.IGNORECASE), "Full Stack"),
    (re.compile(r"\bFront[- ]?end\b", re.IGNORECASE), "Frontend"),
    (re.compile(r"\bBack[- ]?end\b", re.IGNORECASE), "Backend"),
    (re.compile(r"\bSQA\b", re.IGNORECASE), "QA"),
    (re.compile(r"\bQA/QC\b", re.IGNORECASE), "QA"),
    (re.compile(r"\bNodejs\b", re.IGNORECASE), "Node.js"),
    (re.compile(r"\bReactjs\b", re.IGNORECASE), "React"),
    (re.compile(r"\bVuejs\b", re.IGNORECASE), "Vue.js"),
]


def extract_seniority(title: str) -> str:
    """Extract seniority level from job title."""
    if not title:
        return "Unspecified"

    for level, pattern in SENIORITY_PATTERNS:
        if pattern.search(title):
            return level
    return "Mid-Level"  # Standard default when no explicit seniority prefix is given


def normalize_title(raw_title: Optional[str]) -> Dict[str, Any]:
    """Normalize a raw job title into a clean, standardized title string.

    Args:
        raw_title: Verbatim job title string.

    Returns:
        {
            "original_title": str,
            "normalized_title": str,
            "seniority_level": str
        }
    """
    if not raw_title or not isinstance(raw_title, str) or not raw_title.strip():
        return {
            "original_title": raw_title or "",
            "normalized_title": "Unspecified Role",
            "seniority_level": "Unspecified",
        }

    title = raw_title.strip()

    # Extract seniority before token normalization
    seniority = extract_seniority(title)

    # Expand common abbreviations
    cleaned = title
    for pattern, replacement in ABBREVIATION_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)

    # Clean up excess whitespace and punctuation
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s*([,\-\/|])\s*", r" \1 ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Ensure canonical title capitalization if all uppercase
    if cleaned.isupper() and len(cleaned) > 5:
        cleaned = cleaned.title()

    return {
        "original_title": title,
        "normalized_title": cleaned,
        "seniority_level": seniority,
    }

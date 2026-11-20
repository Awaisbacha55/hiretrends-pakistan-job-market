"""HireTrends Workplace Arrangement Normalizer.

Standardizes workplace classifications into 'remote', 'hybrid', or 'on-site'.
Preserves unstated workplace arrangements as unknown (None) without guessing.
"""

import re
from typing import Optional

REMOTE_PATTERN = re.compile(r"\b(remote|work\s+from\s+home|wfh|telecommute|fully\s+remote)\b", re.IGNORECASE)
HYBRID_PATTERN = re.compile(r"\b(hybrid|flexible\s+work|partially\s+remote)\b", re.IGNORECASE)
ONSITE_PATTERN = re.compile(r"\b(in[\s\-]?person|on[\s\-]?site|in[\s\-]?office|office[\s\-]?based)\b", re.IGNORECASE)


def normalize_workplace_type(
    raw_workplace: Optional[str],
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[str]:
    """Normalize workplace arrangement.

    Args:
        raw_workplace: Explicit workplace attribute from API.
        title: Job title (checked if raw is missing).
        description: Job description snippet (checked if raw is missing).

    Returns:
        'remote', 'hybrid', 'on-site', or None if unknown.
    """
    if raw_workplace and isinstance(raw_workplace, str):
        clean = raw_workplace.strip().lower()
        if clean in ("remote", "telecommute", "wfh"):
            return "remote"
        if clean in ("hybrid", "flexible"):
            return "hybrid"
        if clean in ("in_person", "in-person", "in person", "on-site", "onsite", "office"):
            return "on-site"

    # Check title explicitly
    if title and isinstance(title, str):
        if HYBRID_PATTERN.search(title):
            return "hybrid"
        if REMOTE_PATTERN.search(title):
            return "remote"
        if ONSITE_PATTERN.search(title):
            return "on-site"

    # Do NOT infer remote merely because location is unspecified
    return None

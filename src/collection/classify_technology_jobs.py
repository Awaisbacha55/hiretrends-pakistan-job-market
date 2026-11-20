"""HireTrends Technology Job Classifier.

Classifies recruitment postings into 16 standardized technology and non-technology
categories based on job titles and description content using transparent keyword/regex heuristics,
confidence thresholds, and explicit manual-review flagging.
"""

import re
from typing import Any, Dict, Optional, Tuple

CATEGORIES = [
    "Software Engineering",
    "Backend Development",
    "Frontend Development",
    "Full Stack Development",
    "Data Analytics",
    "Data Science",
    "Artificial Intelligence / Machine Learning",
    "Cloud Engineering",
    "DevOps / SRE",
    "Cybersecurity",
    "QA / Software Testing",
    "Database Engineering",
    "Networking",
    "Other Technology",
    "Non-Technology",
    "Uncertain / Manual Review",
]

# Title regex patterns in priority order
TITLE_RULES = [
    # Full Stack
    (
        "Full Stack Development",
        re.compile(r"\b(full[\s\-]?stack|mern|mean|lamp)\b", re.IGNORECASE),
        "Job title specifies full-stack / multi-tier engineering",
        0.95,
    ),
    # Frontend
    (
        "Frontend Development",
        re.compile(r"\b(frontend|front[\s\-]?end|react|vue|angular|ui[\s\/]ux developer|flutter|ios developer|android developer|mobile developer)\b", re.IGNORECASE),
        "Job title indicates client-side, mobile, or front-end engineering",
        0.95,
    ),
    # Backend
    (
        "Backend Development",
        re.compile(r"\b(backend|back[\s\-]?end|python developer|django|node\.?js|laravel|php developer|java developer|golang|spring boot|\.net developer|c# developer)\b", re.IGNORECASE),
        "Job title indicates server-side or backend software engineering",
        0.95,
    ),
    # AI / Machine Learning
    (
        "Artificial Intelligence / Machine Learning",
        re.compile(r"\b(machine learning|ai developer|ai engineer|ml engineer|deep learning|nlp engineer|computer vision|genai|llm engineer|data science & ai)\b", re.IGNORECASE),
        "Job title specifies artificial intelligence or machine learning specialty",
        0.95,
    ),
    # Data Science
    (
        "Data Science",
        re.compile(r"\b(data scientist|applied scientist|data science|statistician)\b", re.IGNORECASE),
        "Job title indicates predictive modeling or data science",
        0.95,
    ),
    # Data Analytics & Engineering
    (
        "Data Analytics",
        re.compile(r"\b(data engineer|data analyst|business intelligence|bi developer|etl developer|power bi|tableau|analytics engineer)\b", re.IGNORECASE),
        "Job title indicates data analytics, warehousing, or business intelligence",
        0.95,
    ),
    # DevOps / SRE
    (
        "DevOps / SRE",
        re.compile(r"\b(devops|site reliability|sre|platform engineer|ci[\s\/]cd engineer|build engineer)\b", re.IGNORECASE),
        "Job title indicates deployment automation, platform engineering, or SRE",
        0.95,
    ),
    # Cloud Engineering
    (
        "Cloud Engineering",
        re.compile(r"\b(cloud engineer|cloud architect|aws engineer|azure engineer|gcp engineer)\b", re.IGNORECASE),
        "Job title specifies cloud infrastructure or cloud solutions architecture",
        0.95,
    ),
    # Cybersecurity
    (
        "Cybersecurity",
        re.compile(r"\b(cyber[\s\-]?security|security analyst|infosec|soc analyst|penetration tester|ethical hacker|security engineer)\b", re.IGNORECASE),
        "Job title specifies cybersecurity or information defense",
        0.95,
    ),
    # QA / Software Testing
    (
        "QA / Software Testing",
        re.compile(r"\b(qa|quality assurance|software test|sqa|automation tester|test engineer|sdet)\b", re.IGNORECASE),
        "Job title specifies software quality assurance or testing",
        0.95,
    ),
    # Database Engineering
    (
        "Database Engineering",
        re.compile(r"\b(database administrator|dba|database engineer|sql developer|oracle dba)\b", re.IGNORECASE),
        "Job title specifies database administration or SQL architecture",
        0.95,
    ),
    # Networking
    (
        "Networking",
        re.compile(r"\b(network engineer|network administrator|ccna|ccnp|telecom engineer|telecommunications)\b", re.IGNORECASE),
        "Job title specifies networking or telecommunications engineering",
        0.90,
    ),
    # General Software Engineering
    (
        "Software Engineering",
        re.compile(r"\b(software engineer|software developer|programmer|coder|tech lead|engineering manager|solution architect|cto|principal engineer)\b", re.IGNORECASE),
        "Job title indicates core software engineering or technical leadership",
        0.90,
    ),
    # Other Technology
    (
        "Other Technology",
        re.compile(r"\b(scrum master|agile coach|product manager|it support|helpdesk|systems administrator|sysadmin|technical writer|game developer|firmware|embedded)\b", re.IGNORECASE),
        "Job title represents IT, technology operations, or embedded development",
        0.85,
    ),
    # Definite Non-Technology Roles
    (
        "Non-Technology",
        re.compile(r"\b(accountant|accounting|audit|auditor|sales|marketing|recruiter|hr|human resources|finance|supply chain|logistics|driver|cook|security guard|receptionist|telemarketer|call center|customer support representative|csr|customer service|graphic designer|content writer|operations executive|store manager|cashier|freight|warehouse|mechanic|tailor|waiter|nurse|doctor|pharmacist|teacher|lecturer|professor|legal|counsel)\b", re.IGNORECASE),
        "Job title matches a known non-technology, business, or operational occupation",
        0.90,
    ),
]

TECH_KEYWORDS_IN_DESC = re.compile(
    r"\b(python|javascript|typescript|react|angular|vue|django|flask|fastapi|docker|kubernetes|aws|azure|gcp|sql|nosql|mongodb|postgresql|git|ci[\s\/]cd|machine learning|c\+\+|c\#|java|rest api|linux)\b",
    re.IGNORECASE,
)


def classify_job(
    title: Optional[str],
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Classify a recruitment posting into a standardized technology category.

    Args:
        title: The job listing title.
        description: The job description text.

    Returns:
        {
            "is_technology_job": bool,
            "technology_category": str,
            "classification_reason": str,
            "classification_confidence": float,
            "needs_manual_review": bool
        }
    """
    clean_title = (title or "").strip()
    clean_desc = (description or "").strip()

    if not clean_title and not clean_desc:
        return {
            "is_technology_job": False,
            "technology_category": "Uncertain / Manual Review",
            "classification_reason": "Listing lacks both title and description text",
            "classification_confidence": 0.0,
            "needs_manual_review": True,
        }

    # Step 1: Evaluate Title against High-Confidence Rules
    if clean_title:
        for cat, pattern, reason, conf in TITLE_RULES:
            if pattern.search(clean_title):
                is_tech = cat != "Non-Technology"
                return {
                    "is_technology_job": is_tech,
                    "technology_category": cat,
                    "classification_reason": f"{reason} (matched title: '{clean_title}')",
                    "classification_confidence": conf,
                    "needs_manual_review": False,
                }

    # Step 2: Evaluate Description Content if Title was not decisive
    if clean_desc:
        tech_matches = TECH_KEYWORDS_IN_DESC.findall(clean_desc)
        if len(tech_matches) >= 3:
            matched_terms = list(set([m.lower() for m in tech_matches[:5]]))
            return {
                "is_technology_job": True,
                "technology_category": "Other Technology",
                "classification_reason": f"Description contains dense technical stack ({', '.join(matched_terms)})",
                "classification_confidence": 0.75,
                "needs_manual_review": False,
            }

    # Step 3: Flag ambiguous titles for manual review rather than silently defaulting to non-tech
    # If the title is generic or ambiguous (e.g., "Officer", "Associate", "Manager", "Consultant", "Specialist")
    ambiguous_tokens = re.search(r"\b(officer|associate|executive|consultant|specialist|coordinator|trainee|analyst|intern|advisor|lead|director)\b", clean_title, re.IGNORECASE)
    if ambiguous_tokens:
        return {
            "is_technology_job": False,
            "technology_category": "Uncertain / Manual Review",
            "classification_reason": f"Ambiguous role title '{clean_title}' requires manual review",
            "classification_confidence": 0.45,
            "needs_manual_review": True,
        }

    # Non-matched general title: classify as Non-Technology with medium confidence
    if clean_title:
        return {
            "is_technology_job": False,
            "technology_category": "Non-Technology",
            "classification_reason": f"Title '{clean_title}' did not match tech taxonomy",
            "classification_confidence": 0.65,
            "needs_manual_review": False,
        }

    return {
        "is_technology_job": False,
        "technology_category": "Uncertain / Manual Review",
        "classification_reason": "Insufficient indicators for definitive classification",
        "classification_confidence": 0.30,
        "needs_manual_review": True,
    }

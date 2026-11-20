"""HireTrends Workplace Arrangement Analysis Engine.

Analyzes workplace distributions (Remote, On-site, Hybrid) while strictly
preserving unknown/unspecified entries and computing proportions using only
known records as the primary denominator.
"""

from typing import Any, Dict, List
import pandas as pd


def analyze_workplace_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate normalized workplace arrangement metrics.

    Rule: Percentages of workplace types must be calculated using only known
    workplace classifications as denominator, while reporting the unknown
    count separately.
    """
    total_listings = len(df)
    known_df = df[df["workplace_type"].notna() & (df["workplace_type"] != "")].copy()
    known_count = len(known_df)
    unknown_count = total_listings - known_count

    if known_count == 0:
        return {
            "total_listings": total_listings,
            "known_workplace_count": 0,
            "unknown_workplace_count": unknown_count,
            "known_rate_pct": 0.0,
            "distribution": {},
        }

    counts = known_df["workplace_type"].str.lower().value_counts().to_dict()

    remote_count = counts.get("remote", 0)
    onsite_count = counts.get("on-site", 0)
    hybrid_count = counts.get("hybrid", 0)

    distribution = {
        "remote": {
            "count": remote_count,
            "pct_of_known": round(remote_count / known_count * 100, 2),
            "pct_of_all_postings": round(remote_count / total_listings * 100, 2),
        },
        "on-site": {
            "count": onsite_count,
            "pct_of_known": round(onsite_count / known_count * 100, 2),
            "pct_of_all_postings": round(onsite_count / total_listings * 100, 2),
        },
        "hybrid": {
            "count": hybrid_count,
            "pct_of_known": round(hybrid_count / known_count * 100, 2),
            "pct_of_all_postings": round(hybrid_count / total_listings * 100, 2),
        },
    }

    # Workplace distribution within Technology Jobs specifically
    tech_known_df = known_df[known_df["is_technology_job"] == True]
    tech_known_count = len(tech_known_df)
    tech_distribution = {}

    if tech_known_count > 0:
        tech_counts = tech_known_df["workplace_type"].str.lower().value_counts().to_dict()
        for wp_type in ["remote", "on-site", "hybrid"]:
            c = tech_counts.get(wp_type, 0)
            tech_distribution[wp_type] = {
                "count": c,
                "pct_of_known_tech": round(c / tech_known_count * 100, 2),
            }

    return {
        "total_listings": total_listings,
        "known_workplace_count": known_count,
        "unknown_workplace_count": unknown_count,
        "known_rate_pct": round(known_count / total_listings * 100, 2),
        "unknown_rate_pct": round(unknown_count / total_listings * 100, 2),
        "distribution": distribution,
        "technology_workplace_distribution": tech_distribution,
    }

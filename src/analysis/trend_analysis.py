"""HireTrends Trend & Longitudinal Growth Analysis Engine.

Provides an extensible statistical framework for calculating skill demand growth,
month-over-month shifts, and emerging/declining technologies across sequential snapshots.
Explicitly flags single-snapshot limitations without fabricating growth percentages.
"""

from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from .skills_analysis import parse_job_skills


def analyze_skill_growth(
    snapshots: Optional[List[Dict[str, Any]]] = None,
    current_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Calculate longitudinal skill growth across temporal observation snapshots.

    Methodological Invariant:
    A single point-in-time snapshot cannot establish growth, velocity, or trends.
    If fewer than 2 valid sequential snapshots exist, this function returns an
    explicit 'UNAVAILABLE_INSUFFICIENT_SNAPSHOTS' status rather than fabricating growth.
    """
    if not snapshots or len(snapshots) < 2:
        return {
            "status": "UNAVAILABLE_INSUFFICIENT_SNAPSHOTS",
            "available_snapshots_count": len(snapshots) if snapshots else (1 if current_df is not None else 0),
            "reason": (
                "Statistically rigorous skill growth, month-over-month trajectory, and velocity "
                "require at least two independent, chronologically distinct observation periods. "
                "Current repository contains a single verified Headcount Labs API snapshot (Nov 20, 2026). "
                "Historical Open Data Pakistan data (2019-2021) has an incompatible schema without standardized skill fields."
            ),
            "growth_metrics_available": False,
            "extensible_fields_supported": [
                "weekly_posting_volume",
                "month_over_month_change",
                "percentage_growth",
                "emerging_skills",
                "declining_skills",
            ],
            "methodology_guideline": (
                "When future weekly or monthly snapshots are ingested into data/raw/headcount/, "
                "this module will compute delta = (current_count - previous_count) / previous_count * 100."
            ),
        }

    # If 2 or more snapshots exist, sort by timestamp
    sorted_snapshots = sorted(snapshots, key=lambda s: s.get("timestamp", ""))
    t0_snap = sorted_snapshots[-2]
    t1_snap = sorted_snapshots[-1]

    t0_df = t0_snap["dataframe"]
    t1_df = t1_snap["dataframe"]

    # Compute unique job counts per skill
    def get_skill_counts(df: pd.DataFrame) -> Counter:
        counts: Counter = Counter()
        for _, row in df.iterrows():
            skills = parse_job_skills(row.get("skills"))
            for s in skills:
                counts[s] += 1
        return counts

    c0 = get_skill_counts(t0_df)
    c1 = get_skill_counts(t1_df)

    all_skills = sorted(list(set(c0.keys()) | set(c1.keys())))
    growth_results = []
    emerging = []
    declining = []

    for s in all_skills:
        prev = c0.get(s, 0)
        curr = c1.get(s, 0)
        abs_delta = curr - prev
        pct_growth = round((abs_delta / prev * 100), 2) if prev > 0 else (100.0 if curr > 0 else 0.0)

        entry = {
            "skill": s,
            "previous_count": prev,
            "current_count": curr,
            "absolute_change": abs_delta,
            "percentage_growth": pct_growth,
        }
        growth_results.append(entry)

        if prev == 0 and curr >= 3:
            emerging.append(s)
        elif prev >= 5 and curr < prev:
            declining.append(s)

    growth_results.sort(key=lambda x: x["percentage_growth"], reverse=True)

    return {
        "status": "SUCCESS",
        "growth_metrics_available": True,
        "baseline_period": t0_snap.get("timestamp"),
        "comparison_period": t1_snap.get("timestamp"),
        "total_skills_tracked": len(all_skills),
        "fastest_growing_skills": growth_results[:10],
        "fastest_declining_skills": sorted(growth_results, key=lambda x: x["percentage_growth"])[:10],
        "emerging_skills": emerging,
        "declining_skills": declining,
    }

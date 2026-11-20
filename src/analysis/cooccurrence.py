"""HireTrends Skill Co-occurrence Analysis Engine.

Computes pairwise technical skill co-occurrences across unique job postings,
identifies dominant technical stack combinations, and constructs symmetric
co-occurrence matrices suitable for graph and heatmap visualizations.
"""

from collections import Counter
import itertools
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from .skills_analysis import parse_job_skills


def compute_skill_cooccurrence(
    df: pd.DataFrame,
    top_n_pairs: int = 30,
    matrix_top_skills: int = 15,
) -> Dict[str, Any]:
    """Calculate skill pair co-occurrences across unique job postings.

    Guarantees:
    - Counts unique job IDs containing both skills, not duplicate word mentions.
    - Symmetric matrix is ordered by top skill prevalence.
    """
    total_jobs = len(df)
    pair_counts: Counter = Counter()
    skill_job_counts: Counter = Counter()

    # Pre-parse skills per job ID
    job_skills_map = {}
    for _, row in df.iterrows():
        jid = row.get("job_id")
        skills = parse_job_skills(row.get("skills"))
        if not jid:
            continue
        # Unique skills within this job
        unique_skills = sorted(list(set(skills)))
        job_skills_map[jid] = unique_skills

        for s in unique_skills:
            skill_job_counts[s] += 1

        # Generate all distinct pairs for this job
        for s1, s2 in itertools.combinations(unique_skills, 2):
            pair_key = (min(s1, s2), max(s1, s2))
            pair_counts[pair_key] += 1

    # Format top pairs
    top_pairs = []
    for rank, ((s1, s2), count) in enumerate(pair_counts.most_common(top_n_pairs), start=1):
        s1_count = skill_job_counts.get(s1, count)
        s2_count = skill_job_counts.get(s2, count)
        # Jaccard similarity index = intersection / union
        union_size = s1_count + s2_count - count
        jaccard = round(count / max(union_size, 1), 3)

        top_pairs.append({
            "rank": rank,
            "skill_a": s1,
            "skill_b": s2,
            "pair_name": f"{s1} + {s2}",
            "cooccurrence_count": count,
            "pct_of_all_jobs": round(count / total_jobs * 100, 2),
            "jaccard_similarity": jaccard,
        })

    # Build symmetric co-occurrence matrix for the top N skills
    top_skills_for_matrix = [s for s, _ in skill_job_counts.most_common(matrix_top_skills)]
    matrix_size = len(top_skills_for_matrix)
    matrix = np.zeros((matrix_size, matrix_size), dtype=int)

    for i, s1 in enumerate(top_skills_for_matrix):
        for j, s2 in enumerate(top_skills_for_matrix):
            if i == j:
                matrix[i][j] = skill_job_counts[s1]
            else:
                pair_key = (min(s1, s2), max(s1, s2))
                matrix[i][j] = pair_counts.get(pair_key, 0)

    matrix_df = pd.DataFrame(matrix, index=top_skills_for_matrix, columns=top_skills_for_matrix)

    return {
        "total_jobs_evaluated": total_jobs,
        "total_unique_skills": len(skill_job_counts),
        "total_distinct_pairs": len(pair_counts),
        "top_cooccurring_pairs": top_pairs,
        "matrix_skills": top_skills_for_matrix,
        "cooccurrence_matrix": matrix_df.to_dict(),
        "cooccurrence_matrix_records": matrix_df.reset_index().to_dict(orient="records"),
    }

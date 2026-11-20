"""HireTrends Skills and Roles Demand Analysis Engine.

Extracts aggregated skill demand metrics across unique job postings,
segmented by technology category, seniority level, domain clusters, and target roles.
"""

from collections import Counter
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd


def parse_job_skills(skills_val: Union[str, list, None]) -> List[str]:
    """Parse skill representation into a unique list of string names."""
    if skills_val is None or (isinstance(skills_val, float) and pd.isna(skills_val)):
        return []
    if isinstance(skills_val, list):
        return sorted(list(set(str(s) for s in skills_val if s)))
    if isinstance(skills_val, str):
        try:
            parsed = json.loads(skills_val)
            if isinstance(parsed, list):
                return sorted(list(set(str(s) for s in parsed if s)))
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def get_top_skills(
    df: pd.DataFrame,
    n: int = 20,
    tech_only: bool = False,
) -> List[Dict[str, Any]]:
    """Calculate the top N most in-demand skills by unique job postings count.

    Important: Counts unique job postings requiring the skill, not repeated word mentions.
    """
    sub_df = df[df["is_technology_job"] == True] if tech_only else df
    total_jobs = len(sub_df)
    if total_jobs == 0:
        return []

    # Map each skill to unique job postings
    skill_job_counts: Counter = Counter()
    for _, row in sub_df.iterrows():
        skills = parse_job_skills(row.get("skills"))
        for s in skills:
            skill_job_counts[s] += 1

    top_list = []
    for rank, (skill, count) in enumerate(skill_job_counts.most_common(n), start=1):
        top_list.append({
            "rank": rank,
            "skill": skill,
            "job_count": count,
            "percentage_of_jobs": round(count / total_jobs * 100, 2),
            "total_evaluated_jobs": total_jobs,
        })
    return top_list


def get_skills_by_category(
    df: pd.DataFrame,
    top_n: int = 5,
) -> Dict[str, List[Dict[str, Any]]]:
    """Extract top skills demanded for each technology taxonomy category."""
    results = {}
    valid_categories = df["technology_category"].dropna().unique()

    for cat in sorted(valid_categories):
        cat_df = df[df["technology_category"] == cat]
        cat_total = len(cat_df)
        if cat_total < 5:
            continue

        skill_counter: Counter = Counter()
        for _, row in cat_df.iterrows():
            for s in parse_job_skills(row.get("skills")):
                skill_counter[s] += 1

        top_skills = [
            {
                "skill": s,
                "count": c,
                "percentage": round(c / cat_total * 100, 1),
            }
            for s, c in skill_counter.most_common(top_n)
        ]
        results[cat] = top_skills
    return results


def get_skills_by_seniority(
    df: pd.DataFrame,
    top_n: int = 8,
) -> Dict[str, Dict[str, Any]]:
    """Extract skills demanded across seniority tiers."""
    results = {}
    seniority_levels = ["Junior / Entry-Level", "Mid-Level", "Senior", "Lead / Principal", "Executive / Director"]

    for sen in seniority_levels:
        sen_df = df[df["seniority_level"] == sen]
        total = len(sen_df)
        if total == 0:
            continue

        skill_counter: Counter = Counter()
        for _, row in sen_df.iterrows():
            for s in parse_job_skills(row.get("skills")):
                skill_counter[s] += 1

        results[sen] = {
            "total_jobs": total,
            "top_skills": [
                {"skill": s, "count": c, "percentage": round(c / total * 100, 1)}
                for s, c in skill_counter.most_common(top_n)
            ],
        }
    return results


def get_domain_skill_demand(df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """Analyze demand for specific domain clusters (Languages, Cloud/DevOps, AI/ML)."""
    domains = {
        "Programming Languages": [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "PHP",
            "Go", "Ruby", "Swift", "Kotlin", "Rust", "SQL", "HTML", "CSS",
        ],
        "Cloud & DevOps": [
            "AWS", "Microsoft Azure", "Google Cloud Platform", "Docker",
            "Kubernetes", "CI/CD", "Terraform", "Linux", "Git",
        ],
        "AI & Machine Learning": [
            "Machine Learning", "Deep Learning", "Large Language Models",
            "PyTorch", "TensorFlow", "NLP", "Computer Vision",
            "Generative AI", "LangChain", "OpenAI",
        ],
        "Databases & Big Data": [
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "Apache Spark", "Snowflake", "Elasticsearch",
        ],
    }

    total_jobs = len(df)
    tech_jobs = int((df["is_technology_job"] == True).sum())
    results = {}

    # Pre-parse all skills for quick membership tests
    all_parsed_skills = [set(parse_job_skills(s)) for s in df["skills"]]

    for domain_name, target_skills in domains.items():
        domain_stats = []
        for s in target_skills:
            # Count job postings with this skill
            count = sum(1 for job_skills in all_parsed_skills if s in job_skills)
            domain_stats.append({
                "skill": s,
                "job_count": count,
                "pct_of_all_jobs": round(count / total_jobs * 100, 2),
                "pct_of_tech_jobs": round(count / max(tech_jobs, 1) * 100, 2),
            })
        # Sort descending by job count
        domain_stats.sort(key=lambda x: x["job_count"], reverse=True)
        results[domain_name] = domain_stats

    return results


# Role patterns mapped to target occupations
TARGET_ROLES = {
    "Software Engineer": re.compile(r"\bsoftware\s*(?:engineer|developer)\b|\bsde\b|\bswe\b", re.IGNORECASE),
    "Python Developer": re.compile(r"\bpython\s*(?:developer|engineer|programmer)\b|\b(?:senior|junior|lead|staff)?\s*python\b", re.IGNORECASE),
    "Backend Developer": re.compile(r"\bback[\s-]?end\s*(?:engineer|developer)\b", re.IGNORECASE),
    "Frontend Developer": re.compile(r"\bfront[\s-]?end\s*(?:engineer|developer)\b", re.IGNORECASE),
    "Full Stack Developer": re.compile(r"\bfull[\s-]?stack\s*(?:engineer|developer)\b", re.IGNORECASE),
    "Data Analyst": re.compile(r"\bdata\s*analyst\b|\bbusiness\s*intelligence\s*analyst\b", re.IGNORECASE),
    "Data Scientist": re.compile(r"\bdata\s*scientist\b", re.IGNORECASE),
    "Machine Learning Engineer": re.compile(r"\bmachine\s*learning\s*(?:engineer|specialist)\b|\bml\s*engineer\b", re.IGNORECASE),
    "AI Engineer": re.compile(r"\bai\s*(?:engineer|developer|researcher)\b|\bartificial\s*intelligence\b", re.IGNORECASE),
    "DevOps Engineer": re.compile(r"\bdevops\s*(?:engineer|specialist)\b|\bsite\s*reliability\s*engineer\b|\bsre\b", re.IGNORECASE),
    "Cloud Engineer": re.compile(r"\bcloud\s*(?:engineer|architect|specialist)\b", re.IGNORECASE),
    "Cybersecurity Engineer": re.compile(r"\bcyber\s*security\b|\binformation\s*security\b|\bsecurity\s*engineer\b", re.IGNORECASE),
}


def get_skills_by_role(
    df: pd.DataFrame,
    top_n: int = 10,
) -> Dict[str, Dict[str, Any]]:
    """Analyze the top skills required for 12 key technology occupations.

    Always reports actual sample size (total matching job postings).
    """
    results = {}

    for role_name, pattern in TARGET_ROLES.items():
        # Match against normalized_title or original job_title
        match_mask = (
            df["normalized_title"].str.contains(pattern, na=False) |
            df["job_title"].str.contains(pattern, na=False)
        )
        role_df = df[match_mask]
        sample_size = len(role_df)

        skill_counter: Counter = Counter()
        for _, row in role_df.iterrows():
            for s in parse_job_skills(row.get("skills")):
                skill_counter[s] += 1

        top_skills = [
            {
                "skill": s,
                "count": c,
                "percentage": round(c / sample_size * 100, 1) if sample_size > 0 else 0.0,
            }
            for s, c in skill_counter.most_common(top_n)
        ]

        results[role_name] = {
            "sample_size": sample_size,
            "has_sufficient_records": sample_size >= 5,
            "top_skills": top_skills,
        }

    return results

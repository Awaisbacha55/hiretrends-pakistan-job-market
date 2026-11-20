"""HireTrends Exploratory Data Analysis & Market Intelligence Subsystem.

Provides statistical modeling, salary benchmarking, geographic clustering,
workplace arrangement analytics, skill taxonomy distributions, and pair co-occurrence.
"""

from .cooccurrence import compute_skill_cooccurrence
from .location_analysis import analyze_locations
from .salary_analysis import analyze_salary_data
from .skills_analysis import (
    get_domain_skill_demand,
    get_skills_by_category,
    get_skills_by_role,
    get_skills_by_seniority,
    get_top_skills,
    parse_job_skills,
)
from .trend_analysis import analyze_skill_growth
from .workplace_analysis import analyze_workplace_distribution

__all__ = [
    "get_top_skills",
    "get_skills_by_category",
    "get_skills_by_seniority",
    "get_domain_skill_demand",
    "get_skills_by_role",
    "analyze_salary_data",
    "analyze_locations",
    "analyze_workplace_distribution",
    "compute_skill_cooccurrence",
    "analyze_skill_growth",
    "parse_job_skills",
]

"""HireTrends Dashboard Shared Data Loader & Filtering Utility.

Provides cached data ingestion, validation of schema invariants,
safe parsing of skill arrays, and global multi-criteria filtering.
"""

import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Union
import numpy as np
import pandas as pd
import streamlit as st

EXPECTED_COLUMNS = [
    "job_id",
    "job_title",
    "normalized_title",
    "seniority_level",
    "company",
    "city",
    "normalized_city",
    "region",
    "country",
    "is_pakistan_location",
    "country_classification",
    "workplace_type",
    "experience_min_years",
    "experience_max_years",
    "salary_text",
    "salary_currency",
    "salary_interval",
    "salary_min_pkr",
    "salary_max_pkr",
    "salary_is_converted",
    "skills",
    "skills_count",
    "is_technology_job",
    "technology_category",
    "classification_confidence",
    "needs_manual_review",
    "posted_date",
    "source",
]


@st.cache_data(show_spinner=False)
def load_clean_data(csv_path: Optional[str] = None) -> pd.DataFrame:
    """Load, validate, and enrich cleaned HireTrends dataset.

    Guarantees:
    - Never exposes raw employer descriptions.
    - Missing values are strictly retained as NaN/None.
    - Skills are parsed into list objects for fast downstream evaluation.
    """
    if csv_path is None or csv_path == "data/processed/jobs_cleaned.csv":
        repo_root = Path(__file__).resolve().parent.parent
        resolved = repo_root / "data" / "processed" / "jobs_cleaned.csv"
        if resolved.exists():
            csv_path = str(resolved)
        else:
            csv_path = "data/processed/jobs_cleaned.csv"

    if not os.path.exists(csv_path):
        # Fallback empty DataFrame with schema
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = pd.read_csv(csv_path, low_memory=False)

    # Validate essential columns exist
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    # Parse skills JSON column
    def safe_parse_skills(val: Any) -> List[str]:
        if pd.isna(val) or val is None or val == "":
            return []
        if isinstance(val, list):
            return [str(s) for s in val if s]
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(s) for s in parsed if s]
            except (json.JSONDecodeError, TypeError):
                pass
        return []

    df["parsed_skills"] = df["skills"].apply(safe_parse_skills)

    # Convenience helper columns
    df["has_salary"] = df["salary_min_pkr"].notna()
    df["has_experience"] = df["experience_min_years"].notna()

    # Experience bracket categorization
    def categorize_exp(years: Any) -> str:
        if pd.isna(years) or years is None:
            return "Unspecified"
        y = float(years)
        if y <= 1.0:
            return "Entry / Junior (0-1 yrs)"
        elif y <= 4.0:
            return "Mid-Level (2-4 yrs)"
        else:
            return "Senior (5+ yrs)"

    df["experience_bracket"] = df["experience_min_years"].apply(categorize_exp)

    # Clean workplace arrangement representation
    df["workplace_display"] = df["workplace_type"].fillna("Unspecified").str.capitalize()

    # Ensure country_classification is populated even for legacy/mock DataFrames
    if "country_classification" not in df.columns or df["country_classification"].isna().all():
        df["country_classification"] = np.where(
            df["is_pakistan_location"] == True,
            "Pakistan",
            np.where(df["country"].notna() & (df["country"].astype(str).str.strip() != ""), "Foreign", "Unknown"),
        )

    return df


SCOPE_OPTIONS = [
    "Confirmed Pakistan Tech",
    "Pakistan-Only (All Roles)",
    "All Deduplicated Records",
    "Foreign Records Only",
    "Non-Technology Records",
    "Uncertain / Manual Review",
    "Unknown Country Records",
]


def apply_global_filters(
    df: pd.DataFrame,
    scope: str = "Confirmed Pakistan Tech",
    category: Optional[str] = None,
    city: Optional[str] = None,
    workplace: Optional[str] = None,
    experience_bracket: Optional[str] = None,
    salary_only: bool = False,
    tech_only: bool = False,
    role_keyword: Optional[str] = None,
) -> pd.DataFrame:
    """Filter DataFrame according to dataset scope and interactive global criteria."""
    filtered = df.copy()

    # Ensure country_classification exists on test/mock DataFrames
    if "country_classification" not in filtered.columns:
        filtered["country_classification"] = np.where(
            filtered["is_pakistan_location"] == True,
            "Pakistan",
            np.where(
                filtered["country"].notna() & (filtered["country"].astype(str).str.strip() != ""),
                "Foreign",
                "Unknown",
            ),
        )

    if scope == "Confirmed Pakistan Tech":
        filtered = filtered[
            (filtered["country_classification"] == "Pakistan") &
            (filtered["is_technology_job"] == True)
        ]
    elif scope == "Pakistan-Only (All Roles)":
        filtered = filtered[filtered["country_classification"] == "Pakistan"]
    elif scope == "Foreign Records Only":
        filtered = filtered[filtered["country_classification"] == "Foreign"]
    elif scope == "Non-Technology Records":
        filtered = filtered[filtered["technology_category"] == "Non-Technology"]
    elif scope == "Uncertain / Manual Review":
        filtered = filtered[filtered["needs_manual_review"] == True]
    elif scope == "Unknown Country Records":
        filtered = filtered[filtered["country_classification"] == "Unknown"]

    if tech_only:
        filtered = filtered[filtered["is_technology_job"] == True]

    if category and category != "All Categories":
        filtered = filtered[filtered["technology_category"] == category]

    if city and city != "All Cities":
        filtered = filtered[filtered["normalized_city"] == city]

    if workplace and workplace != "All Workplaces":
        filtered = filtered[filtered["workplace_display"] == workplace]

    if experience_bracket and experience_bracket != "All Levels":
        filtered = filtered[filtered["experience_bracket"] == experience_bracket]

    if salary_only:
        filtered = filtered[filtered["has_salary"] == True]

    if role_keyword and role_keyword.strip():
        kw = role_keyword.strip()
        pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
        match_mask = (
            filtered["normalized_title"].fillna("").str.contains(pattern) |
            filtered["job_title"].fillna("").str.contains(pattern)
        )
        filtered = filtered[match_mask]

    return filtered


def format_pkr(val: Optional[float], compact: bool = False) -> str:
    """Format numeric value as Pakistani Rupee currency string."""
    if val is None or pd.isna(val) or val <= 0:
        return "N/A"
    if compact:
        if val >= 1_000_000:
            return f"PKR {val / 1_000_000:.2f}M"
        elif val >= 1_000:
            return f"PKR {val / 1_000:.1f}k"
    return f"PKR {val:,.0f}"


def format_pct(val: Union[int, float]) -> str:
    """Format decimal or percentage value cleanly."""
    if val is None or pd.isna(val):
        return "0.0%"
    return f"{float(val):.1f}%"


def format_number(val: Union[int, float]) -> str:
    """Format integer with thousands separator."""
    if val is None or pd.isna(val):
        return "0"
    return f"{int(val):,}"

"""HireTrends Unit Test Suite — Day 5 Streamlit Dashboard Pipeline.

Tests data ingestion, schema validation, global multi-criteria filtering,
role extraction, numeric and currency formatters, and empty-state robustness.
"""

import numpy as np
import pandas as pd
import pytest

from dashboard.data_loader import (
    EXPECTED_COLUMNS,
    apply_global_filters,
    format_number,
    format_pct,
    format_pkr,
    load_clean_data,
)
from src.analysis.skills_analysis import TARGET_ROLES


@pytest.fixture
def sample_dashboard_df() -> pd.DataFrame:
    """Fixture providing a mock dashboard DataFrame."""
    records = [
        {
            "job_id": "dash-001",
            "job_title": "Senior Python Engineer",
            "normalized_title": "Senior Python Engineer",
            "seniority_level": "Senior",
            "company": "Alpha Tech",
            "city": "Lahore",
            "normalized_city": "Lahore",
            "region": "Punjab",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "remote",
            "experience_min_years": 5.0,
            "experience_max_years": None,
            "salary_text": "USD 2,000",
            "salary_currency": "USD",
            "salary_interval": "monthly",
            "salary_min_pkr": 557000.0,
            "salary_max_pkr": 557000.0,
            "salary_is_converted": True,
            "skills": '["Python", "AWS", "Docker"]',
            "skills_count": 3,
            "is_technology_job": True,
            "technology_category": "Software Engineering",
            "classification_confidence": 0.95,
            "needs_manual_review": False,
            "posted_date": "2026-11-15",
            "source": "headcount_labs",
        },
        {
            "job_id": "dash-002",
            "job_title": "Junior Data Analyst",
            "normalized_title": "Junior Data Analyst",
            "seniority_level": "Junior / Entry-Level",
            "company": "Beta Analytics",
            "city": "Karachi",
            "normalized_city": "Karachi",
            "region": "Sindh",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "on-site",
            "experience_min_years": 1.0,
            "experience_max_years": 2.0,
            "salary_text": "PKR 80,000",
            "salary_currency": "PKR",
            "salary_interval": "monthly",
            "salary_min_pkr": 80000.0,
            "salary_max_pkr": 80000.0,
            "salary_is_converted": False,
            "skills": '["SQL", "Excel", "Power BI"]',
            "skills_count": 3,
            "is_technology_job": True,
            "technology_category": "Data Analytics",
            "classification_confidence": 0.90,
            "needs_manual_review": False,
            "posted_date": "2026-11-18",
            "source": "headcount_labs",
        },
        {
            "job_id": "dash-003",
            "job_title": "HR Manager",
            "normalized_title": "HR Manager",
            "seniority_level": "Mid-Level",
            "company": "Corp Org",
            "city": "Islamabad",
            "normalized_city": "Islamabad",
            "region": "Islamabad",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "hybrid",
            "experience_min_years": 3.0,
            "experience_max_years": 4.0,
            "salary_text": None,
            "salary_currency": None,
            "salary_interval": None,
            "salary_min_pkr": None,
            "salary_max_pkr": None,
            "salary_is_converted": False,
            "skills": "[]",
            "skills_count": 0,
            "is_technology_job": False,
            "technology_category": "Non-Technology",
            "classification_confidence": 0.90,
            "needs_manual_review": False,
            "posted_date": "2026-11-19",
            "source": "headcount_labs",
        },
    ]
    df = pd.DataFrame(records)
    # Enrich like load_clean_data
    df["has_salary"] = df["salary_min_pkr"].notna()
    df["has_experience"] = df["experience_min_years"].notna()
    df["parsed_skills"] = [["Python", "AWS", "Docker"], ["SQL", "Excel", "Power BI"], []]
    df["workplace_display"] = df["workplace_type"].str.capitalize()
    df["experience_bracket"] = ["Senior (5+ yrs)", "Entry / Junior (0-1 yrs)", "Mid-Level (2-4 yrs)"]
    return df


class TestDashboardDataLoading:
    """Validate data loading and schema conformity."""

    def test_load_clean_data_actual_dataset(self):
        df = load_clean_data("data/processed/jobs_cleaned.csv")
        assert len(df) == 3707
        assert df["job_url"].dropna().nunique() == len(df)
        for col in ["job_id", "job_title", "normalized_city", "parsed_skills", "has_salary"]:
            assert col in df.columns
        assert isinstance(df.iloc[0]["parsed_skills"], list)

    def test_load_clean_data_fallback_when_missing(self, tmp_path):
        fake_path = str(tmp_path / "non_existent.csv")
        df = load_clean_data(fake_path)
        assert len(df) == 0
        for col in EXPECTED_COLUMNS:
            assert col in df.columns


class TestGlobalFilters:
    """Validate multi-criteria filtering logic."""

    def test_filter_tech_only(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", tech_only=True)
        assert len(res) == 2
        assert all(res["is_technology_job"] == True)

    def test_default_scope_is_confirmed_pakistan_tech(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, date_scope="All Dates (2019–2026 Historical)")
        assert len(res) == 2
        assert all(res["is_pakistan_location"] == True)
        assert all(res["is_technology_job"] == True)

    def test_date_scope_filters_stale_records(self, sample_dashboard_df):
        df_with_stale = sample_dashboard_df.copy()
        df_with_stale["posted_date"] = ["2026-11-18", "2024-01-10", "2026-11-15"]
        recent = apply_global_filters(df_with_stale)
        assert len(recent) == 1
        assert recent.iloc[0]["job_id"] == "dash-001"
        all_dates = apply_global_filters(df_with_stale, date_scope="All Dates (2019–2026 Historical)")
        assert len(all_dates) == 2

    def test_filter_by_city(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", city="Lahore")
        assert len(res) == 1
        assert res.iloc[0]["normalized_city"] == "Lahore"

    def test_filter_by_workplace(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", workplace="Remote")
        assert len(res) == 1
        assert res.iloc[0]["workplace_display"] == "Remote"

    def test_filter_salary_only(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", salary_only=True)
        assert len(res) == 2
        assert all(res["has_salary"] == True)

    def test_filter_by_experience(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", experience_bracket="Senior (5+ yrs)")
        assert len(res) == 1
        assert res.iloc[0]["job_id"] == "dash-001"

    def test_filter_role_keyword(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, scope="All Deduplicated Records", role_keyword="Python")
        assert len(res) == 1
        assert "Python" in res.iloc[0]["job_title"]

    def test_filter_combined_empty_result(self, sample_dashboard_df):
        res = apply_global_filters(sample_dashboard_df, city="Lahore", workplace="On-site")
        assert len(res) == 0


class TestFormatters:
    """Validate string and numeric formatting functions."""

    def test_format_pkr(self):
        assert format_pkr(278500.0) == "PKR 278,500"
        assert format_pkr(1500000.0, compact=True) == "PKR 1.50M"
        assert format_pkr(50000.0, compact=True) == "PKR 50.0k"
        assert format_pkr(None) == "N/A"
        assert format_pkr(np.nan) == "N/A"
        assert format_pkr(0.0) == "N/A"

    def test_format_pct(self):
        assert format_pct(13.72) == "13.7%"
        assert format_pct(0.0) == "0.0%"
        assert format_pct(None) == "0.0%"
        assert format_pct(np.nan) == "0.0%"

    def test_format_number(self):
        assert format_number(4491) == "4,491"
        assert format_number(0) == "0"
        assert format_number(None) == "0"


class TestRoleSelectionAndSampleSizes:
    """Verify target role extraction and sample size reporting."""

    def test_target_roles_exist(self):
        assert len(TARGET_ROLES) == 12
        assert "Software Engineer" in TARGET_ROLES
        assert "DevOps Engineer" in TARGET_ROLES

    def test_role_filtering_on_actual_dataset(self):
        df = load_clean_data("data/processed/jobs_cleaned.csv")
        se_pattern = TARGET_ROLES["Software Engineer"]
        match_mask = (
            df["normalized_title"].fillna("").str.contains(se_pattern) |
            df["job_title"].fillna("").str.contains(se_pattern)
        )
        se_df = df[match_mask]
        assert len(se_df) > 100

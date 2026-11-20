"""HireTrends Unit Test Suite — Day 4 Analysis & Market Intelligence Pipeline.

Validates statistical analysis, skill taxonomy distributions, role segmentation,
salary benchmarking (parametric & non-parametric), geographic clustering,
workplace arrangement calculations, and skill co-occurrence logic.
"""

import json
import os
import numpy as np
import pandas as pd
import pytest

from src.analysis.cooccurrence import compute_skill_cooccurrence
from src.analysis.location_analysis import analyze_locations
from src.analysis.salary_analysis import analyze_salary_data, compute_series_stats
from src.analysis.skills_analysis import (
    get_domain_skill_demand,
    get_skills_by_category,
    get_skills_by_role,
    get_skills_by_seniority,
    get_top_skills,
    parse_job_skills,
)
from src.analysis.trend_analysis import analyze_skill_growth
from src.analysis.workplace_analysis import analyze_workplace_distribution


@pytest.fixture
def mock_job_dataframe() -> pd.DataFrame:
    """Provide a diverse, synthetic DataFrame conforming to the cleaned dataset schema."""
    records = [
        {
            "job_id": "job-001",
            "job_title": "Senior Software Engineer",
            "normalized_title": "Senior Software Engineer",
            "seniority_level": "Senior",
            "company": "Tech Corp Pakistan",
            "city": "Lahore",
            "normalized_city": "Lahore",
            "region": "Punjab",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "remote",
            "experience_text": "5+ years",
            "experience_min_years": 5.0,
            "experience_max_years": None,
            "salary_text": "USD 3,000 - 4,000",
            "salary_currency": "USD",
            "salary_interval": "monthly",
            "salary_min_original": 3000.0,
            "salary_max_original": 4000.0,
            "salary_min_pkr": 835500.0,
            "salary_max_pkr": 1114000.0,
            "salary_is_converted": True,
            "skills": json.dumps(["Python", "AWS", "Docker", "PostgreSQL"]),
            "skills_count": 4,
            "is_technology_job": True,
            "technology_category": "Software Engineering",
            "classification_confidence": 0.95,
            "classification_reason": "High confidence tech title",
            "needs_manual_review": False,
        },
        {
            "job_id": "job-002",
            "job_title": "Junior Python Developer",
            "normalized_title": "Junior Python Developer",
            "seniority_level": "Junior / Entry-Level",
            "company": "DevHouse",
            "city": "Karachi",
            "normalized_city": "Karachi",
            "region": "Sindh",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "on-site",
            "experience_text": "1-2 years",
            "experience_min_years": 1.0,
            "experience_max_years": 2.0,
            "salary_text": "PKR 100,000 - 150,000",
            "salary_currency": "PKR",
            "salary_interval": "monthly",
            "salary_min_original": 100000.0,
            "salary_max_original": 150000.0,
            "salary_min_pkr": 100000.0,
            "salary_max_pkr": 150000.0,
            "salary_is_converted": False,
            "skills": json.dumps(["Python", "SQL", "Git"]),
            "skills_count": 3,
            "is_technology_job": True,
            "technology_category": "Software Engineering",
            "classification_confidence": 0.90,
            "classification_reason": "Matched python title",
            "needs_manual_review": False,
        },
        {
            "job_id": "job-003",
            "job_title": "Data Analyst",
            "normalized_title": "Data Analyst",
            "seniority_level": "Mid-Level",
            "company": "Analytics Lab",
            "city": "Islamabad",
            "normalized_city": "Islamabad",
            "region": "Islamabad",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "hybrid",
            "experience_text": "3 years",
            "experience_min_years": 3.0,
            "experience_max_years": 3.0,
            "salary_text": None,
            "salary_currency": None,
            "salary_interval": None,
            "salary_min_original": None,
            "salary_max_original": None,
            "salary_min_pkr": None,
            "salary_max_pkr": None,
            "salary_is_converted": False,
            "skills": json.dumps(["SQL", "Excel", "Power BI", "Python"]),
            "skills_count": 4,
            "is_technology_job": True,
            "technology_category": "Data Analytics",
            "classification_confidence": 0.95,
            "classification_reason": "High confidence analytics role",
            "needs_manual_review": False,
        },
        {
            "job_id": "job-004",
            "job_title": "Accountant",
            "normalized_title": "Accountant",
            "seniority_level": "Mid-Level",
            "company": "Audit Services",
            "city": "Lahore",
            "normalized_city": "Lahore",
            "region": "Punjab",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": "on-site",
            "experience_text": None,
            "experience_min_years": None,
            "experience_max_years": None,
            "salary_text": "PKR 60,000",
            "salary_currency": "PKR",
            "salary_interval": "monthly",
            "salary_min_original": 60000.0,
            "salary_max_original": 60000.0,
            "salary_min_pkr": 60000.0,
            "salary_max_pkr": 60000.0,
            "salary_is_converted": False,
            "skills": json.dumps(["Excel"]),
            "skills_count": 1,
            "is_technology_job": False,
            "technology_category": "Non-Technology",
            "classification_confidence": 0.90,
            "classification_reason": "Non-tech title",
            "needs_manual_review": False,
        },
        {
            "job_id": "job-005",
            "job_title": "Senior React Frontend Developer",
            "normalized_title": "Senior Frontend Developer",
            "seniority_level": "Senior",
            "company": "Global Remote Inc",
            "city": None,
            "normalized_city": None,
            "region": None,
            "country": "US",
            "is_pakistan_location": False,
            "workplace_type": "remote",
            "experience_text": "5+ years",
            "experience_min_years": 5.0,
            "experience_max_years": None,
            "salary_text": "USD 60,000 per year",
            "salary_currency": "USD",
            "salary_interval": "annual",
            "salary_min_original": 60000.0,
            "salary_max_original": 60000.0,
            "salary_min_pkr": 1392500.0,  # 60,000 * 278.50 / 12
            "salary_max_pkr": 1392500.0,
            "salary_is_converted": True,
            "skills": json.dumps(["React", "JavaScript", "TypeScript", "HTML", "CSS", "Git"]),
            "skills_count": 6,
            "is_technology_job": True,
            "technology_category": "Frontend Development",
            "classification_confidence": 0.95,
            "classification_reason": "Matched frontend title",
            "needs_manual_review": False,
        },
        {
            "job_id": "job-006",
            "job_title": "Project Coordinator",
            "normalized_title": "Project Coordinator",
            "seniority_level": "Mid-Level",
            "company": "Operations Ltd",
            "city": "Rawalpindi",
            "normalized_city": "Rawalpindi",
            "region": "Punjab",
            "country": "PK",
            "is_pakistan_location": True,
            "workplace_type": None,  # Unknown workplace
            "experience_text": None,
            "experience_min_years": None,
            "experience_max_years": None,
            "salary_text": None,
            "salary_currency": None,
            "salary_interval": None,
            "salary_min_original": None,
            "salary_max_original": None,
            "salary_min_pkr": None,
            "salary_max_pkr": None,
            "salary_is_converted": False,
            "skills": json.dumps([]),
            "skills_count": 0,
            "is_technology_job": False,
            "technology_category": "Uncertain / Manual Review",
            "classification_confidence": 0.45,
            "classification_reason": "Ambiguous title",
            "needs_manual_review": True,
        },
    ]
    return pd.DataFrame(records)


class TestSkillsAnalysis:
    """Verify skills extraction, role mapping, and domain clustering."""

    def test_parse_job_skills(self):
        assert parse_job_skills(None) == []
        assert parse_job_skills("not-json") == []
        assert parse_job_skills('["Python", "SQL", "Python"]') == ["Python", "SQL"]
        assert parse_job_skills(["AWS", "Docker"]) == ["AWS", "Docker"]

    def test_get_top_skills(self, mock_job_dataframe):
        top_skills = get_top_skills(mock_job_dataframe, n=5)
        assert len(top_skills) > 0
        skills_found = [s["skill"] for s in top_skills]
        assert "Python" in skills_found

        # Verify job counting (unique jobs, not repeated mentions)
        python_stat = next(s for s in top_skills if s["skill"] == "Python")
        # Python appears in jobs 001, 002, 003 -> exactly 3 jobs
        assert python_stat["job_count"] == 3
        assert python_stat["percentage_of_jobs"] == round(3 / 6 * 100, 2)

    def test_get_top_skills_tech_only(self, mock_job_dataframe):
        tech_top = get_top_skills(mock_job_dataframe, n=5, tech_only=True)
        # Total tech jobs in fixture = 4 (001, 002, 003, 005)
        python_stat = next(s for s in tech_top if s["skill"] == "Python")
        assert python_stat["percentage_of_jobs"] == 75.0  # 3 out of 4

    def test_get_domain_skill_demand(self, mock_job_dataframe):
        domains = get_domain_skill_demand(mock_job_dataframe)
        assert "Programming Languages" in domains
        assert "Cloud & DevOps" in domains

        langs = {d["skill"]: d["job_count"] for d in domains["Programming Languages"]}
        assert langs.get("Python") == 3
        assert langs.get("SQL") == 2

    def test_get_skills_by_role(self, mock_job_dataframe):
        roles = get_skills_by_role(mock_job_dataframe, top_n=5)
        assert "Software Engineer" in roles
        assert "Python Developer" in roles
        assert "Frontend Developer" in roles

        se_info = roles["Software Engineer"]
        assert se_info["sample_size"] >= 1
        top_se_skills = [s["skill"] for s in se_info["top_skills"]]
        assert "Python" in top_se_skills


class TestSalaryAnalysis:
    """Verify compensation statistics, interval handling, and outliers."""

    def test_compute_series_stats(self):
        s = pd.Series([100.0, 200.0, 300.0, 400.0, 500.0])
        stats = compute_series_stats(s)
        assert stats["sample_size"] == 5
        assert stats["min"] == 100.0
        assert stats["max"] == 500.0
        assert stats["median"] == 300.0
        assert stats["mean"] == 300.0
        assert stats["q1"] == 200.0
        assert stats["q3"] == 400.0
        assert stats["iqr"] == 200.0

    def test_compute_series_stats_empty(self):
        stats = compute_series_stats(pd.Series([], dtype=float))
        assert stats["sample_size"] == 0
        assert stats["median"] is None

    def test_analyze_salary_data(self, mock_job_dataframe):
        sal_analysis = analyze_salary_data(mock_job_dataframe)
        assert sal_analysis["total_listings"] == 6
        # 4 records have salary (001, 002, 004, 005)
        assert sal_analysis["disclosed_count"] == 4
        assert sal_analysis["disclosure_rate_pct"] == round(4 / 6 * 100, 2)

        # Currency separation
        assert "USD" in sal_analysis["currency_distribution"]
        assert "PKR" in sal_analysis["currency_distribution"]
        assert sal_analysis["currency_distribution"]["USD"] == 2
        assert sal_analysis["currency_distribution"]["PKR"] == 2

        # Experience breakdown
        exp_breakdown = sal_analysis["salary_by_experience"]
        assert "Entry / Junior (0-1 yrs)" in exp_breakdown
        assert "Senior (5+ yrs)" in exp_breakdown


class TestLocationAnalysis:
    """Verify geographic isolation, foreign handling, and role distribution."""

    def test_analyze_locations(self, mock_job_dataframe):
        loc = analyze_locations(mock_job_dataframe)
        assert loc["total_listings"] == 6
        assert loc["pakistan_listings_count"] == 5
        assert loc["foreign_listings"]["total_foreign_jobs"] == 1
        assert loc["foreign_listings"]["country_breakdown"].get("US") == 1

        # Mapped PK cities: Lahore (2), Karachi (1), Islamabad (1), Rawalpindi (1)
        assert loc["total_mapped_pk_cities"] == 5
        city_names = [c["city"] for c in loc["city_distribution"]]
        assert "Lahore" in city_names
        assert "Karachi" in city_names
        assert "Islamabad" in city_names

        # Lahore role breakdown
        lahore_info = loc["role_by_city"]["Lahore"]
        assert lahore_info["total_postings"] == 2


class TestWorkplaceAnalysis:
    """Verify known vs unknown workplace calculations."""

    def test_analyze_workplace_distribution(self, mock_job_dataframe):
        wp = analyze_workplace_distribution(mock_job_dataframe)
        assert wp["total_listings"] == 6
        # 5 have known workplace (remote, on-site, hybrid, on-site, remote), 1 is None
        assert wp["known_workplace_count"] == 5
        assert wp["unknown_workplace_count"] == 1
        assert wp["known_rate_pct"] == round(5 / 6 * 100, 2)
        assert wp["unknown_rate_pct"] == round(1 / 6 * 100, 2)

        # Denominator check: remote = 2 out of 5 known = 40.0%
        assert wp["distribution"]["remote"]["count"] == 2
        assert wp["distribution"]["remote"]["pct_of_known"] == 40.0


class TestSkillCooccurrence:
    """Verify pairwise skill co-occurrence and symmetric matrix generation."""

    def test_compute_skill_cooccurrence(self, mock_job_dataframe):
        co = compute_skill_cooccurrence(mock_job_dataframe, top_n_pairs=10, matrix_top_skills=5)
        assert co["total_jobs_evaluated"] == 6
        assert len(co["top_cooccurring_pairs"]) > 0

        # In job 001, we have (Python, AWS, Docker, PostgreSQL)
        # Pair Python + AWS must exist
        pair_names = [p["pair_name"] for p in co["top_cooccurring_pairs"]]
        assert any("Python" in p and "AWS" in p for p in pair_names)

        # Matrix should be symmetric
        matrix_dict = co["cooccurrence_matrix"]
        skills = co["matrix_skills"]
        if len(skills) >= 2:
            s1, s2 = skills[0], skills[1]
            assert matrix_dict[s1][s2] == matrix_dict[s2][s1]


class TestTrendAnalysis:
    """Verify longitudinal skill growth calculations and single-snapshot limitation flagging."""

    def test_single_snapshot_insufficient(self, mock_job_dataframe):
        # Empty/None snapshots
        result_none = analyze_skill_growth(snapshots=None, current_df=mock_job_dataframe)
        assert result_none["status"] == "UNAVAILABLE_INSUFFICIENT_SNAPSHOTS"
        assert result_none["growth_metrics_available"] is False
        assert result_none["available_snapshots_count"] == 1
        assert "extensible_fields_supported" in result_none

        # Single snapshot list
        snap_single = [{"timestamp": "2026-11-20T00:00:00Z", "dataframe": mock_job_dataframe}]
        result_single = analyze_skill_growth(snapshots=snap_single)
        assert result_single["status"] == "UNAVAILABLE_INSUFFICIENT_SNAPSHOTS"
        assert result_single["available_snapshots_count"] == 1

    def test_multi_snapshot_growth(self, mock_job_dataframe):
        # Create two distinct chronological snapshots
        df_t0 = mock_job_dataframe.iloc[:3].copy()
        df_t1 = mock_job_dataframe.copy()  # contains more jobs, so more skills

        snapshots = [
            {"timestamp": "2026-10-01T00:00:00Z", "dataframe": df_t0},
            {"timestamp": "2026-11-01T00:00:00Z", "dataframe": df_t1},
        ]

        result = analyze_skill_growth(snapshots=snapshots)
        assert result["status"] == "SUCCESS"
        assert result["growth_metrics_available"] is True
        assert result["total_skills_tracked"] > 0
        assert "fastest_growing_skills" in result
        assert "fastest_declining_skills" in result
        assert "emerging_skills" in result
        assert "declining_skills" in result


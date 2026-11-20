"""Automated Unit Tests for Day 3 Data Cleaning, Normalization, and Skill Extraction.

All tests operate hermetically offline with mocked fixtures and deterministic expectations.
Zero live network calls or credential leaks occur.
"""

import json
import pytest

from src.cleaning.city_normalizer import normalize_city_name, normalize_location
from src.cleaning.experience_parser import parse_experience
from src.cleaning.quality_checks import perform_quality_checks
from src.cleaning.salary_parser import parse_salary
from src.cleaning.skill_extractor import SkillExtractor
from src.cleaning.title_normalizer import extract_seniority, normalize_title
from src.cleaning.workplace_normalizer import normalize_workplace_type
from src.collection.classify_technology_jobs import classify_job


class TestTitleNormalization:
    """Test job title cleaning, abbreviation expansion, and seniority extraction."""

    def test_sr_software_engineer(self):
        res = normalize_title("Sr. Software Engineer")
        assert res["normalized_title"] == "Senior Software Engineer"
        assert res["seniority_level"] == "Senior"

    def test_jr_data_analyst(self):
        res = normalize_title("Jr. Data Analyst")
        assert res["normalized_title"] == "Junior Data Analyst"
        assert res["seniority_level"] == "Junior / Entry-Level"

    def test_fullstack_dev(self):
        res = normalize_title("Fullstack Dev")
        assert res["normalized_title"] == "Full Stack Developer"

    def test_lead_architect(self):
        res = normalize_title("Principal Cloud Solutions Architect")
        assert res["seniority_level"] == "Lead / Principal"

    def test_director_engineering(self):
        res = normalize_title("Director of Engineering")
        assert res["seniority_level"] == "Executive / Director"

    def test_empty_or_none_title(self):
        res = normalize_title(None)
        assert res["normalized_title"] == "Unspecified Role"
        assert res["seniority_level"] == "Unspecified"


class TestCityNormalization:
    """Test Pakistani city canonicalization, foreign exclusion, and remote handling."""

    def test_karachi_variations(self):
        city, reg, cnt, is_pk = normalize_city_name("KARACHI")
        assert city == "Karachi"
        assert reg == "Sindh"
        assert is_pk is True

        city2, _, _, _ = normalize_city_name("Khi")
        assert city2 == "Karachi"

    def test_lahore_and_islamabad(self):
        c1, r1, _, _ = normalize_city_name("Lahore")
        assert c1 == "Lahore"
        assert r1 == "Punjab"

        c2, r2, _, _ = normalize_city_name("Islamabad")
        assert c2 == "Islamabad"
        assert r2 == "Islamabad Capital Territory"

    def test_rawalpindi_and_peshawar(self):
        c1, _, _, _ = normalize_city_name("Rawalpindi")
        assert c1 == "Rawalpindi"

        c2, _, _, _ = normalize_city_name("Peshawar")
        assert c2 == "Peshawar"

    def test_remote_is_not_a_city(self):
        city, _, _, _ = normalize_city_name("Remote")
        assert city is None

    def test_foreign_locations_excluded_from_pakistan(self):
        c1, _, cnt1, is_pk1 = normalize_city_name("Cairo")
        assert c1 is None
        assert is_pk1 is False
        assert cnt1 == "EG"

        c2, _, cnt2, is_pk2 = normalize_city_name("Turkey")
        assert c2 is None
        assert is_pk2 is False
        assert cnt2 == "TR"

    def test_unknown_city_remains_none(self):
        city, _, _, _ = normalize_city_name("Atlantis City")
        assert city is None


class TestExperienceParsing:
    """Test experience requirement regex parsing."""

    def test_experience_range(self):
        res = parse_experience("We require 3-5 years of relevant experience in Python.")
        assert res["experience_min_years"] == 3.0
        assert res["experience_max_years"] == 5.0
        assert "3-5 years" in res["experience_text"]

    def test_experience_to_wording(self):
        res = parse_experience("Candidate must possess 1 to 3 years experience.")
        assert res["experience_min_years"] == 1.0
        assert res["experience_max_years"] == 3.0

    def test_single_or_plus_experience(self):
        res1 = parse_experience("Minimum 5 years of experience required.")
        assert res1["experience_min_years"] == 5.0
        assert res1["experience_max_years"] is None

        res2 = parse_experience("Looking for 2+ years of experience.")
        assert res2["experience_min_years"] == 2.0
        assert res2["experience_max_years"] is None

    def test_fresh_graduate(self):
        res = parse_experience("Open for fresh graduates and entry-level applicants.")
        assert res["experience_min_years"] == 0.0
        assert res["experience_max_years"] == 1.0

    def test_missing_experience_returns_none(self):
        res = parse_experience("Passionate programmer with enthusiasm for coding.")
        assert res["experience_min_years"] is None
        assert res["experience_max_years"] is None
        assert res["experience_text"] is None


class TestSalaryParsing:
    """Test compensation parsing, foreign currency conversion, and null retention."""

    def test_monthly_pkr_range(self):
        res = parse_salary("PKR 150,000 - 250,000 per month")
        assert res["salary_min_pkr"] == 150000.0
        assert res["salary_max_pkr"] == 250000.0
        assert res["salary_currency"] == "PKR"
        assert res["salary_interval"] == "month"
        assert res["salary_is_converted"] is False

    def test_annual_conversion_divides_by_12(self):
        # 2,400,000 PKR / year = 200,000 PKR / month
        res = parse_salary("PKR 2,400,000 per year")
        assert res["salary_min_pkr"] == 200000.0
        assert res["salary_max_pkr"] == 200000.0
        assert res["salary_interval"] == "year"

    def test_foreign_currency_conversion_usd(self):
        # USD 1,000 per month * 278.50 = 278,500 PKR
        res = parse_salary("$1,000 - $2,000 per month")
        assert res["salary_currency"] == "USD"
        assert res["salary_is_converted"] is True
        assert res["salary_min_pkr"] == 278500.0
        assert res["salary_max_pkr"] == 557000.0
        assert "State Bank of Pakistan" in res["exchange_rate_source"]

    def test_missing_salary_strictly_null(self):
        res = parse_salary(None)
        assert res["salary_min_pkr"] is None
        assert res["salary_max_pkr"] is None
        assert res["salary_text"] is None


class TestSkillExtraction:
    """Test regex skill extraction and false-positive guards."""

    @pytest.fixture
    def extractor(self):
        return SkillExtractor()

    def test_standard_skills(self, extractor):
        text = "Looking for a Python and Django developer with React and PostgreSQL experience."
        info = extractor.extract_skills(text)
        assert "Python" in info["skills"]
        assert "Django" in info["skills"]
        assert "React" in info["skills"]
        assert "PostgreSQL" in info["skills"]

    def test_r_false_positive_prevention(self, extractor):
        # The letter 'r' in common English words should NOT match the language 'R'
        text1 = "Responsible for regular reporting and user research."
        info1 = extractor.extract_skills(text1)
        assert "R" not in info1["skills"]

        # Valid technical context for R
        text2 = "Proficient in Python, SQL, and R programming for statistical modeling."
        info2 = extractor.extract_skills(text2)
        assert "R" in info2["skills"]

    def test_go_false_positive_prevention(self, extractor):
        # The verb 'go' should NOT match
        text1 = "We want candidates who go above and beyond."
        info1 = extractor.extract_skills(text1)
        assert "Go" not in info1["skills"]

        # Valid Go technical term
        text2 = "Backend microservices built with Golang and Docker."
        info2 = extractor.extract_skills(text2)
        assert "Go" in info2["skills"]

    def test_java_does_not_falsely_match_javascript(self, extractor):
        text = "Frontend specialist skilled in JavaScript, HTML, and CSS."
        info = extractor.extract_skills(text)
        assert "JavaScript" in info["skills"]
        assert "Java" not in info["skills"]

    def test_excel_does_not_match_excellent(self, extractor):
        text = "Excellent communication skills and leadership mindset."
        info = extractor.extract_skills(text)
        assert "Excel" not in info["skills"]


class TestWorkplaceNormalization:
    """Test workplace arrangement standardization."""

    def test_remote_normalization(self):
        assert normalize_workplace_type("remote") == "remote"
        assert normalize_workplace_type("wfh") == "remote"
        assert normalize_workplace_type(None, title="Senior Python Developer (Remote)") == "remote"

    def test_hybrid_normalization(self):
        assert normalize_workplace_type("hybrid") == "hybrid"
        assert normalize_workplace_type(None, title="Data Analyst - Hybrid Role") == "hybrid"

    def test_onsite_normalization(self):
        assert normalize_workplace_type("in_person") == "on-site"
        assert normalize_workplace_type("on-site") == "on-site"

    def test_unspecified_remains_none(self):
        # Do not guess remote if unknown
        assert normalize_workplace_type(None, title="Accountant", description="Normal office duties.") is None


class TestClassificationAuditAndManualReview:
    """Test classification confidence and manual review triggers."""

    def test_clear_tech_title(self):
        cls = classify_job("Full Stack Engineer")
        assert cls["is_technology_job"] is True
        assert cls["needs_manual_review"] is False
        assert cls["classification_confidence"] >= 0.85

    def test_clear_non_tech_title(self):
        cls = classify_job("Accountant / Bookkeeper")
        assert cls["is_technology_job"] is False
        assert cls["needs_manual_review"] is False
        assert cls["classification_confidence"] >= 0.85

    def test_ambiguous_title_flags_manual_review(self):
        # Ambiguous title with no tech description
        cls = classify_job("Project Officer")
        assert cls["technology_category"] == "Uncertain / Manual Review"
        assert cls["needs_manual_review"] is True
        assert cls["classification_confidence"] < 0.70

    def test_missing_title_and_description(self):
        cls = classify_job("")
        assert cls["technology_category"] == "Uncertain / Manual Review"
        assert cls["needs_manual_review"] is True


class TestQualityChecks:
    """Test data quality metrics."""

    def test_quality_checks_on_sample(self):
        records = [
            {
                "job_id": "job-1",
                "job_title": "Software Engineer",
                "company": "TechCo",
                "normalized_city": "Lahore",
                "workplace_type": "remote",
                "salary_min_pkr": 100000.0,
                "salary_max_pkr": 150000.0,
                "experience_min_years": 2.0,
                "experience_max_years": 4.0,
                "skills": ["Python", "Django"],
                "posted_date": "2026-11-20",
                "needs_manual_review": False,
            }
        ]
        qm = perform_quality_checks(records)
        assert qm["total_records"] == 1
        assert qm["unique_job_ids"] == 1
        assert qm["invalid_salary_ranges"] == 0
        assert qm["records_with_skills"] == 1
        assert qm["manual_review_count"] == 0

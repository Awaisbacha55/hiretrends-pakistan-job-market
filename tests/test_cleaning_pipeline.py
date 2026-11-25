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

    def test_diacritic_and_neighborhood_variants(self):
        c1, r1, _, pk1 = normalize_city_name("Pākpattan")
        assert (c1, r1, pk1) == ("Pakpattan", "Punjab", True)

        c2, r2, _, pk2 = normalize_city_name("Gulberg Lahore")
        assert (c2, r2, pk2) == ("Lahore", "Punjab", True)

        c3, r3, _, pk3 = normalize_city_name("Lahore G.P.O.")
        assert (c3, r3, pk3) == ("Lahore", "Punjab", True)

        c4, r4, _, pk4 = normalize_city_name("Clifton, South Karachi")
        assert (c4, r4, pk4) == ("Karachi", "Sindh", True)

    def test_provinces_and_country_not_treated_as_cities(self):
        c1, r1, cnt1, pk1 = normalize_city_name("Sindh", "PK")
        assert (c1, r1, cnt1, pk1) == (None, "Sindh", "PK", True)

        c2, r2, cnt2, pk2 = normalize_city_name("Punjab", "PK")
        assert (c2, r2, cnt2, pk2) == (None, "Punjab", "PK", True)

        c3, r3, cnt3, pk3 = normalize_city_name("Pakistan", "PK")
        assert (c3, r3, cnt3, pk3) == (None, None, "PK", True)

    def test_multicity_delimiters_do_not_invent_single_city(self):
        for raw in (
            "Multan|Islamabad|Karachi|Lahore|Faisalabad",
            "Karachi/Lahore",
            "Islamabad & Lahore",
        ):
            city, _, cnt, pk = normalize_city_name(raw, "PK")
            assert city is None
            assert cnt == "PK"
            assert pk is True

    def test_secondary_pakistan_cities_and_noise(self):
        for raw, expected in (
            ("Hub", "Hub"),
            ("Nawabshah", "Nawabshah"),
            ("Jhelum", "Jhelum"),
            ("Akora Khattak", "Akora Khattak"),
            ("Dina", "Dina"),
            ("Kharian", "Kharian"),
            ("Vehari", "Vehari"),
            ("Chishtian", "Chishtian"),
        ):
            city, _, cnt, pk = normalize_city_name(raw, "PK")
            assert (city, cnt, pk) == (expected, "PK", True)

        for noise in ("India", "Bahrain", "Any"):
            city, _, cnt, pk = normalize_city_name(noise, "PK")
            assert (city, cnt, pk) == (None, "PK", True)


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
        # USD 1,000 per month * 276.5132 = 276,513.20 PKR (SBP Mark-to-Market / Ready Reference, 2026-11-20)
        res = parse_salary("$1,000 - $2,000 per month")
        assert res["salary_currency"] == "USD"
        assert res["salary_is_converted"] is True
        assert res["exchange_rate_used"] == 276.5132
        assert res["salary_min_pkr"] == 276513.2
        assert res["salary_max_pkr"] == 553026.4
        assert "State Bank of Pakistan" in res["exchange_rate_source"]

    def test_hourly_usd_conversion_uses_176_hours(self):
        # $10/hr * 176 hrs/mo * 276.5132 = 486,663.23 PKR
        res = parse_salary("$10 per hour")
        assert res["salary_currency"] == "USD"
        assert res["salary_interval"] == "hour"
        assert res["salary_min_original"] == 10.0
        assert res["salary_min_pkr"] == round(10.0 * 176.0 * 276.5132, 2)

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


class TestTwoTierDeduplication:
    """Test URL normalization and two-tier deterministic deduplication."""

    def test_url_normalization(self):
        from src.cleaning.clean_jobs import normalize_job_url

        # Trailing slash, uppercase host, tracking params, fragment, query order
        u1 = normalize_job_url("HTTPS://Example.COM/jobs/123/?utm_source=linkedin&b=2&a=1#top")
        u2 = normalize_job_url("https://example.com/jobs/123?a=1&b=2")
        assert u1 == "https://example.com/jobs/123?b=2&a=1" or u1 == "https://example.com/jobs/123?a=1&b=2"
        assert normalize_job_url("https://example.com/jobs/123/") == normalize_job_url("https://EXAMPLE.com/jobs/123")
        # Unusable URLs return None
        assert normalize_job_url(None) is None
        assert normalize_job_url("") is None
        assert normalize_job_url("   ") is None
        assert normalize_job_url("/relative/path") is None
        assert normalize_job_url("not-a-url") is None

    def _make_raw_job(self, job_id, title, company, city, url=None, posted_at="2026-10-28T00:00:00Z", pay=None):
        posting = {"source": "test", "source_posted_at": posted_at}
        if url is not None:
            posting["application_url"] = {"state": "known", "value": url}
        if pay is not None:
            posting["pay"] = pay
        return {
            "job_id": job_id,
            "title": {"state": "known", "value": title},
            "employer_name": {"state": "known", "value": company},
            "description": {"state": "source_omitted"},
            "locations": [{"state": "known", "value": {"city": city, "country": "PK"}}],
            "postings": [posting],
            "job_first_seen_at": posted_at,
        }

    def test_duplicate_urls_removed_and_metadata_accurate(self, tmp_path):
        from src.cleaning.clean_jobs import run_cleaning_pipeline

        raw_file = tmp_path / "jobs_raw.jsonl"
        out_csv = tmp_path / "jobs_cleaned.csv"
        meta_json = tmp_path / "cleaning_metadata.json"
        report_md = tmp_path / "report.md"

        records = [
            # Same URL (with trailing slash & tracking param), different UUIDs
            self._make_raw_job("id-1", "AI Architect", "10Pearls", "Karachi", "https://10pearls.applytojob.com/apply/0c1Cq8CC03/AI-Architect"),
            self._make_raw_job("id-2", "AI Architect", "10Pearls", "Karachi", "https://10pearls.applytojob.com/apply/0c1Cq8CC03/AI-Architect/?utm_source=x"),
            # Distinct job
            self._make_raw_job("id-3", "Backend Engineer", "Systems Ltd", "Lahore", "https://systemsltd.com/jobs/456"),
        ]
        raw_file.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

        meta = run_cleaning_pipeline(
            raw_path=str(raw_file),
            output_csv=str(out_csv),
            metadata_output=str(meta_json),
            report_output=str(report_md),
        )
        assert meta["input_records"] == 3
        assert meta["output_records"] == 2
        assert meta["removed_duplicates"] == 1
        assert meta["deduplication"]["url_duplicates_removed"] == 1
        assert meta["deduplication"]["fallback_duplicates_removed"] == 0
        assert meta["unique_job_urls_remaining"] == 2

    def test_fallback_dedup_for_urlless_records(self, tmp_path):
        from src.cleaning.clean_jobs import run_cleaning_pipeline

        raw_file = tmp_path / "jobs_raw.jsonl"
        out_csv = tmp_path / "jobs_cleaned.csv"
        meta_json = tmp_path / "cleaning_metadata.json"
        report_md = tmp_path / "report.md"

        records = [
            # Two URL-less duplicates differing only by whitespace and casing
            self._make_raw_job("id-1", "Python   Developer", "Acme Corp", "Lahore", url=None, posted_at="2026-10-28T00:00:00Z"),
            self._make_raw_job("id-2", "python developer", " acme corp ", "lahore", url="", posted_at="2026-10-28T12:00:00Z"),
            # Different posted_date -> MUST NOT be removed
            self._make_raw_job("id-3", "Python Developer", "Acme Corp", "Lahore", url=None, posted_at="2026-10-29T00:00:00Z"),
            # Different city -> MUST NOT be removed
            self._make_raw_job("id-4", "Python Developer", "Acme Corp", "Karachi", url=None, posted_at="2026-10-28T00:00:00Z"),
            # Different company -> MUST NOT be removed
            self._make_raw_job("id-5", "Python Developer", "Beta Ltd", "Lahore", url=None, posted_at="2026-10-28T00:00:00Z"),
        ]
        raw_file.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

        meta = run_cleaning_pipeline(
            raw_path=str(raw_file),
            output_csv=str(out_csv),
            metadata_output=str(meta_json),
            report_output=str(report_md),
        )
        assert meta["input_records"] == 5
        assert meta["output_records"] == 4
        assert meta["removed_duplicates"] == 1
        assert meta["deduplication"]["url_duplicates_removed"] == 0
        assert meta["deduplication"]["fallback_duplicates_removed"] == 1

    def test_deduplication_is_deterministic_and_rerunnable(self, tmp_path):
        import pandas as pd
        from src.cleaning.clean_jobs import run_cleaning_pipeline

        raw_file = tmp_path / "jobs_raw.jsonl"
        out_csv1 = tmp_path / "out1.csv"
        out_csv2 = tmp_path / "out2.csv"
        meta1 = tmp_path / "meta1.json"
        meta2 = tmp_path / "meta2.json"
        rep = tmp_path / "rep.md"

        # One record has salary (higher completeness), so it should deterministically win
        pay = {"state": "known", "value": {"currency": "PKR", "min_amount": 150000, "max_amount": 200000, "interval": "month"}}
        records = [
            self._make_raw_job("id-b", "Data Engineer", "CorpX", "Islamabad", "https://corpx.com/jobs/1", pay=None),
            self._make_raw_job("id-a", "Data Engineer", "CorpX", "Islamabad", "https://corpx.com/jobs/1", pay=pay),
        ]
        raw_file.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

        run_cleaning_pipeline(str(raw_file), str(out_csv1), str(meta1), str(rep))
        run_cleaning_pipeline(str(raw_file), str(out_csv2), str(meta2), str(rep))

        df1 = pd.read_csv(out_csv1)
        df2 = pd.read_csv(out_csv2)
        assert len(df1) == 1
        assert df1["job_id"].iloc[0] == "id-a"  # Most complete record kept
        assert df1["job_id"].tolist() == df2["job_id"].tolist()


class TestIssue2CountryAndTechScope:
    """Tests for Review Issue #2: Country classification, tech classifier rules, and dataset reconciliation."""

    def test_missing_country_is_unknown_not_pakistan(self):
        loc = normalize_location(city=None, country=None)
        assert loc["is_pakistan"] is False
        assert loc["country_classification"] == "Unknown"
        assert loc["normalized_country"] is None

    def test_remote_only_without_country_is_unknown(self):
        loc = normalize_location(city="Remote", country=None)
        assert loc["is_pakistan"] is False
        assert loc["country_classification"] == "Unknown"

    def test_explicit_pakistan_country_or_city(self):
        loc1 = normalize_location(city="Remote", country="PK")
        assert loc1["is_pakistan"] is True
        assert loc1["country_classification"] == "Pakistan"

        loc2 = normalize_location(city="Lahore", country=None)
        assert loc2["is_pakistan"] is True
        assert loc2["country_classification"] == "Pakistan"
        assert loc2["normalized_city"] == "Lahore"

    def test_explicit_foreign_and_mclean(self):
        loc1 = normalize_location(city="McLean", country="PK")
        assert loc1["is_pakistan"] is False
        assert loc1["country_classification"] == "Foreign"
        assert loc1["normalized_country"] == "US"

        loc2 = normalize_location(city=None, country="IN")
        assert loc2["is_pakistan"] is False
        assert loc2["country_classification"] == "Foreign"

    def test_multilocation_extraction_does_not_default_pk(self):
        from src.collection.map_headcount_record import extract_locations

        res = extract_locations([{"state": "known", "value": {"city": None, "country": None}}])
        assert res["primary_country"] is None

        res_multi = extract_locations([
            {"state": "known", "value": {"city": "Sunnyvale", "country": "US"}},
            {"state": "known", "value": {"city": "Lahore", "country": "PK"}},
        ])
        assert res_multi["primary_country"] == "US"
        assert len(res_multi["all_locations"]) == 2

    def test_commercial_sales_bd_presales_safeguards(self):
        for title in [
            "Sales Development Representative (SDR) - Cyber Security | Remote",
            "Business Development Representative - Cybersecurity",
            "Presales Consultant",
            "Account Executive",
            "Business Development Executive – Cloud Services",
        ]:
            cls = classify_job(title, "Requires knowledge of AWS, Python, Java, GCP, Docker.")
            assert cls["is_technology_job"] is False
            assert cls["technology_category"] == "Non-Technology"

    def test_targeted_tech_role_patterns(self):
        for title in [
            "AI Architect",
            "AI Systems Engineer (LLM & AI Agent Development)",
            "Senior WordPress Developer",
            "Magento 2 Developer",
        ]:
            cls = classify_job(title)
            assert cls["is_technology_job"] is True
            assert cls["needs_manual_review"] is False

    def test_processed_datasets_reconcile(self):
        import os
        import pandas as pd

        if not os.path.exists("data/processed/jobs_cleaned.csv"):
            pytest.skip("Processed CSVs not present")

        df_all = pd.read_csv("data/processed/jobs_cleaned.csv")
        df_pk = pd.read_csv("data/processed/jobs_pakistan.csv")
        df_pk_tech = pd.read_csv("data/processed/jobs_pakistan_tech.csv")

        with open("data/processed/cleaning_metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        assert len(df_all) == meta["output_records"] == 3707
        assert len(df_pk) == meta["scope_breakdown"]["pakistan_only_records"]
        assert len(df_pk_tech) == meta["scope_breakdown"]["pakistan_tech_records"]
        assert (df_pk["country_classification"] == "Pakistan").all()
        assert (df_pk_tech["country_classification"] == "Pakistan").all()
        assert (df_pk_tech["is_technology_job"] == True).all()

        c_brk = meta["scope_breakdown"]["country_classification"]
        assert c_brk["Pakistan"] + c_brk["Foreign"] + c_brk["Unknown"] == len(df_all)
        t_brk = meta["scope_breakdown"]["technology_classification"]
        assert t_brk["Tech"] + t_brk["Non-Technology"] + t_brk["Uncertain"] == len(df_all)


class TestIssue4DateWindowFiltering:
    """Tests for Review Issue #4: 12-month date-window filtering and boundary handling."""

    def test_recent_window_boundary_dates(self):
        from src.cleaning.clean_jobs import is_within_recent_window

        # Inclusive boundaries: 2025-11-20 and 2026-11-20
        assert is_within_recent_window("2025-11-20") is True
        assert is_within_recent_window("2026-11-20") is True
        assert is_within_recent_window("2026-06-15") is True
        # Stale & out-of-window dates
        assert is_within_recent_window("2025-11-19") is False
        assert is_within_recent_window("2019-10-02") is False
        assert is_within_recent_window("2026-11-21") is False

    def test_recent_window_invalid_and_missing_dates(self):
        from src.cleaning.clean_jobs import is_within_recent_window

        assert is_within_recent_window(None) is False
        assert is_within_recent_window("") is False
        assert is_within_recent_window("not-a-date") is False

    def test_recent_dataset_generation_and_counts(self):
        import os
        import pandas as pd

        if not os.path.exists("data/processed/jobs_pakistan_tech_recent.csv"):
            pytest.skip("Processed CSVs not present")

        df_pk_tech = pd.read_csv("data/processed/jobs_pakistan_tech.csv")
        df_recent = pd.read_csv("data/processed/jobs_pakistan_tech_recent.csv")

        assert len(df_pk_tech) == 848
        assert len(df_recent) == 685
        assert (df_recent["is_recent_12m"] == True).all()
        assert df_recent["posted_date"].min() >= "2025-11-20"
        assert df_recent["posted_date"].max() <= "2026-11-20"


class TestIssue5SkillsRankingScope:
    """Tests for Review Issue #5: Primary top skills scoped to Recent 12M Confirmed Pakistan Tech."""

    def test_metadata_top_skills_scoped_to_recent_pk_tech(self):
        import os

        if not os.path.exists("data/processed/cleaning_metadata.json"):
            pytest.skip("cleaning_metadata.json not present")

        with open("data/processed/cleaning_metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        assert "Confirmed Pakistan Tech (Recent 12M" in meta["top_skills_scope"]
        top_names = [s[0] for s in meta["top_skills"]]
        assert top_names[0] == "Python"
        assert "Excel" not in top_names[:10]
        # Pipeline-wide extraction diagnostics must be explicitly separated
        diag = meta["all_records_skills_diagnostics"]
        assert "All Deduplicated Records" in diag["scope"]
        assert diag["total_skills_extracted"] > meta["total_skills_extracted"]

    def test_skills_by_role_and_cooccurrence_on_recent_pk_tech(self):
        import os
        import pandas as pd
        from src.analysis.skills_analysis import get_skills_by_role
        from src.analysis.cooccurrence import compute_skill_cooccurrence

        if not os.path.exists("data/processed/jobs_pakistan_tech_recent.csv"):
            pytest.skip("jobs_pakistan_tech_recent.csv not present")

        df_recent = pd.read_csv("data/processed/jobs_pakistan_tech_recent.csv")
        roles = get_skills_by_role(df_recent, top_n=5)
        assert roles["Software Engineer"]["sample_size"] == 70
        assert all(v["has_sufficient_records"] for v in roles.values())

        co = compute_skill_cooccurrence(df_recent, top_n_pairs=5)
        assert co["total_jobs_evaluated"] == 685
        assert co["top_cooccurring_pairs"][0]["pair_name"] == "AWS + Microsoft Azure"

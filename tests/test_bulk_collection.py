"""Automated Unit Tests for Day 2 Bulk Collection, Mapping, and Classification.

All tests operate hermetically offline with mocked network sessions and fixtures.
Zero live network calls or credential leaks occur.
"""

import json
import os
from unittest.mock import MagicMock, patch
import pytest
import requests

from src.collection.bulk_collect_headcount import HeadcountBulkCollector
from src.collection.classify_technology_jobs import classify_job
from src.collection.map_headcount_record import (
    extract_locations,
    extract_salary_info,
    extract_state_value,
    map_headcount_job,
)


class TestRecordMapping:
    """Test mapping Headcount Labs state-wrapped records to internal schema."""

    def test_extract_state_value(self):
        assert extract_state_value({"state": "known", "value": "Python Developer"}) == "Python Developer"
        assert extract_state_value({"state": "source_omitted"}) is None
        assert extract_state_value({"state": "extraction_failed"}) is None
        assert extract_state_value(None) is None
        assert extract_state_value("raw_string") == "raw_string"

    def test_extract_locations(self):
        locs = [
            {"state": "known", "value": {"city": "Lahore", "region": "Punjab", "country": "PK"}},
            {"state": "known", "value": {"city": "Karachi", "region": "Sindh", "country": "PK"}},
        ]
        info = extract_locations(locs)
        assert info["primary_city"] == "Lahore"
        assert info["primary_region"] == "Punjab"
        assert info["primary_country"] == "PK"
        assert len(info["all_locations"]) == 2

    def test_extract_salary_info_when_disclosed(self):
        postings = [
            {
                "pay": {
                    "state": "known",
                    "value": {
                        "currency": "PKR",
                        "min_amount": 250000,
                        "max_amount": 350000,
                        "interval": "month",
                    },
                }
            }
        ]
        sal = extract_salary_info(postings)
        assert sal["salary_min_pkr"] == 250000.0
        assert sal["salary_max_pkr"] == 350000.0
        assert "PKR 250000 - 350000 (month)" in sal["salary_text"]

    def test_extract_salary_info_when_omitted_returns_none(self):
        # Critical schema rule: null, never 0
        postings = [{"pay": {"state": "extraction_failed"}}]
        sal = extract_salary_info(postings)
        assert sal["salary_min_pkr"] is None
        assert sal["salary_max_pkr"] is None
        assert sal["salary_text"] is None

    def test_map_headcount_job_complete(self):
        raw = {
            "job_id": "job-12345",
            "title": {"state": "known", "value": "Senior Django Engineer"},
            "employer_name": {"state": "known", "value": "Acme Tech"},
            "description": {"state": "known", "value": "Building backend APIs"},
            "work_arrangement": {"state": "known", "value": "remote"},
            "locations": [{"state": "known", "value": {"city": "Islamabad", "region": "Federal", "country": "PK"}}],
            "postings": [{"posting_url": "https://example.com/apply", "source": "greenhouse"}],
        }
        mapped = map_headcount_job(raw)
        assert mapped["job_id"] == "job-12345"
        assert mapped["job_title"] == "Senior Django Engineer"
        assert mapped["company"] == "Acme Tech"
        assert mapped["city"] == "Islamabad"
        assert mapped["workplace_type"] == "remote"
        assert mapped["source"] == "headcount_labs:greenhouse"
        assert mapped["job_url"] == "https://example.com/apply"


class TestTechnologyClassification:
    """Test heuristic classification into 16 categories."""

    def test_full_stack_classification(self):
        res = classify_job("Full Stack Software Engineer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Full Stack Development"
        assert res["classification_confidence"] >= 0.90

    def test_backend_classification(self):
        res = classify_job("Python / Django Backend Developer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Backend Development"

    def test_frontend_classification(self):
        res = classify_job("Senior React & Vue Frontend Developer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Frontend Development"

    def test_ai_ml_classification(self):
        res = classify_job("Lead Machine Learning / GenAI Engineer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Artificial Intelligence / Machine Learning"

    def test_data_analytics_classification(self):
        res = classify_job("Data Engineer - ETL & Snowflake")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Data Analytics"

    def test_devops_classification(self):
        res = classify_job("DevOps & Site Reliability Engineer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "DevOps / SRE"

    def test_cybersecurity_classification(self):
        res = classify_job("SOC Analyst / Information Security Specialist")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Cybersecurity"

    def test_qa_testing_classification(self):
        res = classify_job("Software Quality Assurance (SQA) Engineer")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "QA / Software Testing"

    def test_cloud_engineering_classification(self):
        res = classify_job("Cloud Architect (AWS / Azure)")
        assert res["is_technology_job"] is True
        assert res["technology_category"] == "Cloud Engineering"

    def test_non_technology_classification(self):
        res = classify_job("Senior Accountant / Financial Controller")
        assert res["is_technology_job"] is False
        assert res["technology_category"] == "Non-Technology"

    def test_uncertain_classification(self):
        res = classify_job("")
        assert res["is_technology_job"] is False
        assert res["technology_category"] == "Uncertain / Manual Review"


class TestBulkCollectorPagination:
    """Test pagination, cursor continuation, error handling, and checkpoints."""

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_key"})
    @patch("src.collection.bulk_collect_headcount.time.sleep", return_value=None)
    def test_multipage_pagination_and_deduplication(self, mock_sleep, tmp_path):
        collector = HeadcountBulkCollector(
            output_dir=str(tmp_path),
            limit_per_page=2,
        )

        page1 = {
            "data": [
                {"job_id": "id-001", "title": {"state": "known", "value": "Python Dev"}},
                {"job_id": "id-002", "title": {"state": "known", "value": "Data Analyst"}},
            ],
            "next_cursor": "cursor_page_2",
            "snapshot_watermark": "2026-11-20T12:00:00Z",
        }
        page2 = {
            "data": [
                {"job_id": "id-002", "title": {"state": "known", "value": "Duplicate ID"}},
                {"job_id": "id-003", "title": {"state": "known", "value": "DevOps Engineer"}},
            ],
            "next_cursor": None,  # Signals end
            "snapshot_watermark": "2026-11-20T12:00:00Z",
        }

        with patch.object(collector.session, "get") as mock_get:
            resp1 = MagicMock()
            resp1.status_code = 200
            resp1.json.return_value = page1

            resp2 = MagicMock()
            resp2.status_code = 200
            resp2.json.return_value = page2

            mock_get.side_effect = [resp1, resp2]

            result = collector.run(resume=False)

            assert result["success"] is True
            assert result["total_pages"] == 2
            assert result["total_records_received"] == 4
            assert result["unique_job_ids"] == 3
            assert result["duplicate_job_ids"] == 1
            assert result["snapshot_watermark"] == "2026-11-20T12:00:00Z"

            # Verify files written
            assert os.path.exists(collector.jobs_file)
            assert os.path.exists(collector.metadata_file)
            assert os.path.exists(collector.checkpoint_file)

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_key"})
    @patch("src.collection.bulk_collect_headcount.time.sleep", return_value=None)
    def test_repeated_cursor_detection(self, mock_sleep, tmp_path):
        collector = HeadcountBulkCollector(output_dir=str(tmp_path))

        loop_page = {
            "data": [{"job_id": "id-100"}],
            "next_cursor": "same_cursor",
            "snapshot_watermark": "2026-11-20T12:00:00Z",
        }

        with patch.object(collector.session, "get") as mock_get:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = loop_page
            mock_get.return_value = resp

            result = collector.run(resume=False, max_pages=5)
            assert result["success"] is False
            assert any("Repeated cursor detected" in err for err in result["errors"])

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_key"})
    @patch("src.collection.bulk_collect_headcount.time.sleep", return_value=None)
    def test_empty_final_page_completes_cleanly(self, mock_sleep, tmp_path):
        collector = HeadcountBulkCollector(output_dir=str(tmp_path))

        empty_page = {
            "data": [],
            "next_cursor": None,
            "snapshot_watermark": "2026-11-20T12:00:00Z",
        }

        with patch.object(collector.session, "get") as mock_get:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = empty_page
            mock_get.return_value = resp

            result = collector.run(resume=False)
            assert result["success"] is True
            assert result["total_records_received"] == 0

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_key"})
    @patch("src.collection.bulk_collect_headcount.time.sleep", return_value=None)
    def test_checkpoint_resume(self, mock_sleep, tmp_path):
        collector = HeadcountBulkCollector(output_dir=str(tmp_path))

        # Write existing checkpoint
        checkpoint = {
            "page_number": 1,
            "next_cursor": "resume_cursor_002",
            "snapshot_watermark": "2026-11-20T12:00:00Z",
            "records_fetched": 2,
            "unique_records": 2,
            "duplicate_records": 0,
            "country": "PK",
            "currentness": "current",
            "limit": 250,
            "last_updated_at": "2026-11-20T12:00:00Z",
        }
        with open(collector.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f)

        final_page = {
            "data": [{"job_id": "id-003"}],
            "next_cursor": None,
            "snapshot_watermark": "2026-11-20T12:00:00Z",
        }

        with patch.object(collector.session, "get") as mock_get:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = final_page
            mock_get.return_value = resp

            result = collector.run(resume=True)
            assert result["success"] is True
            # Verified that request was made using the resume cursor
            call_params = mock_get.call_args[1]["params"]
            assert call_params["cursor"] == "resume_cursor_002"

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_key"})
    @patch("src.collection.bulk_collect_headcount.time.sleep", return_value=None)
    def test_http_401_stops_immediately_without_retry(self, mock_sleep, tmp_path):
        collector = HeadcountBulkCollector(output_dir=str(tmp_path))

        with patch.object(collector.session, "get") as mock_get:
            resp = MagicMock()
            resp.status_code = 401
            resp.text = "Unauthorized"
            mock_get.return_value = resp

            result = collector.run(resume=False)
            assert result["success"] is False
            assert mock_get.call_count == 1  # No repeated retry on 401

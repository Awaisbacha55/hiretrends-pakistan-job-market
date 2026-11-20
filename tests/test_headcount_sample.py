"""Automated Unit Tests for Headcount Labs Sample Data Ingestion and Parsing.

All tests operate hermetically offline with mocked network calls and fixtures.
Zero live network calls or credential leaks occur.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
import requests

from src.collection.fetch_headcount_sample import (
    analyze_sample_records,
    fetch_headcount_sample,
)

MOCK_API_SAMPLE_PAYLOAD = [
    {
        "job_id": "test-uuid-001",
        "company_id": "comp-uuid-001",
        "employer_name": {"state": "known", "value": "Tech Pakistan Pvt Ltd"},
        "title": {"state": "known", "value": "Lead Python Engineer"},
        "description": {"state": "known", "value": "Seeking a Senior Python and Django specialist."},
        "work_arrangement": {"state": "known", "value": "remote"},
        "locations": [
            {"state": "known", "value": {"city": "Islamabad", "region": "Federal", "country": "PK"}}
        ],
        "postings": [
            {
                "posting_id": "post-001",
                "source": "lever",
                "posting_url": "https://example.com/jobs/001",
                "pay": {"state": "known", "min": 300000, "max": 450000, "currency": "PKR"},
                "attribution": {"required": False},
            }
        ],
    },
    {
        "job_id": "test-uuid-002",
        "company_id": "comp-uuid-002",
        "employer_name": {"state": "known", "value": "Global Logistics Corp"},
        "title": {"state": "known", "value": "Data Analyst"},
        "description": {"state": "known", "value": "SQL, Excel, and Power BI role."},
        "work_arrangement": {"state": "source_omitted"},
        "locations": [
            {"state": "known", "value": {"city": "Lahore", "region": "Punjab", "country": "PK"}}
        ],
        "postings": [
            {
                "posting_id": "post-002",
                "source": "workday",
                "posting_url": "https://example.com/jobs/002",
                "pay": {"state": "extraction_failed"},
            }
        ],
    },
]


class TestHeadcountSampleIngestion:
    """Test sample retrieval, error handling, and response processing."""

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_api_response_parsing(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_API_SAMPLE_PAYLOAD
        mock_get.return_value = mock_resp

        out_file = tmp_path / "sample_out.json"
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is True
        assert result["status_code"] == 200
        assert len(result["records"]) == 2
        assert result["records"][0]["job_id"] == "test-uuid-001"
        assert out_file.exists()

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_empty_response(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        out_file = tmp_path / "empty_out.json"
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is True
        assert result["records"] == []

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_missing_fields_in_records(self, mock_get, tmp_path):
        sparse_record = [{"job_id": "sparse-001"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sparse_record
        mock_get.return_value = mock_resp

        out_file = tmp_path / "sparse_out.json"
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is True
        assert len(result["records"]) == 1
        assert result["records"][0].get("title") is None

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_invalid_api_response_body(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = "unexpected string payload"
        mock_get.return_value = mock_resp

        out_file = tmp_path / "invalid_out.json"
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is True
        assert result["records"] == []

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_api_authentication_errors(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = '{"error": "Unauthorized"}'
        mock_get.return_value = mock_resp

        out_file = tmp_path / "auth_error.json"
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is False
        assert result["status_code"] == 401
        assert "HTTP 401" in result["error"]

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_test_token"})
    @patch("src.collection.fetch_headcount_sample.requests.get")
    def test_sample_size_limit_enforced(self, mock_get, tmp_path):
        # 15 records in mock
        large_mock = [{"job_id": f"job-{i}"} for i in range(15)]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = large_mock
        mock_get.return_value = mock_resp

        out_file = tmp_path / "limit_out.json"
        # Request limit=10
        result = fetch_headcount_sample(limit=10, output_path=str(out_file))

        assert result["success"] is True
        assert len(result["records"]) == 10


class TestSampleAnalyzer:
    """Test sample data analysis function."""

    def test_analyze_sample_records(self):
        analysis = analyze_sample_records(MOCK_API_SAMPLE_PAYLOAD)
        assert analysis["total_records"] == 2
        assert analysis["description_available_count"] == 2
        assert analysis["locations_available_count"] == 2
        assert analysis["work_arrangement_available_count"] == 1
        assert "job_id" in analysis["all_fields"]

    def test_analyze_empty_sample(self):
        analysis = analyze_sample_records([])
        assert analysis["total_records"] == 0

"""Automated Unit Tests for Headcount Labs API Connection Module.

All tests operate offline with mocked requests and environment variables.
Zero live network calls or credential leaks occur.
"""

from unittest.mock import MagicMock, patch
import pytest
import requests

from src.collection.headcount_client import (
    check_api_key_configuration,
    verify_headcount_connection,
)


class TestHeadcountAPIConfiguration:
    """Test API key environment loading and validation."""

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "valid_mock_token_12345"}, clear=True)
    def test_key_detected(self):
        result = check_api_key_configuration(load_env=False)
        assert result["configured"] is True
        assert result["key_length"] == len("valid_mock_token_12345")
        # Ensure key value is not exposed in message
        assert "valid_mock_token_12345" not in result["message"]

    @patch.dict("os.environ", {}, clear=True)
    def test_key_missing(self):
        result = check_api_key_configuration(load_env=False)
        assert result["configured"] is False
        assert result["key_length"] == 0
        assert "not set or empty" in result["message"]

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "   "}, clear=True)
    def test_key_whitespace_only(self):
        result = check_api_key_configuration(load_env=False)
        assert result["configured"] is False
        assert result["key_length"] == 0
        assert "empty or contains only whitespace" in result["message"]


class TestHeadcountConnectionHandling:
    """Test connection handling under varied network and HTTP response conditions."""

    @patch.dict("os.environ", {}, clear=True)
    def test_connection_fails_without_key(self):
        result = verify_headcount_connection(load_env=False)
        assert result["success"] is False
        assert result["error_type"] == "MISSING_CREDENTIALS"

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_successful_200_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"count": 4493, "snapshot_watermark": "2026-11-20T12:50:56.000Z"}
        mock_get.return_value = mock_resp

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"]["count"] == 4493
        assert result["error_type"] is None

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_unauthorized_401_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is False
        assert result["status_code"] == 401
        assert result["error_type"] == "AUTHENTICATION_ERROR"

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_forbidden_403_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_get.return_value = mock_resp

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is False
        assert result["status_code"] == 403
        assert result["error_type"] == "FORBIDDEN"

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_rate_limited_429_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_get.return_value = mock_resp

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is False
        assert result["status_code"] == 429
        assert result["error_type"] == "RATE_LIMIT_EXCEEDED"

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_timeout_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is False
        assert result["error_type"] == "TIMEOUT"
        assert "timed out" in result["message"]

    @patch.dict("os.environ", {"HEADCOUNTLABS_API_KEY": "dummy_key"})
    @patch("src.collection.headcount_client.requests.get")
    def test_connection_error_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS failure")

        result = verify_headcount_connection(country="PK", load_env=False)
        assert result["success"] is False
        assert result["error_type"] == "CONNECTION_ERROR"

"""Automated Unit Tests for Robots.txt and Source Permission Checker.

All tests operate offline without connecting to live websites.
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.collection.check_sources import (
    build_robots_url,
    check_robots_txt,
    fetch_robots_txt,
    is_valid_url,
    verify_source_permission,
)


class TestURLValidation:
    """Test URL parsing and validation logic."""

    def test_valid_http_and_https_urls(self):
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/jobs") is True
        assert is_valid_url("https://jobs.example.com.pk/postings/123") is True

    def test_invalid_urls(self):
        assert is_valid_url("") is False
        assert is_valid_url("not_a_url") is False
        assert is_valid_url("ftp://example.com") is False
        assert is_valid_url("https://") is False
        assert is_valid_url(None) is False  # type: ignore

    def test_build_robots_url(self):
        assert (
            build_robots_url("https://example.com/jobs/search?q=python")
            == "https://example.com/robots.txt"
        )
        assert (
            build_robots_url("http://sub.domain.pk/page.html")
            == "http://sub.domain.pk/robots.txt"
        )


class TestRobotsParser:
    """Test parsing and evaluation of robots.txt directives offline."""

    MOCK_ROBOTS_TXT = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /api/
Crawl-delay: 5

User-agent: BadBot
Disallow: /
"""

    @patch("src.collection.check_sources.fetch_robots_txt")
    def test_permitted_url(self, mock_fetch):
        mock_fetch.return_value = (self.MOCK_ROBOTS_TXT, 200, None)

        result = check_robots_txt(
            base_url="https://example.com",
            target_url="https://example.com/jobs/software-engineer",
            user_agent="HireTrendsBot/1.0",
        )

        assert result["verified"] is True
        assert result["can_fetch"] is True
        assert result["crawl_delay"] == 5
        assert result["error"] is None

    @patch("src.collection.check_sources.fetch_robots_txt")
    def test_disallowed_url(self, mock_fetch):
        mock_fetch.return_value = (self.MOCK_ROBOTS_TXT, 200, None)

        result = check_robots_txt(
            base_url="https://example.com",
            target_url="https://example.com/admin/dashboard",
            user_agent="HireTrendsBot/1.0",
        )

        assert result["verified"] is True
        assert result["can_fetch"] is False

    @patch("src.collection.check_sources.fetch_robots_txt")
    def test_missing_robots_txt_returns_404(self, mock_fetch):
        # HTTP 404 indicates robots.txt doesn't exist, which web standards treat as permitted
        mock_fetch.return_value = ("", 404, None)

        result = check_robots_txt(
            base_url="https://example.com",
            target_url="https://example.com/jobs",
        )

        assert result["verified"] is True
        assert result["can_fetch"] is True
        assert result["status_code"] == 404

    @patch("src.collection.check_sources.fetch_robots_txt")
    def test_fail_closed_on_http_forbidden_403(self, mock_fetch):
        # 403 Forbidden must fail closed
        mock_fetch.return_value = (None, 403, "HTTP 403 while fetching robots.txt")

        result = check_robots_txt(
            base_url="https://example.com",
            target_url="https://example.com/jobs",
        )

        assert result["verified"] is False
        assert result["can_fetch"] is False
        assert "403" in result["error"]

    @patch("src.collection.check_sources.fetch_robots_txt")
    def test_fail_closed_on_network_timeout(self, mock_fetch):
        mock_fetch.return_value = (None, None, "Timeout after 10 seconds")

        result = check_robots_txt(
            base_url="https://example.com",
            target_url="https://example.com/jobs",
        )

        assert result["verified"] is False
        assert result["can_fetch"] is False
        assert "Timeout" in result["error"]


class TestPermissionVerification:
    """Test source permission validation against sources.json."""

    def test_approved_source(self, tmp_path):
        cfg_file = tmp_path / "sources.json"
        cfg_file.write_text(
            json.dumps({
                "sources": [{
                    "id": "test_portal",
                    "name": "Test Portal",
                    "permission_status": "APPROVED",
                }]
            }),
            encoding="utf-8",
        )

        is_approved, meta, msg = verify_source_permission("test_portal", str(cfg_file))
        assert is_approved is True
        assert meta["id"] == "test_portal"
        assert "APPROVED" in msg

    def test_prohibited_source(self, tmp_path):
        cfg_file = tmp_path / "sources.json"
        cfg_file.write_text(
            json.dumps({
                "sources": [{
                    "id": "blocked_portal",
                    "name": "Blocked Portal",
                    "permission_status": "PROHIBITED",
                }]
            }),
            encoding="utf-8",
        )

        is_approved, meta, msg = verify_source_permission("blocked_portal", str(cfg_file))
        assert is_approved is False
        assert meta["id"] == "blocked_portal"
        assert "NOT approved" in msg

    def test_source_not_found(self, tmp_path):
        cfg_file = tmp_path / "sources.json"
        cfg_file.write_text(json.dumps({"sources": []}), encoding="utf-8")

        is_approved, meta, msg = verify_source_permission("non_existent", str(cfg_file))
        assert is_approved is False
        assert meta is None
        assert "not found" in msg

    def test_missing_config_file(self):
        is_approved, meta, msg = verify_source_permission("any", "non_existent_file.json")
        assert is_approved is False
        assert meta is None
        assert "not found" in msg

    def test_corrupted_config_json(self, tmp_path):
        cfg_file = tmp_path / "bad.json"
        cfg_file.write_text("{invalid json", encoding="utf-8")

        is_approved, meta, msg = verify_source_permission("any", str(cfg_file))
        assert is_approved is False
        assert meta is None
        assert "Failed to load" in msg

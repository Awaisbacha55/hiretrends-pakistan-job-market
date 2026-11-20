"""Automated Unit Tests for Ethical Scraper Foundation.

All tests utilize offline HTML fixtures and mocked network components.
Zero live scraping calls are made.
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.collection.scraper import (
    EthicalScraper,
    generate_job_id,
    parse_job_cards,
)

SAMPLE_HTML_FIXTURE = """
<!DOCTYPE html>
<html>
<head><title>Job Listings</title></head>
<body>
    <div class="job-container">
        <article class="job-card">
            <h2 class="job-title"><a href="/jobs/101" class="job-link">Senior Python Developer</a></h2>
            <span class="company-name">Tech Innovators Pvt Ltd</span>
            <span class="job-location">Lahore, Pakistan</span>
            <div class="salary-tag">PKR 250,000 - 350,000 per month</div>
            <p class="job-summary">Seeking an experienced Python and Django developer.</p>
        </article>
        <article class="job-card">
            <h2 class="job-title"><a href="/jobs/102" class="job-link">Data Engineer (PySpark)</a></h2>
            <span class="company-name">DataSphere Solutions</span>
            <span class="job-location">Karachi, Pakistan</span>
            <div class="salary-tag">PKR 200,000 - 300,000 per month</div>
            <p class="job-summary">Build scalable data pipelines with Spark and Kafka.</p>
        </article>
    </div>
</body>
</html>
"""

STANDARD_SELECTORS = {
    "job_card": "article.job-card",
    "title": "h2.job-title",
    "company": "span.company-name",
    "city": "span.job-location",
    "salary": "div.salary-tag",
    "description": "p.job-summary",
    "job_url": "a.job-link",
}


class TestHTMLCardParsing:
    """Test extracting structured data from HTML fixtures."""

    def test_parse_valid_cards(self):
        records = parse_job_cards(
            SAMPLE_HTML_FIXTURE,
            STANDARD_SELECTORS,
            source_name="test_portal",
        )

        assert len(records) == 2

        first = records[0]
        assert first["job_title"] == "Senior Python Developer"
        assert first["company"] == "Tech Innovators Pvt Ltd"
        assert first["city"] == "Lahore, Pakistan"
        assert first["salary_text"] == "PKR 250,000 - 350,000 per month"
        assert first["job_url"] == "/jobs/101"
        assert "Python" in first["description"]
        assert first["source"] == "test_portal"
        # Schema rule: numeric values must be None (not 0)
        assert first["salary_min_pkr"] is None
        assert first["salary_max_pkr"] is None
        assert first["experience_min_years"] is None

        second = records[1]
        assert second["job_title"] == "Data Engineer (PySpark)"
        assert second["company"] == "DataSphere Solutions"
        assert second["city"] == "Karachi, Pakistan"

    def test_empty_html_content(self):
        assert parse_job_cards("", STANDARD_SELECTORS) == []
        assert parse_job_cards(None, STANDARD_SELECTORS) == []  # type: ignore

    def test_zero_cards_matching_selector(self):
        bad_selectors = {"job_card": "div.non-existent-card", "title": "h1"}
        records = parse_job_cards(SAMPLE_HTML_FIXTURE, bad_selectors)
        assert records == []

    def test_missing_optional_selectors(self):
        minimal_selectors = {
            "job_card": "article.job-card",
            "title": "h2.job-title",
        }
        records = parse_job_cards(SAMPLE_HTML_FIXTURE, minimal_selectors)
        assert len(records) == 2
        assert records[0]["job_title"] == "Senior Python Developer"
        assert records[0]["company"] is None
        assert records[0]["city"] is None
        assert records[0]["salary_text"] is None

    def test_missing_job_card_selector_fails_gracefully(self):
        records = parse_job_cards(SAMPLE_HTML_FIXTURE, {"title": "h2"})
        assert records == []

    def test_deterministic_job_id_generation(self):
        id1 = generate_job_id("test", "Engineer", "TechCo", "/job/1")
        id2 = generate_job_id("test", "Engineer", "TechCo", "/job/1")
        id3 = generate_job_id("test", "Manager", "TechCo", "/job/2")

        assert id1 == id2
        assert id1 != id3
        assert id1.startswith("test_")


class TestEthicalScraperCompliance:
    """Test runtime compliance enforcement and fail-closed protections."""

    def test_scraper_halts_on_unapproved_source(self, tmp_path):
        cfg = tmp_path / "sources.json"
        cfg.write_text(
            json.dumps({
                "sources": [{
                    "id": "unapproved_site",
                    "permission_status": "REQUIRES_PERMISSION",
                }]
            }),
            encoding="utf-8",
        )

        scraper = EthicalScraper(
            source_identifier="unapproved_site",
            sources_config_path=str(cfg),
        )

        with pytest.raises(PermissionError) as exc_info:
            scraper.verify_compliance("https://example.com/jobs")

        assert "Collection disallowed" in str(exc_info.value)

    def test_scraper_halts_on_prohibited_source(self, tmp_path):
        cfg = tmp_path / "sources.json"
        cfg.write_text(
            json.dumps({
                "sources": [{
                    "id": "blocked_site",
                    "permission_status": "PROHIBITED",
                }]
            }),
            encoding="utf-8",
        )

        scraper = EthicalScraper(
            source_identifier="blocked_site",
            sources_config_path=str(cfg),
        )

        with pytest.raises(PermissionError):
            scraper.verify_compliance("https://example.com/jobs")

    @patch("src.collection.scraper.check_robots_txt")
    def test_scraper_halts_when_robots_disallows(self, mock_robots, tmp_path):
        cfg = tmp_path / "sources.json"
        cfg.write_text(
            json.dumps({
                "sources": [{
                    "id": "approved_site",
                    "permission_status": "APPROVED",
                }]
            }),
            encoding="utf-8",
        )

        mock_robots.return_value = {
            "verified": True,
            "can_fetch": False,
            "crawl_delay": None,
            "error": None,
        }

        scraper = EthicalScraper(
            source_identifier="approved_site",
            sources_config_path=str(cfg),
        )

        with pytest.raises(PermissionError) as exc_info:
            scraper.verify_compliance("https://example.com/disallowed-job")

        assert "DISALLOWS" in str(exc_info.value)

    @patch("src.collection.scraper.check_robots_txt")
    def test_scraper_succeeds_only_when_both_permitted(self, mock_robots, tmp_path):
        cfg = tmp_path / "sources.json"
        cfg.write_text(
            json.dumps({
                "sources": [{
                    "id": "approved_site",
                    "permission_status": "APPROVED",
                }]
            }),
            encoding="utf-8",
        )

        mock_robots.return_value = {
            "verified": True,
            "can_fetch": True,
            "crawl_delay": 2.0,
            "error": None,
        }

        scraper = EthicalScraper(
            source_identifier="approved_site",
            sources_config_path=str(cfg),
        )

        result = scraper.verify_compliance("https://example.com/allowed-job")
        assert result["source_meta"]["permission_status"] == "APPROVED"
        assert result["robots_result"]["can_fetch"] is True

    def test_invalid_target_url_raises_value_error(self, tmp_path):
        scraper = EthicalScraper(source_identifier="any")
        with pytest.raises(ValueError):
            scraper.verify_compliance("")

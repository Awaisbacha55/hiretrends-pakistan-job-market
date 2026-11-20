"""HireTrends Ethical Web Scraper Foundation.

Enforces strict compliance with:
1. config/sources.json permission status (must be explicitly 'APPROVED')
2. robots.txt policies via check_sources.py
3. Polite crawling delays and non-disruptive request headers
"""

from datetime import datetime, timezone
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .check_sources import DEFAULT_USER_AGENT, check_robots_txt, verify_source_permission

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.Scraper")


def generate_job_id(source: str, title: str, company: Optional[str], url: Optional[str]) -> str:
    """Generate a deterministic, unique identifier for a job posting."""
    seed = f"{source}::{title or ''}::{company or ''}::{url or ''}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"{source}_{digest}"


def parse_job_cards(
    html_content: str,
    selectors: Dict[str, str],
    source_name: str = "unknown",
) -> List[Dict[str, Any]]:
    """Parse raw HTML content into structured job listing records.

    Args:
        html_content: Raw HTML text of the job listing page.
        selectors: Mapping of field names to CSS selector strings.
            Expected keys include:
                - job_card: container element for each job
                - title: job title element
                - company: company name element
                - city: location element
                - salary: raw compensation text element (optional)
                - description: description or summary snippet (optional)
                - job_url: link element or attribute (optional)
        source_name: Name of the originating source.

    Returns:
        List of structured record dictionaries matching dataset schema.
    """
    if not html_content or not selectors:
        return []

    card_selector = selectors.get("job_card")
    if not card_selector:
        logger.warning("No 'job_card' selector provided. Cannot parse listings.")
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    cards = soup.select(card_selector)
    if not cards:
        logger.info("Zero cards matched selector: '%s'", card_selector)
        return []

    title_sel = selectors.get("title")
    company_sel = selectors.get("company")
    city_sel = selectors.get("city")
    salary_sel = selectors.get("salary")
    desc_sel = selectors.get("description")
    url_sel = selectors.get("job_url")

    records: List[Dict[str, Any]] = []
    now_utc = datetime.now(timezone.utc).isoformat()

    for card in cards:
        title = None
        if title_sel:
            el = card.select_one(title_sel)
            if el:
                title = el.get_text(strip=True)

        # Skip empty card if no title exists
        if not title:
            continue

        company = None
        if company_sel:
            el = card.select_one(company_sel)
            if el:
                company = el.get_text(strip=True)

        city = None
        if city_sel:
            el = card.select_one(city_sel)
            if el:
                city = el.get_text(strip=True)

        salary_text = None
        if salary_sel:
            el = card.select_one(salary_sel)
            if el:
                salary_text = el.get_text(strip=True)

        description = None
        if desc_sel:
            el = card.select_one(desc_sel)
            if el:
                description = el.get_text(strip=True)

        job_url = None
        if url_sel:
            el = card.select_one(url_sel)
            if el:
                job_url = el.get("href")

        job_id = generate_job_id(source_name, title, company, job_url)

        record = {
            "job_id": job_id,
            "job_title": title,
            "normalized_title": None,  # Populated during Day 2/3 cleaning
            "company": company,
            "city": city,
            "normalized_city": None,  # Populated during Day 2/3 cleaning
            "salary_text": salary_text,
            "salary_min_pkr": None,  # Explicitly None (null), not 0
            "salary_max_pkr": None,  # Explicitly None (null), not 0
            "experience_text": None,
            "experience_min_years": None,
            "experience_max_years": None,
            "employment_type": None,
            "workplace_type": None,
            "description": description,
            "skills": [],
            "posted_date": None,
            "source": source_name,
            "job_url": job_url,
            "collected_at": now_utc,
        }
        records.append(record)

    logger.info("Extracted %d valid job cards from HTML.", len(records))
    return records


class EthicalScraper:
    """Production-grade ethical scraper foundation.

    Enforces mandatory source approval and robots.txt permission.
    """

    def __init__(
        self,
        source_identifier: str,
        sources_config_path: str = "config/sources.json",
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = 15,
        delay_seconds: float = 3.0,
    ):
        self.source_identifier = source_identifier
        self.sources_config_path = sources_config_path
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self._last_request_time: float = 0.0

    def verify_compliance(self, target_url: str) -> Dict[str, Any]:
        """Validate both platform permission and robots.txt policy.

        Raises:
            PermissionError: If the source is not explicitly APPROVED in configuration,
                             or if robots.txt disallows fetching the target URL.
            ValueError: If the target URL is invalid.
        """
        if not target_url or not isinstance(target_url, str):
            raise ValueError(f"Invalid target URL: {target_url}")

        # Check 1: Must be explicitly APPROVED in sources.json
        is_approved, source_meta, reason = verify_source_permission(
            self.source_identifier,
            self.sources_config_path,
        )
        if not is_approved:
            logger.error("Compliance Check FAILED: %s", reason)
            raise PermissionError(
                f"Collection disallowed for source '{self.source_identifier}': {reason}. "
                "HireTrends requires explicit 'APPROVED' status in config/sources.json."
            )

        # Check 2: Must be permitted by robots.txt
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_result = check_robots_txt(
            base_url=base_url,
            target_url=target_url,
            user_agent=self.user_agent,
            timeout=self.timeout,
        )

        if not robots_result["verified"]:
            raise PermissionError(
                f"Fail-closed compliance trigger: could not verify robots.txt for {target_url}. "
                f"Error: {robots_result.get('error')}"
            )

        if not robots_result["can_fetch"]:
            raise PermissionError(
                f"Robots.txt policy DISALLOWS crawling URL: {target_url} for user-agent: {self.user_agent}"
            )

        # Adjust polite delay if crawl-delay directive is present
        crawl_delay = robots_result.get("crawl_delay")
        if crawl_delay and crawl_delay > self.delay_seconds:
            logger.info("Applying robots.txt crawl-delay: %.1f seconds", crawl_delay)
            self.delay_seconds = float(crawl_delay)

        return {
            "source_meta": source_meta,
            "robots_result": robots_result,
        }

    def _apply_polite_delay(self) -> None:
        """Enforce spacing between consecutive requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            logger.debug("Polite rate limiting: sleeping for %.2f seconds", sleep_time)
            time.sleep(sleep_time)

    @retry(
        retry=retry_if_exception_type((requests.exceptions.RequestException,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def fetch_page(self, target_url: str) -> str:
        """Fetch page content with retries, politeness delay, and compliance check."""
        self.verify_compliance(target_url)
        self._apply_polite_delay()

        logger.info("Fetching target URL: %s", target_url)
        response = self.session.get(target_url, timeout=self.timeout)
        self._last_request_time = time.time()
        response.raise_for_status()
        return response.text

    def scrape_listings(
        self,
        target_url: str,
        selectors: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Fetch and extract structured job listings from a target page."""
        html = self.fetch_page(target_url)
        return parse_job_cards(html, selectors, source_name=self.source_identifier)

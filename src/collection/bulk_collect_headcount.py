"""HireTrends Headcount Labs Bulk Data Collection Pipeline.

Extracts the full feed of Pakistan job postings using official cursor-based
pagination (/v1/jobs?country=PK&currentness=current&limit=250).

Features:
- Requests.Session with retry backoff and rate-limit compliance
- Checkpoint persistence and safe resumption
- Duplicate ID detection and cursor loop prevention
- JSON Lines raw dataset generation in data/raw/headcount/
- Complete metadata tracking in collection_metadata.json

SECURITY NOTICE:
HEADCOUNTLABS_API_KEY is loaded in memory and NEVER logged, printed, or exposed.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Set

from dotenv import load_dotenv
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.BulkCollector")

API_BASE_URL = "https://api.headcountlabs.com"
JOBS_ENDPOINT = f"{API_BASE_URL}/v1/jobs"
DEFAULT_PAGE_SIZE = 250
DEFAULT_TIMEOUT = 30
REQUEST_INTERVAL_SECONDS = 1.2  # Ensures compliance with 1 request/sec limit
USER_AGENT = (
    "HireTrendsResearchBot/1.0 "
    "(+https://github.com/Awaisbacha55/hiretrends-pakistan-job-market; academic research)"
)


class HeadcountBulkCollector:
    """Orchestrates paginated bulk ingestion of Pakistan job records from Headcount Labs."""

    def __init__(
        self,
        output_dir: str = "data/raw/headcount",
        country: str = "PK",
        currentness: str = "current",
        limit_per_page: int = DEFAULT_PAGE_SIZE,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.output_dir = output_dir
        self.country = country
        self.currentness = currentness
        self.limit_per_page = limit_per_page
        self.timeout = timeout

        self.jobs_file = os.path.join(self.output_dir, "jobs_raw.jsonl")
        self.metadata_file = os.path.join(self.output_dir, "collection_metadata.json")
        self.checkpoint_file = os.path.join(self.output_dir, "collection_checkpoint.json")

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        })

        load_dotenv()
        self.api_key = os.getenv("HEADCOUNTLABS_API_KEY")

        self.seen_job_ids: Set[str] = set()
        self.seen_cursors: Set[str] = set()
        self.snapshot_watermark: Optional[str] = None
        self.total_records_received = 0
        self.duplicate_records_count = 0
        self.total_pages = 0
        self.collection_started_at: Optional[str] = None
        self.errors: List[str] = []

    def _ensure_api_key(self) -> str:
        """Validate presence of API key without logging its value."""
        if not self.api_key or not self.api_key.strip():
            raise PermissionError("HEADCOUNTLABS_API_KEY is not set or empty in the environment.")
        return self.api_key.strip()

    def _fetch_page_with_retry(
        self,
        cursor: Optional[str] = None,
        max_retries: int = 5,
    ) -> Dict[str, Any]:
        """Fetch a single page with polite rate limiting and bounded exponential backoff."""
        key = self._ensure_api_key()
        headers = {"Authorization": f"Bearer {key}"}

        params: Dict[str, Any] = {
            "country": self.country,
            "currentness": self.currentness,
            "limit": self.limit_per_page,
        }
        if cursor:
            params["cursor"] = cursor

        backoff = 2.0
        for attempt in range(1, max_retries + 1):
            time.sleep(REQUEST_INTERVAL_SECONDS)
            try:
                response = self.session.get(
                    JOBS_ENDPOINT,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response.json()

                if response.status_code in (401, 403):
                    msg = f"Non-retryable HTTP {response.status_code}: {response.text[:150]}"
                    logger.error(msg)
                    raise PermissionError(msg)

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else backoff
                    logger.warning("HTTP 429 rate limit reached. Sleeping %.1f seconds...", sleep_time)
                    time.sleep(sleep_time)
                    backoff = min(backoff * 2.0, 30.0)
                    continue

                if response.status_code >= 500:
                    logger.warning("HTTP %d server error (attempt %d/%d). Retrying in %.1f s...", response.status_code, attempt, max_retries, backoff)
                    time.sleep(backoff)
                    backoff = min(backoff * 2.0, 30.0)
                    continue

                # Any other unexpected 4xx code
                msg = f"HTTP {response.status_code} error from API: {response.text[:200]}"
                logger.error(msg)
                raise RuntimeError(msg)

            except requests.exceptions.Timeout:
                logger.warning("Timeout fetching page (attempt %d/%d).", attempt, max_retries)
                if attempt == max_retries:
                    raise
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)
            except requests.exceptions.RequestException as exc:
                logger.warning("Request error on attempt %d: %s", attempt, str(exc))
                if attempt == max_retries:
                    raise
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)

        raise RuntimeError(f"Failed to fetch page after {max_retries} attempts.")

    def _save_checkpoint(self, next_cursor: Optional[str]) -> None:
        """Write current collection checkpoint to disk."""
        checkpoint = {
            "page_number": self.total_pages,
            "next_cursor": next_cursor,
            "snapshot_watermark": self.snapshot_watermark,
            "records_fetched": self.total_records_received,
            "unique_records": len(self.seen_job_ids),
            "duplicate_records": self.duplicate_records_count,
            "country": self.country,
            "currentness": self.currentness,
            "limit": self.limit_per_page,
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)

    def _save_metadata(self, pagination_completed: bool) -> None:
        """Write comprehensive collection metadata."""
        completed_at = datetime.now(timezone.utc).isoformat()
        metadata = {
            "source_name": "Headcount Labs",
            "source_url": "https://headcountlabs.com",
            "endpoint": JOBS_ENDPOINT,
            "collection_started_at": self.collection_started_at,
            "collection_completed_at": completed_at if pagination_completed else None,
            "country": self.country,
            "currentness": self.currentness,
            "page_size": self.limit_per_page,
            "total_pages": self.total_pages,
            "total_records_received": self.total_records_received,
            "unique_job_ids": len(self.seen_job_ids),
            "duplicate_job_ids": self.duplicate_records_count,
            "snapshot_watermark": self.snapshot_watermark,
            "pagination_completed": pagination_completed,
            "errors": self.errors,
            "license": "ODbL 1.0 (Database), DbCL 1.0 (Database Contents)",
            "attribution": (
                "Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. "
                "Job descriptions belong to their employers. "
                "Location data © OpenStreetMap contributors and Overture Maps."
            ),
        }
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def load_existing_job_ids_from_file(self) -> None:
        """Read existing job IDs from JSONL file to prevent duplicate writes on resume."""
        if not os.path.exists(self.jobs_file):
            return
        with open(self.jobs_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        jid = record.get("job_id")
                        if jid:
                            self.seen_job_ids.add(jid)
                    except json.JSONDecodeError:
                        pass
        logger.info("Loaded %d existing job IDs from %s", len(self.seen_job_ids), self.jobs_file)

    def run(
        self,
        resume: bool = True,
        max_pages: Optional[int] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Execute the bulk collection loop.

        Returns summary dictionary.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        self.collection_started_at = datetime.now(timezone.utc).isoformat()

        current_cursor = None
        start_page = 1

        # Check for resume
        if resume and os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    chk = json.load(f)
                if (
                    chk.get("country") == self.country
                    and chk.get("currentness") == self.currentness
                    and chk.get("next_cursor")
                ):
                    current_cursor = chk.get("next_cursor")
                    self.total_pages = chk.get("page_number", 0)
                    self.snapshot_watermark = chk.get("snapshot_watermark")
                    self.total_records_received = chk.get("records_fetched", 0)
                    self.load_existing_job_ids_from_file()
                    start_page = self.total_pages + 1
                    logger.info("Resuming from checkpoint at page %d with cursor.", start_page)
            except Exception as e:
                logger.warning("Failed to load checkpoint (%s). Starting fresh.", e)

        if not current_cursor and not os.path.exists(self.jobs_file):
            # Fresh start: clear/initialize file
            open(self.jobs_file, "w", encoding="utf-8").close()

        pagination_completed = False
        page_num = start_page

        logger.info("Starting collection. Destination: %s", self.jobs_file)

        with open(self.jobs_file, "a", encoding="utf-8") as jsonl_out:
            while True:
                if max_pages and page_num > max_pages:
                    logger.info("Reached configured max_pages limit: %d", max_pages)
                    break

                if current_cursor and current_cursor in self.seen_cursors:
                    err_msg = f"Repeated cursor detected at page {page_num}. Halting pagination loop."
                    logger.error(err_msg)
                    self.errors.append(err_msg)
                    break

                if current_cursor:
                    self.seen_cursors.add(current_cursor)

                logger.info("Fetching page %d (limit=%d, cursor=%s)...", page_num, self.limit_per_page, "YES" if current_cursor else "NONE")

                try:
                    payload = self._fetch_page_with_retry(cursor=current_cursor)
                except Exception as exc:
                    err_msg = f"Fatal error fetching page {page_num}: {str(exc)}"
                    logger.error(err_msg)
                    self.errors.append(err_msg)
                    break

                # Official schema envelope validation
                if not isinstance(payload, dict) or "data" not in payload:
                    err_msg = f"Invalid response envelope at page {page_num}: missing 'data' field."
                    logger.error(err_msg)
                    self.errors.append(err_msg)
                    break

                jobs = payload.get("data") or []
                if not isinstance(jobs, list):
                    err_msg = f"Invalid 'data' field type at page {page_num}: expected list, got {type(jobs)}."
                    logger.error(err_msg)
                    self.errors.append(err_msg)
                    break

                if not self.snapshot_watermark:
                    self.snapshot_watermark = payload.get("snapshot_watermark")

                page_new_records = 0
                for job in jobs:
                    self.total_records_received += 1
                    jid = job.get("job_id") if isinstance(job, dict) else None
                    if jid:
                        if jid in self.seen_job_ids:
                            self.duplicate_records_count += 1
                            continue
                        self.seen_job_ids.add(jid)

                    jsonl_out.write(json.dumps(job, ensure_ascii=False) + "\n")
                    page_new_records += 1

                jsonl_out.flush()
                self.total_pages += 1
                logger.info(
                    "Page %d: received %d jobs (%d new unique, %d duplicates). Running total: %d unique.",
                    page_num,
                    len(jobs),
                    page_new_records,
                    len(jobs) - page_new_records,
                    len(self.seen_job_ids),
                )

                if dry_run:
                    logger.info("Dry-run requested: terminating after page 1.")
                    self._save_checkpoint(payload.get("next_cursor"))
                    self._save_metadata(pagination_completed=False)
                    return {
                        "dry_run": True,
                        "pages": 1,
                        "records": len(jobs),
                        "unique": len(self.seen_job_ids),
                    }

                next_cursor = payload.get("next_cursor")
                self._save_checkpoint(next_cursor)

                if not next_cursor or len(jobs) == 0:
                    logger.info("Pagination completed! No further next_cursor.")
                    pagination_completed = True
                    break

                current_cursor = next_cursor
                page_num += 1

        self._save_metadata(pagination_completed=pagination_completed)

        return {
            "success": pagination_completed and not self.errors,
            "total_pages": self.total_pages,
            "total_records_received": self.total_records_received,
            "unique_job_ids": len(self.seen_job_ids),
            "duplicate_job_ids": self.duplicate_records_count,
            "snapshot_watermark": self.snapshot_watermark,
            "output_file": self.jobs_file,
            "metadata_file": self.metadata_file,
            "errors": self.errors,
        }


def main() -> int:
    """CLI execution for bulk collection."""
    parser = argparse.ArgumentParser(description="HireTrends Headcount Labs Bulk Job Collector")
    parser.add_argument("--output-dir", default="data/raw/headcount", help="Output directory")
    parser.add_argument("--limit", type=int, default=DEFAULT_PAGE_SIZE, help="Records per page (max 250)")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum pages to fetch")
    parser.add_argument("--dry-run", action="store_true", help="Fetch 1 page dry-run only")
    parser.add_argument("--no-resume", action="store_true", help="Start from beginning ignoring checkpoint")

    args = parser.parse_args()

    collector = HeadcountBulkCollector(
        output_dir=args.output_dir,
        limit_per_page=args.limit,
    )

    result = collector.run(
        resume=not args.no_resume,
        max_pages=args.max_pages,
        dry_run=args.dry_run,
    )

    print("\nCOLLECTION SUMMARY:")
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") or result.get("dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())

"""Fetch a small, controlled sample of Headcount Labs Pakistan job records.

Executes:
GET https://api.headcountlabs.com/v1/jobs?country=PK&currentness=current&limit=10
Saves the exactly 10 returned records to data/samples/headcount_pakistan_sample.json.

SECURITY NOTICE:
HEADCOUNTLABS_API_KEY is loaded in memory via python-dotenv and NEVER logged,
printed, or written to disk.
"""

from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.FetchHeadcountSample")

API_ENDPOINT = "https://api.headcountlabs.com/v1/jobs"
DEFAULT_TIMEOUT = 30
TARGET_SAMPLE_PATH = "data/samples/headcount_pakistan_sample.json"


def fetch_headcount_sample(
    country: str = "PK",
    currentness: str = "current",
    limit: int = 10,
    timeout: int = DEFAULT_TIMEOUT,
    output_path: str = TARGET_SAMPLE_PATH,
) -> Dict[str, Any]:
    """Fetch exactly `limit` job records for Pakistan and save to output_path."""
    load_dotenv()
    api_key = os.getenv("HEADCOUNTLABS_API_KEY")

    if not api_key or not api_key.strip():
        logger.error("Authentication error: HEADCOUNTLABS_API_KEY is not set in .env")
        return {
            "success": False,
            "status_code": None,
            "error": "HEADCOUNTLABS_API_KEY missing from environment",
            "records": [],
        }

    clean_key = api_key.strip()
    headers = {
        "Authorization": f"Bearer {clean_key}",
        "Accept": "application/json",
        "User-Agent": (
            "HireTrendsResearchBot/1.0 "
            "(+https://github.com/Awaisbacha55/hiretrends-pakistan-job-market; research project)"
        ),
    }
    params = {
        "country": country,
        "currentness": currentness,
        "limit": limit,
    }

    logger.info("Requesting sample: %s with params %s", API_ENDPOINT, params)

    try:
        response = requests.get(
            API_ENDPOINT,
            headers=headers,
            params=params,
            timeout=timeout,
        )

        logger.info("Received HTTP status code: %d", response.status_code)

        if response.status_code != 200:
            logger.error("API error response: %s", response.text[:200])
            return {
                "success": False,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "records": [],
            }

        payload = response.json()

        # Handle different potential packaging schemas (list, dict with results/jobs/data)
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            for key in ("results", "jobs", "data", "items"):
                if key in payload and isinstance(payload[key], list):
                    records = payload[key]
                    break
            else:
                # If it's a dict without an array container, keep values if array
                records = [payload]
        else:
            records = []

        logger.info("Extracted %d raw records from response payload.", len(records))

        # Enforce exact limit
        records = records[:limit]

        # Ensure target directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        logger.info("Successfully saved %d records to %s", len(records), output_path)

        return {
            "success": True,
            "status_code": 200,
            "error": None,
            "record_count": len(records),
            "output_path": output_path,
            "records": records,
        }

    except requests.exceptions.Timeout:
        logger.error("Timeout after %d seconds requesting %s", timeout, API_ENDPOINT)
        return {
            "success": False,
            "status_code": None,
            "error": f"Request timed out after {timeout} seconds",
            "records": [],
        }
    except requests.exceptions.RequestException as exc:
        logger.error("Request failed: %s", str(exc))
        return {
            "success": False,
            "status_code": None,
            "error": f"Request exception: {str(exc)}",
            "records": [],
        }


def analyze_sample_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the fields present and missing across the sample records."""
    if not records:
        return {"total_records": 0}

    total = len(records)
    all_fields = set()
    field_counts: Dict[str, int] = {}

    salary_count = 0
    desc_count = 0
    locations_count = 0
    work_arrangement_count = 0
    emp_type_count = 0

    for rec in records:
        for k, v in rec.items():
            all_fields.add(k)
            if v is not None and v != "" and v != []:
                field_counts[k] = field_counts.get(k, 0) + 1

        # Check salary / pay
        pay_val = rec.get("pay") or rec.get("salary") or rec.get("compensation")
        if pay_val:
            if isinstance(pay_val, dict):
                if pay_val.get("state") == "known" or pay_val.get("min") or pay_val.get("value"):
                    salary_count += 1
            else:
                salary_count += 1

        # Check description
        desc_val = rec.get("description") or rec.get("description_html") or rec.get("job_description")
        if desc_val:
            if isinstance(desc_val, dict):
                if desc_val.get("value") or desc_val.get("state") == "known":
                    desc_count += 1
            elif isinstance(desc_val, str) and desc_val.strip():
                desc_count += 1

        # Check locations
        locs_val = rec.get("locations") or rec.get("location")
        if locs_val:
            if isinstance(locs_val, list) and len(locs_val) > 0:
                locations_count += 1
            elif isinstance(locs_val, dict) and locs_val.get("value"):
                locations_count += 1
            elif isinstance(locs_val, str) and locs_val.strip():
                locations_count += 1

        # Check work arrangement
        wa_val = rec.get("work_arrangement") or rec.get("workplace_type")
        if wa_val:
            if isinstance(wa_val, dict) and (wa_val.get("value") or wa_val.get("state") == "known"):
                work_arrangement_count += 1
            elif isinstance(wa_val, str) and wa_val.strip():
                work_arrangement_count += 1

        # Check employment type
        et_val = rec.get("employment_type")
        if et_val:
            if isinstance(et_val, dict) and (et_val.get("value") or et_val.get("state") == "known"):
                emp_type_count += 1
            elif isinstance(et_val, str) and et_val.strip():
                emp_type_count += 1

    return {
        "total_records": total,
        "all_fields": sorted(list(all_fields)),
        "field_population_counts": field_counts,
        "salary_available_count": salary_count,
        "description_available_count": desc_count,
        "locations_available_count": locations_count,
        "work_arrangement_available_count": work_arrangement_count,
        "employment_type_available_count": emp_type_count,
    }


def main() -> int:
    """Fetch sample, save to file, and print analysis summary."""
    result = fetch_headcount_sample()
    if not result["success"]:
        print(f"[ERROR] Failed to fetch sample: {result['error']}")
        return 1

    records = result["records"]
    analysis = analyze_sample_records(records)

    print("=" * 65)
    print("HIRETRENDS — HEADCOUNT LABS SAMPLE DATA ANALYSIS")
    print("=" * 65)
    print(f"Total Records Fetched:           {analysis['total_records']}")
    print(f"Salary / Pay Data Present:       {analysis['salary_available_count']} / {analysis['total_records']}")
    print(f"Description Data Present:        {analysis['description_available_count']} / {analysis['total_records']}")
    print(f"Locations Data Present:          {analysis['locations_available_count']} / {analysis['total_records']}")
    print(f"Work Arrangement Data Present:   {analysis['work_arrangement_available_count']} / {analysis['total_records']}")
    print(f"Employment Type Present:         {analysis['employment_type_available_count']} / {analysis['total_records']}")
    print("-" * 65)
    print("All Observed Field Names in Payload:")
    for f in analysis["all_fields"]:
        pop = analysis["field_population_counts"].get(f, 0)
        print(f"  - {f:<30} (populated in {pop}/{analysis['total_records']} records)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())

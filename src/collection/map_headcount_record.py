"""HireTrends Headcount Labs Record Mapper.

Transforms Headcount Labs state-wrapped job objects into the standardized
HireTrends internal representation without losing data lineage or inventing values.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def extract_state_value(obj: Any) -> Optional[Any]:
    """Extract value from Headcount Labs state-wrapped object.

    Headcount Labs objects follow the pattern:
        {"state": "known" | "source_omitted" | "extraction_failed", "value": ...}
    Only returns `value` when `state == 'known'`. Otherwise returns None.
    """
    if not isinstance(obj, dict):
        return obj if obj is not None else None

    state = obj.get("state")
    if state == "known":
        return obj.get("value")
    # For source_omitted, extraction_failed, or any other state, return None
    return None


def extract_locations(locations_list: Any) -> Dict[str, Any]:
    """Parse locations array and extract primary city, region, country, and all locations.

    Returns:
        {
            "primary_city": str | None,
            "primary_region": str | None,
            "primary_country": str | None,
            "all_locations": list
        }
    """
    if not isinstance(locations_list, list) or not locations_list:
        return {
            "primary_city": None,
            "primary_region": None,
            "primary_country": None,
            "all_locations": [],
        }

    known_locations = []
    primary_city = None
    primary_region = None
    primary_country = None

    for loc in locations_list:
        if isinstance(loc, dict) and loc.get("state") == "known":
            val = loc.get("value", {})
            if isinstance(val, dict):
                known_locations.append(val)
                if not primary_city and val.get("city"):
                    primary_city = val.get("city")
                if not primary_region and val.get("region"):
                    primary_region = val.get("region")
                if not primary_country and val.get("country"):
                    primary_country = val.get("country")
        elif isinstance(loc, dict) and "city" in loc:
            known_locations.append(loc)
            if not primary_city and loc.get("city"):
                primary_city = loc.get("city")
            if not primary_region and loc.get("region"):
                primary_region = loc.get("region")
            if not primary_country and loc.get("country"):
                primary_country = loc.get("country")

    return {
        "primary_city": primary_city,
        "primary_region": primary_region,
        "primary_country": primary_country,  # Never default missing country to "PK"
        "all_locations": known_locations,
    }


def extract_salary_info(postings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract compensation data from postings without inventing figures.

    Missing values are strictly returned as None (null), never zero.
    """
    salary_text = None
    salary_min_pkr = None
    salary_max_pkr = None

    if not isinstance(postings, list):
        return {
            "salary_text": None,
            "salary_min_pkr": None,
            "salary_max_pkr": None,
        }

    for p in postings:
        if not isinstance(p, dict):
            continue
        pay = p.get("pay")
        if isinstance(pay, dict) and pay.get("state") == "known":
            val = pay.get("value")
            if isinstance(val, dict):
                curr = val.get("currency")
                min_val = val.get("min_amount") or val.get("min")
                max_val = val.get("max_amount") or val.get("max")
                interval = val.get("interval") or val.get("unit")
                salary_text = f"{curr or ''} {min_val or ''} - {max_val or ''} ({interval or ''})".strip()
                if curr == "PKR":
                    salary_min_pkr = float(min_val) if min_val is not None else None
                    salary_max_pkr = float(max_val) if max_val is not None else None
                break
            elif isinstance(val, (int, float)):
                salary_text = str(val)
                salary_min_pkr = float(val)
                break

    return {
        "salary_text": salary_text,
        "salary_min_pkr": salary_min_pkr,
        "salary_max_pkr": salary_max_pkr,
    }


def map_headcount_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw Headcount Labs API record into the HireTrends internal representation.

    Guarantees:
    - Missing fields are null (None), not 0 or false defaults.
    - All postings and locations are preserved.
    - Lineage attributes (job_id, company_id, timestamps) are retained.
    """
    job_id = raw_job.get("job_id") or ""
    title = extract_state_value(raw_job.get("title"))
    company = extract_state_value(raw_job.get("employer_name"))
    description = extract_state_value(raw_job.get("description"))
    work_arrangement = extract_state_value(raw_job.get("work_arrangement"))

    loc_info = extract_locations(raw_job.get("locations"))

    postings = raw_job.get("postings", [])
    salary_info = extract_salary_info(postings)

    # Postings URLs and sources
    primary_source_name = "headcount_labs"
    primary_job_url = None
    primary_source_url = None
    posted_date = None

    if postings and isinstance(postings, list):
        p0 = postings[0] if isinstance(postings[0], dict) else {}
        app_url_val = extract_state_value(p0.get("application_url")) or p0.get("application_url")
        if isinstance(app_url_val, dict):
            app_url_val = app_url_val.get("value") or app_url_val.get("url")
        post_url_val = extract_state_value(p0.get("posting_url")) or p0.get("posting_url")
        if isinstance(post_url_val, dict):
            post_url_val = post_url_val.get("value") or post_url_val.get("url")

        primary_job_url = str(app_url_val) if app_url_val else (str(post_url_val) if post_url_val else None)
        primary_source_url = str(post_url_val) if post_url_val else None
        posted_date = p0.get("source_posted_at")
        if p0.get("source"):
            primary_source_name = f"headcount_labs:{p0.get('source')}"

    if not posted_date:
        posted_date = raw_job.get("job_first_seen_at")

    now_utc = datetime.now(timezone.utc).isoformat()

    return {
        "job_id": job_id,
        "job_title": title,
        "company": company,
        "city": loc_info["primary_city"],
        "region": loc_info["primary_region"],
        "country": loc_info["primary_country"],
        "all_locations": loc_info["all_locations"],
        "salary_text": salary_info["salary_text"],
        "salary_min_pkr": salary_info["salary_min_pkr"],
        "salary_max_pkr": salary_info["salary_max_pkr"],
        "experience_text": None,  # Parsed in Day 2/3 NLP phase
        "employment_type": None,  # Inferred in Day 2/3 NLP phase
        "workplace_type": work_arrangement,
        "description": description,
        "posted_date": posted_date,
        "job_first_seen_at": raw_job.get("job_first_seen_at"),
        "job_updated_at": raw_job.get("job_updated_at"),
        "source": primary_source_name,
        "source_url": primary_source_url,
        "job_url": primary_job_url,
        "postings_count": len(postings) if isinstance(postings, list) else 0,
        "postings": postings,
        "raw_company_id": raw_job.get("company_id"),
        "currentness": raw_job.get("currentness"),
        "stale": raw_job.get("stale"),
        "collected_at": now_utc,
    }

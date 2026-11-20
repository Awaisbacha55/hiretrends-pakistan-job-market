"""HireTrends Data Quality Engine.

Audits cleaned records for missing values, duplicates, range violations,
unmapped geographic attributes, skill coverage, and manual-review requirements.
"""

from collections import Counter
from datetime import datetime
import re
from typing import Any, Dict, List, Optional


def perform_quality_checks(cleaned_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run comprehensive quality assurance checks on cleaned records.

    Returns:
        Structured dictionary of quality indicators and statistics.
    """
    total = len(cleaned_records)
    if total == 0:
        return {"total_records": 0, "status": "EMPTY_DATASET"}

    seen_job_ids = set()
    duplicate_job_ids = 0

    seen_job_urls = set()
    duplicate_job_urls = 0

    missing_fields: Counter = Counter()

    invalid_dates = 0
    invalid_salary_ranges = 0
    invalid_experience_ranges = 0
    unmapped_cities = 0
    unknown_workplaces = 0
    records_with_skills = 0
    manual_review_count = 0

    for rec in cleaned_records:
        # 1. Duplicates
        jid = rec.get("job_id")
        if jid:
            if jid in seen_job_ids:
                duplicate_job_ids += 1
            else:
                seen_job_ids.add(jid)

        jurl = rec.get("job_url")
        if isinstance(jurl, dict):
            jurl = str(jurl.get("value") or jurl.get("url") or jurl)
        elif jurl is not None and not isinstance(jurl, str):
            jurl = str(jurl)
        if jurl:
            if jurl in seen_job_urls:
                duplicate_job_urls += 1
            else:
                seen_job_urls.add(jurl)

        # 2. Missing Fields
        for field in [
            "job_id",
            "job_title",
            "company",
            "normalized_city",
            "workplace_type",
            "salary_min_pkr",
            "experience_min_years",
            "description",
            "posted_date",
        ]:
            val = rec.get(field)
            if val is None or val == "":
                missing_fields[field] += 1

        # 3. Date Validation
        pdate = rec.get("posted_date")
        if pdate:
            try:
                # Expect ISO format YYYY-MM-DD
                datetime.fromisoformat(str(pdate)[:10])
            except ValueError:
                invalid_dates += 1

        # 4. Salary Range Validation
        s_min = rec.get("salary_min_pkr")
        s_max = rec.get("salary_max_pkr")
        if s_min is not None and s_max is not None:
            if s_min < 0 or s_max < 0 or s_min > s_max:
                invalid_salary_ranges += 1

        # 5. Experience Range Validation
        e_min = rec.get("experience_min_years")
        e_max = rec.get("experience_max_years")
        if e_min is not None and e_max is not None:
            if e_min < 0 or e_max < 0 or e_min > e_max or e_max > 40:
                invalid_experience_ranges += 1

        # 6. Unmapped Cities & Workplace
        if not rec.get("normalized_city"):
            unmapped_cities += 1

        if not rec.get("workplace_type"):
            unknown_workplaces += 1

        # 7. Skills Coverage
        skills = rec.get("skills")
        if skills and (isinstance(skills, list) and len(skills) > 0 or isinstance(skills, str) and len(skills) > 2):
            records_with_skills += 1

        # 8. Manual Review
        if rec.get("needs_manual_review"):
            manual_review_count += 1

    return {
        "total_records": total,
        "unique_job_ids": len(seen_job_ids),
        "duplicate_job_ids": duplicate_job_ids,
        "duplicate_job_urls": duplicate_job_urls,
        "missing_fields": dict(missing_fields),
        "missing_percentages": {k: round(v / total * 100, 2) for k, v in missing_fields.items()},
        "invalid_dates": invalid_dates,
        "invalid_salary_ranges": invalid_salary_ranges,
        "invalid_experience_ranges": invalid_experience_ranges,
        "unmapped_cities": unmapped_cities,
        "unknown_workplaces": unknown_workplaces,
        "records_with_skills": records_with_skills,
        "skill_coverage_pct": round(records_with_skills / total * 100, 2),
        "manual_review_count": manual_review_count,
        "manual_review_pct": round(manual_review_count / total * 100, 2),
    }

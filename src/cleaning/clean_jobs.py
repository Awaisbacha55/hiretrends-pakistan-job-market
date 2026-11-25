"""HireTrends Job Data Cleaning and Normalization Pipeline.

Loads raw Headcount Labs JSON Lines, normalizes job titles, Pakistani cities,
workplace arrangements, experience requirements, compensation metrics, and extracts technical skills.
Saves processed tabular dataset to data/processed/jobs_cleaned.csv and generates reports/data_cleaning_report.md.
"""

from collections import Counter
from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode

import pandas as pd

from .city_normalizer import normalize_location
from .experience_parser import parse_experience
from .quality_checks import perform_quality_checks
from .salary_parser import parse_salary
from .skill_extractor import SkillExtractor
from .title_normalizer import normalize_title
from .workplace_normalizer import normalize_workplace_type
from src.collection.classify_technology_jobs import classify_job
from src.collection.map_headcount_record import map_headcount_job

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.DataCleaning")

# Query parameters to strip during URL normalization (tracking/attribution params)
_TRACKING_PARAMS = frozenset({
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "source", "ref", "referer", "referrer", "fbclid", "gclid", "li_fat_id",
})


def normalize_job_url(url: Optional[str]) -> Optional[str]:
    """Normalize a job URL for deterministic deduplication.

    Steps:
    1. Strip leading/trailing whitespace.
    2. Lowercase the scheme and hostname (path case is preserved).
    3. Remove trailing slashes from the path.
    4. Remove URL fragments (#...).
    5. Remove known tracking query parameters (utm_*, source, ref, etc.).
    6. Sort remaining query parameters for deterministic comparison.

    Returns None if input is None, empty, or not a valid URL.
    """
    if url is None or not isinstance(url, str):
        return None
    url = url.strip()
    if not url:
        return None

    try:
        parsed = urlparse(url)
    except Exception:
        return None

    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()
    if scheme not in ("http", "https") or not netloc:
        return None

    path = parsed.path.rstrip("/") if parsed.path else ""

    # Filter tracking query params and sort the rest
    if parsed.query:
        qs = parse_qs(parsed.query, keep_blank_values=True)
        filtered = {k: v for k, v in qs.items() if k.lower() not in _TRACKING_PARAMS}
        sorted_query = urlencode(filtered, doseq=True) if filtered else ""
    else:
        sorted_query = ""

    # Reconstruct without fragment
    normalized = f"{scheme}://{netloc}{path}"
    if sorted_query:
        normalized += f"?{sorted_query}"
    return normalized


def _record_completeness_score(rec: Dict[str, Any]) -> int:
    """Count the number of non-null, non-empty fields in a cleaned record.

    Used to pick the most complete representative when deduplicating.
    """
    score = 0
    for key, val in rec.items():
        if val is None:
            continue
        if isinstance(val, str) and val.strip() == "":
            continue
        if isinstance(val, float) and val != val:  # NaN check
            continue
        score += 1
    return score


def clean_single_record(
    raw_job: Dict[str, Any],
    skill_extractor: SkillExtractor,
) -> Dict[str, Any]:
    """Clean, normalize, and enrich a single job record."""
    # 1. Map to baseline schema
    mapped = map_headcount_job(raw_job)

    # 2. Normalize title and seniority
    title_info = normalize_title(mapped.get("job_title"))
    norm_title = title_info["normalized_title"]
    seniority = title_info["seniority_level"]

    # 3. Normalize location
    loc_info = normalize_location(
        city=mapped.get("city"),
        region=mapped.get("region"),
        country=mapped.get("country"),
        all_locations=mapped.get("all_locations"),
    )

    # 4. Normalize workplace arrangement
    workplace = normalize_workplace_type(
        raw_workplace=mapped.get("workplace_type"),
        title=norm_title,
        description=mapped.get("description"),
    )

    # 5. Parse experience
    full_text = f"{norm_title}\n{mapped.get('description') or ''}"
    exp_info = parse_experience(full_text)

    # 6. Parse and normalize salary
    structured_pay = None
    postings = raw_job.get("postings", [])
    if postings and isinstance(postings, list) and isinstance(postings[0], dict):
        structured_pay = postings[0].get("pay")

    salary_info = parse_salary(
        salary_text=mapped.get("salary_text"),
        structured_pay=structured_pay,
    )

    # 7. Extract technical skills
    skill_info = skill_extractor.extract_skills(full_text)
    skills_list = skill_info["skills"]

    # 8. Technology classification & audit
    cls_info = classify_job(norm_title, mapped.get("description"))

    raw_job_url = mapped.get("job_url")
    if isinstance(raw_job_url, dict):
        job_url_str = str(raw_job_url.get("value") or raw_job_url.get("url") or raw_job_url)
    elif raw_job_url is not None:
        job_url_str = str(raw_job_url)
    else:
        job_url_str = None

    return {
        "job_id": mapped["job_id"],
        "job_title": mapped["job_title"],
        "normalized_title": norm_title,
        "seniority_level": seniority,
        "company": mapped["company"],
        "city": mapped["city"],
        "normalized_city": loc_info["normalized_city"],
        "region": loc_info["normalized_region"],
        "country": loc_info["normalized_country"],
        "is_pakistan_location": loc_info["is_pakistan"],
        "workplace_type": workplace,
        "experience_text": exp_info["experience_text"],
        "experience_min_years": exp_info["experience_min_years"],
        "experience_max_years": exp_info["experience_max_years"],
        "salary_text": salary_info["salary_text"],
        "salary_currency": salary_info["salary_currency"],
        "salary_interval": salary_info["salary_interval"],
        "salary_min_original": salary_info["salary_min_original"],
        "salary_max_original": salary_info["salary_max_original"],
        "salary_min_pkr": salary_info["salary_min_pkr"],
        "salary_max_pkr": salary_info["salary_max_pkr"],
        "salary_is_converted": salary_info["salary_is_converted"],
        "skills": json.dumps(skills_list),
        "skills_count": len(skills_list),
        "is_technology_job": cls_info["is_technology_job"],
        "technology_category": cls_info["technology_category"],
        "classification_confidence": cls_info["classification_confidence"],
        "classification_reason": cls_info["classification_reason"],
        "needs_manual_review": cls_info["needs_manual_review"],
        "posted_date": str(mapped.get("posted_date") or "")[:10] if mapped.get("posted_date") else None,
        "source": mapped["source"],
        "job_url": job_url_str,
        "collected_at": mapped["collected_at"],
    }


def run_cleaning_pipeline(
    raw_path: str = "data/raw/headcount/jobs_raw.jsonl",
    output_csv: str = "data/processed/jobs_cleaned.csv",
    metadata_output: str = "data/processed/cleaning_metadata.json",
    report_output: str = "reports/data_cleaning_report.md",
) -> Dict[str, Any]:
    """Execute the complete data cleaning and normalization pipeline."""
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at: {raw_path}")

    logger.info("Initializing SkillExtractor from config/skills_dictionary.json...")
    extractor = SkillExtractor()

    logger.info("Reading raw records from %s...", raw_path)
    cleaned_records = []
    input_records_count = 0
    raw_job_ids = set()
    duplicate_raw_id_count = 0

    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            input_records_count += 1
            try:
                raw_job = json.loads(line_str)
            except json.JSONDecodeError:
                continue

            jid = raw_job.get("job_id")
            if jid:
                if jid in raw_job_ids:
                    duplicate_raw_id_count += 1
                    continue
                raw_job_ids.add(jid)

            cleaned = clean_single_record(raw_job, extractor)
            cleaned_records.append(cleaned)

    logger.info("Cleaned %d unique-ID records (input: %d, raw ID duplicates: %d).",
                len(cleaned_records), input_records_count, duplicate_raw_id_count)

    # ===================================================================
    # TWO-TIER SEMANTIC DEDUPLICATION
    # ===================================================================
    # Tier 1: Deduplicate on normalized job_url (primary identity)
    # Tier 2: Fallback dedup on (normalized_title, company, normalized_city, posted_date)
    # ===================================================================
    pre_dedup_count = len(cleaned_records)
    url_dupes_removed = 0
    fallback_dupes_removed = 0
    url_dupes_log: List[Dict[str, str]] = []
    fallback_dupes_log: List[Dict[str, str]] = []

    # --- Tier 1: URL-based deduplication ---
    url_groups: Dict[str, List[int]] = {}  # normalized_url -> list of indices
    no_url_indices: List[int] = []

    for idx, rec in enumerate(cleaned_records):
        raw_url = rec.get("job_url")
        norm_url = normalize_job_url(raw_url)
        if norm_url:
            url_groups.setdefault(norm_url, []).append(idx)
        else:
            no_url_indices.append(idx)

    keep_indices = set()
    for norm_url, indices in url_groups.items():
        if len(indices) == 1:
            keep_indices.add(indices[0])
        else:
            # Pick the record with the highest completeness score;
            # break ties deterministically with earliest collected_at, then job_id.
            best_idx = min(indices, key=lambda i: (
                -_record_completeness_score(cleaned_records[i]),
                cleaned_records[i].get("collected_at") or "9999",
                cleaned_records[i].get("job_id") or "",
            ))
            keep_indices.add(best_idx)
            for i in indices:
                if i != best_idx:
                    url_dupes_removed += 1
                    url_dupes_log.append({
                        "removed_job_id": cleaned_records[i]["job_id"],
                        "kept_job_id": cleaned_records[best_idx]["job_id"],
                        "job_url": norm_url,
                        "reason": "duplicate_url",
                    })

    # --- Tier 2: Fallback deduplication ONLY for records without a usable URL ---
    # Deduplicate on normalized (title, company, city, posted_date)
    fallback_groups: Dict[str, List[int]] = {}
    for idx in no_url_indices:
        rec = cleaned_records[idx]
        title_norm = " ".join(str(rec.get("normalized_title") or rec.get("job_title") or "").split()).lower()
        company_norm = " ".join(str(rec.get("company") or "").split()).lower()
        city_norm = " ".join(str(rec.get("normalized_city") or rec.get("city") or "").split()).lower()
        date_norm = " ".join(str(rec.get("posted_date") or "").split())
        fallback_key = f"{title_norm}|{company_norm}|{city_norm}|{date_norm}"
        fallback_groups.setdefault(fallback_key, []).append(idx)

    for fb_key, indices in fallback_groups.items():
        if len(indices) == 1:
            keep_indices.add(indices[0])
        else:
            best_idx = min(indices, key=lambda i: (
                -_record_completeness_score(cleaned_records[i]),
                cleaned_records[i].get("collected_at") or "9999",
                cleaned_records[i].get("job_id") or "",
            ))
            keep_indices.add(best_idx)
            for i in indices:
                if i != best_idx:
                    fallback_dupes_removed += 1
                    fallback_dupes_log.append({
                        "removed_job_id": cleaned_records[i]["job_id"],
                        "kept_job_id": cleaned_records[best_idx]["job_id"],
                        "fallback_key": fb_key,
                        "reason": "duplicate_title_company_city_date",
                    })

    final_records = [cleaned_records[i] for i in sorted(keep_indices)]
    total_dupes_removed = url_dupes_removed + fallback_dupes_removed

    logger.info("Tier 1 (URL dedup): %d URL duplicates removed.", url_dupes_removed)
    logger.info("Tier 2 (fallback dedup on %d URL-less records): %d fallback duplicates removed.",
                len(no_url_indices), fallback_dupes_removed)
    logger.info("Total duplicates removed: %d (%d -> %d records).",
                total_dupes_removed, pre_dedup_count, len(final_records))

    # Convert to DataFrame
    df = pd.DataFrame(final_records)

    # Save to processed CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    logger.info("Saved cleaned dataset to %s (%d rows, %d columns)", output_csv, len(df), len(df.columns))

    # Perform Quality Assurance Checks
    quality_metrics = perform_quality_checks(final_records)

    # Aggregations for report
    all_skills_flat = []
    for r in final_records:
        s_list = json.loads(r["skills"]) if isinstance(r["skills"], str) else []
        all_skills_flat.extend(s_list)

    skill_counts = Counter(all_skills_flat)
    top_20_skills = skill_counts.most_common(20)

    # City distributions
    city_counts = Counter(df["normalized_city"].dropna())
    workplace_counts = Counter(df["workplace_type"].dropna())
    seniority_counts = Counter(df["seniority_level"].dropna())
    tech_counts = Counter(df["technology_category"].dropna())

    sal_present = int(df["salary_min_pkr"].notna().sum())
    exp_present = int(df["experience_min_years"].notna().sum())
    tech_present = int(df["is_technology_job"].sum())

    # Unique URL count in final dataset
    final_unique_urls = df["job_url"].dropna().nunique()

    # Metadata
    metadata = {
        "pipeline_name": "HireTrends Data Cleaning & Normalization Engine",
        "pipeline_version": "2.0.0",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "input_records": input_records_count,
        "unique_id_records": pre_dedup_count,
        "output_records": len(df),
        "deduplication": {
            "raw_id_duplicates_removed": duplicate_raw_id_count,
            "url_duplicates_removed": url_dupes_removed,
            "fallback_duplicates_removed": fallback_dupes_removed,
            "total_duplicates_removed": total_dupes_removed,
            "dedup_method": "two_tier: normalized_job_url (primary) + normalized_title|company|city|date (fallback)",
            "url_normalization": "lowercase scheme+host, strip trailing slashes, remove tracking params (utm_*), remove fragments, sort query params",
            "selection_rule": "keep record with highest field-completeness score; earliest collected_at as tiebreaker",
        },
        "unique_job_urls_remaining": final_unique_urls,
        "removed_duplicates": total_dupes_removed,
        "tech_roles_count": tech_present,
        "disclosed_salary_count": sal_present,
        "parsed_experience_count": exp_present,
        "total_skills_extracted": len(all_skills_flat),
        "unique_skills_found": len(skill_counts),
        "top_skills": top_20_skills,
        "quality_metrics": quality_metrics,
        "source_license": "ODbL 1.0 & DbCL 1.0 (Headcount Labs)",
    }

    with open(metadata_output, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Save deduplication log for auditability
    dedup_log_path = os.path.join(os.path.dirname(metadata_output), "deduplication_log.json")
    dedup_log = {
        "url_duplicates": url_dupes_log,
        "fallback_duplicates": fallback_dupes_log,
        "total_removed": total_dupes_removed,
    }
    with open(dedup_log_path, "w", encoding="utf-8") as f:
        json.dump(dedup_log, f, indent=2)

    # Generate Markdown Report
    _generate_cleaning_report(
        report_output,
        metadata,
        city_counts,
        workplace_counts,
        seniority_counts,
        tech_counts,
        top_20_skills,
        sal_present,
        exp_present,
        len(df),
    )

    return metadata


def _generate_cleaning_report(
    report_path: str,
    meta: Dict[str, Any],
    city_counts: Counter,
    workplace_counts: Counter,
    seniority_counts: Counter,
    tech_counts: Counter,
    top_20_skills: List[Tuple[str, int]],
    sal_count: int,
    exp_count: int,
    total_records: int,
) -> None:
    """Generate reports/data_cleaning_report.md."""
    qm = meta.get("quality_metrics", {})
    dedup = meta.get("deduplication", {})
    input_count = max(meta["input_records"], 1)
    removed_pct = meta["removed_duplicates"] / input_count * 100
    output_pct = meta["output_records"] / input_count * 100
    lines = [
        "# HireTrends — Day 3 Data Cleaning, Normalization & Skill Extraction Report",
        "",
        f"**Pipeline Execution Timestamp:** {meta['processed_at']}  ",
        "**Input Source Dataset:** `data/raw/headcount/jobs_raw.jsonl`  ",
        "**Processed Tabular Output:** `data/processed/jobs_cleaned.csv`  ",
        "**Attribution & License:** Open Database License (ODbL 1.0 & DbCL 1.0 (Headcount Labs)  ",
        "",
        "---",
        "",
        "## 1. Pipeline Execution Summary",
        "",
        "| Metric | Count | % of Input | Notes |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Raw Input Records** | **{meta['input_records']:,}** | 100.0% | Ingested from Headcount Labs Pakistan feed |",
        f"| **Duplicates Removed (URL)** | **{dedup.get('url_duplicates_removed', 0):,}** | {dedup.get('url_duplicates_removed', 0)/input_count*100:.1f}% | Normalized `job_url` primary deduplication |",
        f"| **Duplicates Removed (Fallback)** | **{dedup.get('fallback_duplicates_removed', 0):,}** | {dedup.get('fallback_duplicates_removed', 0)/input_count*100:.1f}% | Normalized `(title, company, city, posted_date)` for URL-less records |",
        f"| **Total Duplicates Removed** | **{meta['removed_duplicates']:,}** | {removed_pct:.1f}% | Two-tier deterministic deduplication |",
        f"| **Cleaned Output Records** | **{meta['output_records']:,}** | {output_pct:.1f}% | Unique job postings in standardized schema |",
        f"| **Technology Roles** | **{meta.get('tech_roles_count', 0):,} Tech** | {meta.get('tech_roles_count', 0)/max(total_records, 1)*100:.1f}% Tech | Segmented via high-confidence taxonomy |",
        f"| **Non-Technology Roles** | **{tech_counts.get('Non-Technology', 0):,} Non-Tech** | {tech_counts.get('Non-Technology', 0)/max(total_records, 1)*100:.1f}% Non-Tech | Operations, sales, medical, customer service |",
        f"| **Manual Review Flagged** | **{qm.get('manual_review_count', 0):,}** | {qm.get('manual_review_pct', 0.0)}% | Ambiguous titles flagged transparently |",
        "",
        "---",
        "",
        "## 2. Salary & Compensation Extraction Analysis",
        "",
        "| Metric | Total Value | Percentage | Observation |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Disclosed Salaries Parsed** | **{sal_count:,}** | **{sal_count/max(total_records, 1)*100:.2f}%** | Explicit compensation ranges |",
        f"| **Missing / Undisclosed Salaries** | **{total_records - sal_count:,}** | **{(total_records - sal_count)/max(total_records, 1)*100:.2f}%** | Preserved as null (`NaN`), never 0 |",
        f"| **Currency Conversion Standard** | Monthly PKR | - | Official State Bank of Pakistan rates (USD 278.50) |",
        f"| **Annual to Monthly Normalization** | Applied | - | Divided annual wages by 12.0 |",
        "",
        "---",
        "",
        "## 3. Experience Requirements Analysis",
        "",
        "| Metric | Total Value | Percentage | Observation |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Parsed Experience Requirements** | **{exp_count:,}** | **{exp_count/max(total_records, 1)*100:.1f}%** | Extracted min/max years from text |",
        f"| **Missing Experience Requirements** | **{total_records - exp_count:,}** | **{(total_records - exp_count)/max(total_records, 1)*100:.1f}%** | Preserved as null, not guessed |",
        "",
        "---",
        "",
        "## 4. Technical Skill Extraction & Top 20 Demanded Skills",
        "",
        f"- **Total Skill Mentions Extracted:** {meta['total_skills_extracted']:,}",
        f"- **Unique Skills Identified:** {meta['unique_skills_found']:,}",
        f"- **Listings with Technical Skills:** {qm.get('records_with_skills', 0):,} ({qm.get('skill_coverage_pct', 0.0)}%)",
        "",
        "### Top 20 Most Demanded Skills in Pakistan Tech Jobs:",
        "",
        "| Rank | Technical Skill | Category | Mentions Count | % of All Postings |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for rank, (skill_name, count) in enumerate(top_20_skills, start=1):
        lines.append(f"| {rank} | **{skill_name}** | Technical Taxonomy | {count:,} | {count/max(total_records, 1)*100:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Geographic Normalization & City Distribution",
        "",
        "Pakistani cities were normalized to standard canonical spellings. Foreign cities (e.g. Cairo, Turkey) were partitioned as foreign non-PK locations. Remote is tracked as a workplace arrangement.",
        "",
        "| Standardized Pakistani City | Province / Region | Listings Count | % of Mapped Cities |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for city, count in city_counts.most_common(12):
        lines.append(f"| **{city}** | Pakistan | {count:,} | {count/max(sum(city_counts.values()), 1)*100:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Workplace Arrangement Distribution",
        "",
        "| Workplace Type | Count | % of Known Arrangements | Notes |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for wp, count in workplace_counts.most_common():
        lines.append(f"| **{wp.capitalize()}** | {count:,} | {count/max(sum(workplace_counts.values()), 1)*100:.1f}% | Standardized |")

    lines.extend([
        "",
        "---",
        "",
        "## 7. Seniority Level Distribution",
        "",
        "| Seniority Level | Listings Count | % of Total Postings |",
        "| :--- | :--- | :--- |",
    ])

    for sen, count in seniority_counts.most_common():
        lines.append(f"| **{sen}** | {count:,} | {count/max(total_records, 1)*100:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 8. Data Quality Assurance Audit",
        "",
        f"- **Duplicate Job IDs:** {qm.get('duplicate_job_ids', 0)}",
        f"- **Duplicate Job URLs:** {qm.get('duplicate_job_urls', 0)}",
        f"- **Invalid Date Formats:** {qm.get('invalid_dates', 0)}",
        f"- **Invalid Salary Ranges (min > max):** {qm.get('invalid_salary_ranges', 0)}",
        f"- **Invalid Experience Ranges (min > max):** {qm.get('invalid_experience_ranges', 0)}",
        f"- **Unmapped / Foreign Cities:** {qm.get('unmapped_cities', 0)} (predominantly remote or foreign roles)",
        f"- **Manual Review Flagged Records:** {qm.get('manual_review_count', 0)}",
        "",
        "---",
        "",
        "## 9. Legal Attribution Notice",
        "",
        "> *“Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps.”*",
    ])

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Saved data cleaning report to %s", report_path)


if __name__ == "__main__":
    logger.info("Starting HireTrends Data Cleaning & Normalization Pipeline...")
    meta = run_cleaning_pipeline()
    logger.info("Day 3 Data Cleaning Pipeline completed successfully!")
    logger.info(
        "Processed %d records -> %d cleaned output records.",
        meta["input_records"],
        meta["output_records"],
    )

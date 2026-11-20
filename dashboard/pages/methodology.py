"""HireTrends Dashboard — Methodology & Data Disclosures Page.

Documents pipeline lineage, data sources, ethical scraping charters,
licensing, and technical normalization methodologies.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st

from dashboard.components import render_attribution_footer, render_header

render_header("Data & Methodology", "Technical documentation, legal licensing, and data governance standards")

st.markdown(
    """
    ### 1. Data Sources & Provenance

    HireTrends integrates and clearly distinguishes two primary data sources:

    1. **Primary Dataset — Headcount Labs Jobs API (Current Baseline):**
       - **Collection Date:** November 20, 2026 (Snapshot Watermark: `2026-11-20T16:16:45.703Z`)
       - **Volume:** 4,491 total Pakistan job listings retrieved across 18 cursor-paginated pages.
       - **Deduplication:** SHA-256 and UUIDv4 integrity check (0 duplicates).
       - **Licensing:** Provided courtesy of [Headcount Labs](https://headcountlabs.com) under the **Open Database License (ODbL) 1.0**. Database contents are subject to the **Database Contents License (DbCL) 1.0**.

    2. **Historical Baseline — Open Data Pakistan (Dec 2019 – Mar 2021):**
       - **Scope:** Static historical employment records archived at `data/raw/pakistan-available-job-dec-19-mar-21.csv`.
       - **Usage:** Used strictly for comparative context and baseline validation. Kept 100% separate from live 2026 figures.

    ---

    ### 2. Data Cleaning & Normalization Engine (`src/cleaning/`)

    - **Occupational Title Normalization:**
      Standardizes noisy job titles (e.g. `Sr. Python Developer` → `Senior Python Developer`) while retaining original titles and extracting standardized seniority tiers (`Junior`, `Mid-Level`, `Senior`, `Lead`, `Executive`).

    - **Geographic Canonicalization:**
      Standardizes Pakistani cities against known canonical gazetteers (Karachi, Lahore, Islamabad, Rawalpindi, Peshawar, Faisalabad, Multan, etc.).
      *Rule:* Remote is treated strictly as a workplace arrangement, not a city. Foreign listings (e.g., Cairo, US, UAE) are partitioned separately.

    - **Experience Range Parser:**
      Extracts standardized minimum and maximum years using regular expression boundaries (e.g., `3-5 years` → min 3.0, max 5.0; `fresh graduate` → min 0.0). Missing requirements remain strictly `null`.

    - **Currency Normalization & SBP Exchange Benchmarks:**
      All disclosed salaries are converted into **Monthly PKR Equivalent** using official State Bank of Pakistan reference rates (November 20, 2026):
      - **USD:** 278.50 PKR
      - **EUR:** 295.00 PKR
      - **GBP:** 352.00 PKR
      - **AED:** 75.80 PKR
      *Interval Standard:* Annual salaries are divided by 12.0; hourly rates assume full-time engagement (176 working hours/month).

    ---

    ### 3. Technical Skill Extraction & Taxonomy Matching (`src/analysis/skills_analysis.py`)

    - Utilizes regular expression matching with strict word boundaries (`\\b`) against the taxonomy defined in `config/skills_dictionary.json` (69 distinct technical competencies).
    - Prevents false-positive substring collisions (e.g. distinguishing `Go` from "good", `C` from "customer", `R` from "recruiter").
    - Skill penetration percentages are calculated as the number of **unique job postings** containing the skill divided by the relevant sample size, rather than counting repeated raw keyword mentions.

    ---

    ### 4. Classification Consistency & Audit Reconciliation

    - **Confirmed Technology Jobs:** 1,075 postings (23.94%) matching high-confidence technical taxonomy rules.
    - **Manual Review / Ambiguous Roles:** 1,074 postings (23.91%) tagged with `needs_manual_review = True` (e.g. generic titles like "Associate", "Operations Lead").
    - **Non-Technology Jobs:** 2,342 postings (52.15%) representing medical, retail, driving, and hospitality roles.

    ---

    ### 5. Ethical Scraping & Data Governance Standards

    - **Zero PII Harvested:** No candidate resumes, applicant contact information, phone numbers, or private profiles are stored.
    - **No Redistribution of Raw Descriptions:** Full text employer job descriptions remain the intellectual property of their hiring entities and are excluded from public tables and Git repositories.
    - **Compliance:** Built in compliance with platform terms of service and `robots.txt` verification standards.

    ---

    ### 6. Legal Attribution & Copyright Notice

    > *“Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps.”*
    """
)

render_attribution_footer()

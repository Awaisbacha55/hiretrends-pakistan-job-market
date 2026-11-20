# HireTrends — Pakistan Tech Job Market Intelligence

An ethical, data-driven intelligence platform tracking technology job vacancies, compensation benchmarks, and skill demands across Pakistan's evolving software landscape.

[![Automated Tests](https://github.com/Awaisbacha55/hiretrends-pakistan-job-market/actions/workflows/tests.yml/badge.svg)](https://github.com/Awaisbacha55/hiretrends-pakistan-job-market/actions/workflows/tests.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Day 4 Complete](https://img.shields.io/badge/Development%20Status-Day%204%20Complete-brightgreen.svg)]()

---

## 1. Project Overview & Introduction

**HireTrends** is an applied data engineering and market intelligence project engineered to collect, clean, standardize, and analyze tech recruitment listings in Pakistan. By transforming noisy, unstructured job descriptions into structured tabular schemas and interactive analytics, HireTrends aims to empower students, software engineers, and engineering managers with empirical market data.

> [!NOTE]
> **Development Phase — Day 4 Complete:** Days 1, 2, 3, and 4 are fully completed and verified. The platform features an ethical ingestion engine, official Headcount Labs API bulk collector (4,491 Pakistan job records), a robust cleaning pipeline (`src/cleaning/`), an extensive exploratory data analysis engine (`src/analysis/`), 14 Plotly HTML & Matplotlib/Seaborn publication figures (`reports/figures/`), comprehensive market report ([`reports/market_analysis_report.md`](reports/market_analysis_report.md)), and a 109-test offline unit test suite. Days 5–6 will deliver production pipeline hardening and the interactive Streamlit dashboard.

---

## 2. Real-World Problem

In Pakistan's rapidly expanding tech ecosystem, job seekers and career switchers often lack reliable, centralized transparency into:
* **True compensation distributions:** Salaries are frequently omitted or expressed in conflicting hourly, monthly, or annual ranges.
* **Geographical talent hubs:** Understanding the volume split between Lahore, Karachi, Islamabad/Rawalpindi, and fully remote openings.
* **High-velocity skill requirements:** Discerning real-world industry demand for modern technologies (e.g., Python, React, Next.js, FastAPI, AWS, Docker) versus outdated curriculum standards.
* **Recruitment noise and ethical collection gaps:** Many ad-hoc web scrapers disrupt production job boards and harvest private candidate data without regard for terms of service or robots standards.

HireTrends solves these issues by establishing a principled, automated pipeline with strict compliance safeguards and statistical rigor.

---

## 3. Project Objectives

1. **Ethical & Compliant Ingestion:** Implement strict verification against platform Terms of Service and `robots.txt` before any collection occurs.
2. **Standardized Target Dataset:** Curate a target baseline of 2,000+ technology listings where legally authorized and available.
3. **Data Cleaning & Normalization:** Standardize disparate job titles, salary structures (normalized to Monthly PKR), and experience bands.
4. **Automated Skill Extraction:** Identify technical skills, frameworks, cloud tools, and databases via regular expressions and taxonomy mapping.
5. **Interactive Streamlit Dashboard:** Visualize hiring trends, salary quartiles, geographic density, and skill co-occurrence.

---

## 4. Technology Stack

* **Language:** Python 3.12+
* **HTTP & Web Parsing:** `requests`, `beautifulsoup4`, `lxml`, `tenacity`
* **Dynamic Rendering (Permitted Scenarios):** `playwright`
* **Data Processing & Analytics:** `pandas`, `numpy`
* **Visualization & Reporting:** `plotly`, `matplotlib`, `seaborn`, `wordcloud`
* **Interactive UI:** `streamlit`
* **Testing & Quality Assurance:** `pytest`
* **CI/CD & Version Control:** GitHub Actions, Git

---

## 5. Repository Structure

```text
hiretrends-pakistan-job-market/
│
├── data/
│   ├── raw/                  # Unprocessed raw ingestion records (JSONL/CSV)
│   ├── processed/            # Cleaned, standardized tabular datasets (jobs_cleaned.csv)
│   └── samples/              # Anonymized sample records for testing
│
├── notebooks/                # Exploratory data analysis (EDA) notebooks
│   └── README.md
│
├── src/
│   ├── __init__.py
│   ├── collection/           # Ingestion, source compliance, Headcount Labs API
│   │   ├── __init__.py
│   │   ├── check_sources.py  # CLI tool auditing robots.txt and permissions
│   │   ├── scraper.py        # Reusable ethical scraper foundation
│   │   ├── headcount_client.py # Headcount Labs authenticated client
│   │   ├── headcount_bulk_collector.py # Resilient cursor paginator
│   │   ├── map_headcount_record.py # State unwrapping & schema mapper
│   │   ├── classify_technology_jobs.py # Tech classification & audit flags
│   │   └── collect_jobs.py   # Collection pipeline orchestrator
│   │
│   ├── cleaning/             # Data cleaning, normalization, and NLP extraction
│   │   ├── __init__.py
│   │   ├── clean_jobs.py     # End-to-end cleaning pipeline orchestrator
│   │   ├── title_normalizer.py # Seniority and job title standardizer
│   │   ├── city_normalizer.py  # Pakistani city mapper & foreign filter
│   │   ├── workplace_normalizer.py # Remote, Hybrid, On-site classifier
│   │   ├── experience_parser.py # Regex min/max experience range parser
│   │   ├── salary_parser.py  # Currency conversion (SBP rates) to Monthly PKR
│   │   ├── skill_extractor.py # Regex taxonomy matcher with word boundaries
│   │   └── quality_checks.py # Quality audit (duplicates, ranges, coverage)
│   │
│   ├── analysis/             # Statistical analysis, salary benchmarking & EDA
│   │   ├── __init__.py
│   │   ├── skills_analysis.py # Top skills, domains, and role-wise analysis
│   │   ├── salary_analysis.py # Parametric/non-parametric salary metrics
│   │   ├── location_analysis.py # Top hiring cities & foreign segregation
│   │   ├── workplace_analysis.py # Remote, Hybrid, On-site distributions
│   │   ├── cooccurrence.py   # Pairwise co-occurrence matrix & Jaccard
│   │   └── generate_visualizations.py # Plotly HTML & Matplotlib PNG generator
│   │
│   └── utils/                # Logging, file handling, and helpers
│       └── __init__.py
│
├── dashboard/                # Streamlit dashboard implementation
│   └── README.md
│
├── config/
│   ├── sources.json          # Source registry and legal permission statuses
│   └── skills_dictionary.json# Structured tech skills taxonomy and aliases
│
├── reports/
│   ├── source_audit.md       # Detailed legal & technical source audit
│   ├── data_dictionary.md    # 19-attribute dataset schema definition
│   ├── headcount_api_sample_report.md # 10-record sample analysis report
│   ├── headcount_collection_report.md # Day 2 bulk collection audit
│   ├── data_cleaning_report.md # Day 3 cleaning, normalization & skills report
│   ├── market_analysis_report.md # Day 4 EDA & market intelligence findings
│   └── figures/              # Rendered Plotly HTML and PNG charts (14 files)
│
├── tests/
│   ├── __init__.py
│   ├── test_source_checker.py# Unit tests for robots.txt & permission logic
│   ├── test_scraper.py       # Unit tests for HTML card parsing & compliance
│   ├── test_headcount_api.py # Unit tests for API authentication & config
│   ├── test_headcount_sample.py # Unit tests for sample ingestion & fields
│   ├── test_bulk_collection.py  # Unit tests for cursor pagination & mapping
│   ├── test_cleaning_pipeline.py # Unit tests for title, city, pay, exp, skills
│   └── test_analysis_pipeline.py # Unit tests for skills, salary, location, co-occurrence
│
├── .github/
│   └── workflows/
│       └── tests.yml         # GitHub Actions continuous integration
│
├── .gitignore                # Production ignore rules (no secrets/venv/data)
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── LICENSE                   # Open source license
└── CONTRIBUTING.md           # Contribution and ethical coding standards
```

---

## 6. Ethical Scraping Policy

HireTrends operates under a strict **Ethical and Responsible Data Collection Charter**:

1. **Terms of Service Supremacy:** A permissive `robots.txt` does not override a platform's legal Terms of Service. If a platform prohibits scraping or commercial harvesting, automated collection is disallowed.
2. **Fail-Closed Safeguards:** If network conditions, HTTP 403 Forbidden responses, or missing configs prevent verification of a source's policy, the scraper halts immediately.
3. **No Technical Circumvention:** The system does not bypass CAPTCHAs, paywalls, IP throttles, or Cloudflare/WAF security boundaries.
4. **Zero Personally Identifiable Information (PII):** Candidate resumes, applicant contact numbers, personal email addresses, and recruiter profiles are never collected or stored.
5. **Polite Crawl Delays:** All requests are throttled (default 3.0s minimum, or following explicit `Crawl-delay` headers) to minimize server resource impact.
6. **Transparent User-Agent:** All HTTP headers identify the bot:
   `HireTrendsResearchBot/1.0 (+https://github.com/Awaisbacha55/hiretrends-pakistan-job-market; academic research)`

---

## 7. Data Sources & Source Audit Findings

The initial source audit documented in [`reports/source_audit.md`](reports/source_audit.md) evaluated three major channels:

| Source | Category | Status | Allowed Collection Method | Findings & Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Mustakbil** | Commercial Job Board | `PROHIBITED` | None | Terms of Service strictly forbid scraping, copying, reverse engineering, and machine learning training. |
| **Rozee.pk** | Commercial Job Board | `REQUIRES_PERMISSION` | Official API / Agreement | Automated requests to `robots.txt` trigger HTTP 403 Forbidden (Cloudflare WAF). Terms restrict automated harvesting. |
| **Open Data Pakistan** | Open Data Portal | `DATASET_ONLY` | Bulk Dataset Download | Static historical job market dataset under Open Data Commons ODbL. Direct file download permitted; dynamic HTML crawling restricted. |

---

## 8. Dataset Schema & Data Dictionary

All collected records conform to the standardized 19-attribute schema specified in [`reports/data_dictionary.md`](reports/data_dictionary.md):

| Field Name | Type | Key Rule |
| :--- | :--- | :--- |
| `job_id` | String | Deterministic SHA-256 hash derived from source, title, company, and URL. |
| `job_title` | String | Verbatim job title from posting. |
| `normalized_title` | String | Standardized occupational role. |
| `company` | String | Hiring organization name. |
| `city` / `normalized_city` | String | Geographic location standardized to major Pakistani tech centers. |
| `salary_text` | String | Original verbatim salary compensation text. |
| `salary_min_pkr` / `salary_max_pkr` | Float | Normalized Monthly PKR compensation. Missing values are `null` (never 0). |
| `experience_text` | String | Verbatim required experience phrase. |
| `experience_min_years` / `max_years` | Float | Standardized experience bounds in years. Missing values are `null`. |
| `employment_type` | String | `Full-time`, `Part-time`, `Contract`, `Internship`. |
| `workplace_type` | String | `Remote`, `Hybrid`, `On-site`. |
| `description` | Text | Cleaned textual description (HTML stripped). |
| `skills` | Array | Matched technical skills from `config/skills_dictionary.json`. |
| `posted_date` | Date | ISO 8601 publication date (`YYYY-MM-DD`). |
| `source` | String | Source platform identifier. |
| `job_url` | String | Canonical URL of posting. |
| `collected_at` | Timestamp | ISO 8601 UTC collection timestamp. |

---

## 9. Installation & Local Setup (Windows PowerShell)

### Prerequisites
* Windows 10/11 with PowerShell
* Python 3.12 (verified: Python 3.12.10)
* Git

### Step-by-Step Instructions

1. **Clone the Repository:**
   ```powershell
   git clone https://github.com/Awaisbacha55/hiretrends-pakistan-job-market.git
   cd hiretrends-pakistan-job-market
   ```

2. **Create Python Virtual Environment:**
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```powershell
   Copy-Item .env.example .env
   ```

---

## 10. Running the Source Compliance Checker

Audit any website's `robots.txt` policy and verify compliance from the command line:

```powershell
# Check whether a URL is permitted under robots.txt
python -m src.collection.check_sources --base-url https://example.com --target-url https://example.com/

# Output structured JSON results
python -m src.collection.check_sources --base-url https://example.com --target-url https://example.com/jobs/123 --json
```

---

## 11. Running Automated Tests

HireTrends includes a comprehensive unit test suite ensuring parsing correctness, URL validation, cursor pagination, data cleaning, statistical modeling, and fail-closed compliance logic. All tests run **100% offline** using mocked fixtures:

```powershell
pytest -v
```

Expected output:
```text
tests/test_analysis_pipeline.py ...........                              [ 10%]
tests/test_bulk_collection.py .....................                      [ 29%]
tests/test_cleaning_pipeline.py ...................................      [ 61%]
tests/test_headcount_api.py ..........                                   [ 70%]
tests/test_headcount_sample.py ........                                  [ 77%]
tests/test_scraper.py ...........                                        [ 88%]
tests/test_source_checker.py .............                               [100%]
============================= 109 passed in 2.50s ==============================
```

---

## 12. Current Progress & Development Roadmap

### Day 1: Project Foundation (Completed)
- [x] Cloned and initialized Git repository structure.
- [x] Configured Python 3.12 virtual environment and installed 15 required dependencies.
- [x] Conducted comprehensive ethical source audit ([`reports/source_audit.md`](reports/source_audit.md)).
- [x] Formalized 19-field dataset schema ([`reports/data_dictionary.md`](reports/data_dictionary.md)).
- [x] Designed structured technical skills taxonomy ([`config/skills_dictionary.json`](config/skills_dictionary.json)).
- [x] Built CLI source compliance and `robots.txt` checker (`src/collection/check_sources.py`).
- [x] Implemented ethical scraper foundation with fail-closed safeguards (`src/collection/scraper.py`).
- [x] Created collection entry point (`src/collection/collect_jobs.py`).
- [x] Authored 24 automated unit tests (`tests/`).
- [x] Configured GitHub Actions CI workflow (`.github/workflows/tests.yml`).

### Day 2: Headcount Labs API Bulk Ingestion (Completed)
- [x] Integrated authenticated Headcount Labs Jobs API client (`src/collection/headcount_client.py`).
- [x] Implemented cursor-based pagination with snapshot watermark locking (`src/collection/headcount_bulk_collector.py`).
- [x] Collected 4,491 live Pakistan job records to `data/raw/headcount/jobs_raw.jsonl` (zero duplicates).
- [x] Unwrapped state envelopes preserving missing fields as strictly `null` (`src/collection/map_headcount_record.py`).
- [x] Classified technology postings and generated Day 2 audit report ([`reports/headcount_collection_report.md`](reports/headcount_collection_report.md)).
- [x] Expanded test suite to 63 automated unit tests.

### Day 3: Data Cleaning, Normalization & Skill Extraction (Completed)
- [x] Built reproducible end-to-end cleaning pipeline (`src/cleaning/clean_jobs.py`).
- [x] Implemented job title & seniority standardization (`src/cleaning/title_normalizer.py`).
- [x] Implemented Pakistani city canonicalizer and foreign location filter (`src/cleaning/city_normalizer.py`).
- [x] Implemented workplace arrangement classifier: Remote, Hybrid, On-site (`src/cleaning/workplace_normalizer.py`).
- [x] Built regex experience range parser with fresh-grad handling (`src/cleaning/experience_parser.py`).
- [x] Built salary normalizer to Monthly PKR using official State Bank of Pakistan rates (`src/cleaning/salary_parser.py`).
- [x] Implemented taxonomy-based regex skill extractor with boundary matching (`src/cleaning/skill_extractor.py`).
- [x] Added classification confidence scoring & manual review tagging (`src/collection/classify_technology_jobs.py`).
- [x] Built comprehensive data quality assurance audit (`src/cleaning/quality_checks.py`).
- [x] Cleaned 4,491 records into 33-column tabular dataset (`data/processed/jobs_cleaned.csv`).
- [x] Authored comprehensive Day 3 report ([`reports/data_cleaning_report.md`](reports/data_cleaning_report.md)).
- [x] Expanded automated test suite to 98 passing unit tests (`tests/test_cleaning_pipeline.py`).

### Day 4: Exploratory Data Analysis & Market Intelligence (Completed)
- [x] Reconciled Day 2 vs Day 3 classification divergence (1,075 verified tech vs 1,074 manual-review roles).
- [x] Built top skills and taxonomy clustering engine (`src/analysis/skills_analysis.py`).
- [x] Analyzed skills across 12 specific tech occupations with exact sample sizes.
- [x] Implemented compensation benchmarking separating USD and native PKR (`src/analysis/salary_analysis.py`).
- [x] Evaluated regional hub density across Pakistani cities and foreign origins (`src/analysis/location_analysis.py`).
- [x] Analyzed workplace arrangements using known denominators (`src/analysis/workplace_analysis.py`).
- [x] Computed pairwise technical skill co-occurrence matrix and Jaccard metrics (`src/analysis/cooccurrence.py`).
- [x] Generated 14 interactive Plotly HTML and publication PNG figures (`src/analysis/generate_visualizations.py`).
- [x] Published comprehensive Day 4 intelligence report ([`reports/market_analysis_report.md`](reports/market_analysis_report.md)).
- [x] Expanded automated test suite to 109 passing unit tests (`tests/test_analysis_pipeline.py`).

### Upcoming Milestones (Days 5–6)
* **Day 5: Production Ingestion & Pipeline Hardening:** Large-scale dataset ingestion with fault tolerance, sqlite/parquet serialization, and pipeline automation.
* **Day 6: Streamlit Interactive Dashboard:** Multi-page web application deployment with Plotly interactive charts and filters.

---

## 13. Limitations & Responsible Use

* **Historical Data vs. Live Scraping:** Because major Pakistani commercial boards restrict unauthorized automated harvesting, live data ingestion requires official APIs or authorized datasets. Historical open datasets may not reflect real-time 2026 shifts.
* **Salary Disclosures:** Less than 4% of tech postings advertise explicit salary numbers. Statistical analyses on compensation report sample sizes and confidence boundaries to avoid sample bias.
* **Academic & Non-Commercial Purpose:** This project is intended solely for educational, research, and non-commercial market intelligence.

---

## 14. License & Attribution

- **Code:** Distributed under the [MIT License](LICENSE).
- **Headcount Labs Database:** Data courtesy of [Headcount Labs](https://headcountlabs.com), provided under the Open Database License (ODbL) 1.0. Database contents are subject to Database Contents License (DbCL) 1.0.
- **Employer Rights:** Individual job descriptions remain the copyright of their respective hiring organizations.
- **Geographic Data:** Location entities © OpenStreetMap contributors and Overture Maps.

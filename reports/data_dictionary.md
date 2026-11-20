# HireTrends: Job Market Dataset Schema & Data Dictionary

**Project:** HireTrends — Pakistan Tech Job Market Intelligence  
**Document:** Dataset Schema Specification and Field Definitions  
**Version:** 1.0.0  
**Effective Date:** 2026-11-20  

---

## 1. Schema Overview

The HireTrends dataset schema is engineered to convert semi-structured, noisy recruitment postings into standardized, analytical-ready records. The schema balances raw text preservation (for auditability and re-parsing) with clean normalized numeric/categorical attributes (for statistical and machine learning applications).

---

## 2. Field Specifications

| Column Name | Data Type | Nullable | Description & Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | `VARCHAR(64)` | No | SHA-256 hash or natural identifier combining source and listing ID. Primary Key. | `"mb_849201"` / `"hash_e3b0c442"` |
| `job_title` | `VARCHAR(255)` | No | Raw job title as extracted directly from the listing. | `"Senior Full Stack Developer (React / Python)"` |
| `normalized_title` | `VARCHAR(100)` | Yes | Standardized occupational title mapped to industry taxonomy. | `"Full Stack Developer"` |
| `company` | `VARCHAR(255)` | Yes | Name of the hiring entity or recruitment agency. Null if confidential. | `"Systems Limited"` |
| `city` | `VARCHAR(100)` | Yes | Raw city or geographical location string from the listing. | `"Lahore, Pakistan"` |
| `normalized_city` | `VARCHAR(50)` | Yes | Standardized Pakistani tier-1/tier-2 tech hub or remote marker. | `"Lahore"` |
| `salary_text` | `VARCHAR(100)` | Yes | Verbatim salary string as advertised. | `"PKR 150,000 - 250,000 per month"` |
| `salary_min_pkr` | `FLOAT` | Yes | Minimum normalized monthly compensation in Pakistani Rupees (PKR). | `150000.0` |
| `salary_max_pkr` | `FLOAT` | Yes | Maximum normalized monthly compensation in Pakistani Rupees (PKR). | `250000.0` |
| `experience_text` | `VARCHAR(100)` | Yes | Verbatim required experience phrase. | `"3 to 5 years of relevant experience"` |
| `experience_min_years`| `FLOAT` | Yes | Parsed minimum required experience in completed years. | `3.0` |
| `experience_max_years`| `FLOAT` | Yes | Parsed maximum required experience in completed years. | `5.0` |
| `employment_type` | `VARCHAR(50)` | Yes | Classification: `Full-time`, `Part-time`, `Contract`, `Internship`, `Freelance`. | `"Full-time"` |
| `workplace_type` | `VARCHAR(50)` | Yes | Classification: `Remote`, `Hybrid`, `On-site`. | `"Hybrid"` |
| `description` | `TEXT` | Yes | Full cleaned job description text stripped of HTML tags and navigation boilerplate. | `"We are seeking an experienced developer..."` |
| `skills` | `JSON / ARRAY` | Yes | Array of matched technical skills derived from skills dictionary. | `["Python", "React", "PostgreSQL", "Docker"]` |
| `posted_date` | `DATE` | Yes | Posting publication date in ISO 8601 (`YYYY-MM-DD`). | `"2026-11-15"` |
| `source` | `VARCHAR(50)` | No | Source platform identifier matching `config/sources.json`. | `"opendata_pakistan"` |
| `job_url` | `VARCHAR(500)` | Yes | Canonical source listing URL for audit and deduplication. | `"https://example.com/jobs/849201"` |
| `collected_at` | `TIMESTAMP` | No | UTC timestamp when record was ingested (`YYYY-MM-DDTHH:MM:SSZ`). | `"2026-11-20T12:00:00Z"` |

---

## 3. Data Ingestion & Transformation Rules

### 3.1 Numeric Null Handling
* **Critical Rule:** Missing numeric values (`salary_min_pkr`, `salary_max_pkr`, `experience_min_years`, `experience_max_years`) **MUST be stored as NULL (`NaN` in pandas)**, never as `0`.
* A salary of `0` falsely indicates unpaid or volunteer labor, which corrupts wage distributions and average metrics.

### 3.2 Salary Normalization Protocol
* **Standard Unit:** All salary figures are normalized to **Monthly PKR**.
* **Annual Conversions:** If a compensation figure is specified annually (e.g., `"2.4M PKR per annum"`), it is divided by `12.0` to calculate monthly equivalents.
* **Hourly / Daily Conversions:** Standard labor assumptions (8 hours/day, 22 working days/month = 176 monthly hours) apply only if explicit in text, and must be flagged in transformation logs.
* **Foreign Currencies (USD / EUR / GBP):** When remote postings quote foreign currency, the raw currency code is retained in parsing metadata; conversion to PKR utilizes fixed date-stamped reference rates.

### 3.3 Experience Extraction Protocol
* If an advertisement specifies `"Minimum 4 years"`, `experience_min_years = 4.0` and `experience_max_years = NULL`.
* If specified as `"Fresh graduate"`, `experience_min_years = 0.0` and `experience_max_years = 1.0`.

### 3.4 Date & Timezone Conventions
* All ingestion timestamps (`collected_at`) are captured in standard **UTC (Coordinated Universal Time)** with ISO 8601 formatting.
* Posting dates (`posted_date`) reflect Pakistan Standard Time (PKT, UTC+5) as published on local job portals.

### 3.5 Privacy & PII Protection
* Under no circumstances may recruitment applicant names, personal phone numbers, applicant resumes, personal email addresses, or hiring manager personal profiles be stored.

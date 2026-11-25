# Data Dictionary

## Processed Dataset Scopes

The cleaning pipeline (`src/cleaning/clean_jobs.py`) produces four CSV files in `data/processed/` sharing the same 35-column schema:

| File | Row Count | Scope Definition |
| :--- | ---: | :--- |
| `jobs_cleaned.csv` | `3,707` | All deduplicated records (`4,491` raw minus `784` URL duplicates), all countries, all domains, all dates. |
| `jobs_pakistan.csv` | `3,362` | Deduplicated records with `country_classification == "Pakistan"` (`345` Foreign, `0` Unknown excluded), all domains, all dates. |
| `jobs_pakistan_tech.csv` | `848` | Confirmed Pakistan Tech records (`country_classification == "Pakistan"` and `technology_category == "Tech"`), all dates. |
| `jobs_pakistan_tech_recent.csv` | `685` | **Primary analysis scope:** Confirmed Pakistan Tech records within the 12-month window `2025-11-20` through `2026-11-20` (`is_recent_12m == True`; `163` older postings excluded). |

---

## Schema Reference (35 Columns)

### 1. Identifiers & Role Metadata
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `job_id` | `str` | No | Unique job identifier assigned from source record or deterministic hash. |
| `job_title` | `str` | No | Raw job title as collected from the source listing. |
| `normalized_title` | `str` | No | Standardized role bucket (e.g., `Software Engineer`, `Full Stack Developer`, `AI Engineer`, `Other`). |
| `seniority_level` | `str` | No | Inferred seniority tier (`Intern`, `Junior`, `Mid`, `Senior`, `Lead/Principal`, `Unspecified`). |
| `company` | `str` | Yes | Hiring organization name; `"Unknown"` or empty if omitted by the listing. |

### 2. Geography & Workplace
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `city` | `str` | Yes | Raw city string from the source listing. |
| `normalized_city` | `str` | Yes | Standardized city name (e.g., `Lahore`, `Islamabad`, `Karachi`); `"Unknown"` when unmapped or missing. |
| `region` | `str` | Yes | Province or administrative region mapped from `normalized_city`. |
| `country` | `str` | Yes | Raw or normalized country label associated with the posting. |
| `is_pakistan_location` | `bool` | No | `True` when location signals confirm Pakistan; `False` otherwise. |
| `country_classification` | `str` | No | Three-way location classification: `"Pakistan"`, `"Foreign"`, or `"Unknown"`. |
| `workplace_type` | `str` | Yes | Work arrangement (`"On-site"`, `"Remote"`, `"Hybrid"`, or null/empty when unstated). |

### 3. Experience
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `experience_text` | `str` | Yes | Raw experience requirement snippet extracted from the posting. |
| `experience_min_years` | `float64` | Yes | Parsed minimum years of experience (`NaN` when not stated). |
| `experience_max_years` | `float64` | Yes | Parsed maximum years of experience (`NaN` when not stated or single-bound). |

### 4. Compensation & Currency Normalization
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `salary_text` | `str` | Yes | Raw salary string from the listing (`NaN` when undisclosed). |
| `salary_currency` | `str` | Yes | Detected currency code (`"PKR"`, `"USD"`, etc.; `NaN` when undisclosed). |
| `salary_interval` | `str` | Yes | Detected pay period (`"monthly"`, `"yearly"`, `"hourly"`, etc.; `NaN` when undisclosed). |
| `salary_min_original` | `float64` | Yes | Parsed minimum salary in original currency and interval (`NaN` when undisclosed). |
| `salary_max_original` | `float64` | Yes | Parsed maximum salary in original currency and interval (`NaN` when undisclosed). |
| `salary_min_pkr` | `float64` | Yes | Minimum salary normalized to **monthly PKR** (`NaN` when undisclosed or unconvertible). |
| `salary_max_pkr` | `float64` | Yes | Maximum salary normalized to **monthly PKR** (`NaN` when undisclosed or unconvertible). |
| `salary_is_converted` | `bool` | No | `True` if currency or pay interval conversion was applied to derive PKR monthly values. |

**Normalization Rules:**
- **Exchange Rate:** `1 USD = 276.5132 PKR` (reference snapshot date `2026-11-20`).
- **Hourly-to-Monthly Factor:** `176 hours/month` (`22` working days × `8` hours/day).
- **Yearly-to-Monthly Factor:** Divided by `12`.
- **Null Handling:** Undisclosed salaries remain `NaN` (never imputed with `0`).

### 5. Skills
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `skills` | `str` | No | JSON-encoded array string of canonicalized technical skills extracted from the posting (e.g., `'["Python", "SQL", "AWS"]'`). |
| `skills_count` | `int64` | No | Count of extracted canonical skills in `skills` (`0` when none matched). |

> **Note on Job Descriptions:** Full job descriptions are present in the raw Headcount Labs API records and are used internally by `src/cleaning/clean_jobs.py` (alongside `job_title`) for skill extraction, experience parsing, and technology classification. Full description text is intentionally omitted from processed/public CSV outputs and Git to respect employer copyright.

### 6. Technology Domain Classification
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `is_technology_job` | `bool` | No | `True` only when classified as `"Tech"`; `False` for `"Non-Technology"` and `"Uncertain"`. |
| `technology_category` | `str` | No | Three-way domain classification: `"Tech"`, `"Non-Technology"`, or `"Uncertain"`. |
| `classification_confidence` | `float64` | No | Heuristic confidence score in `[0.0, 1.0]` for the domain classification. |
| `classification_reason` | `str` | No | Human-readable explanation of the rule/keyword match that produced `technology_category`. |
| `needs_manual_review` | `bool` | No | `True` for borderline or `"Uncertain"` classifications flagged for review. |

### 7. Dates & Provenance
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `posted_date` | `str` | Yes | ISO date (`YYYY-MM-DD`) when the job was posted. |
| `is_recent_12m` | `bool` | No | `True` when `posted_date` falls within `2025-11-20` through `2026-11-20` (inclusive); `False` otherwise. |
| `source` | `str` | No | Source identifier (e.g., `"headcount_labs_api"`). |
| `job_url` | `str` | No | Canonical URL of the job posting (used as the deduplication key). |
| `collected_at` | `str` | No | UTC ISO-8601 timestamp recording when the raw record was fetched. |

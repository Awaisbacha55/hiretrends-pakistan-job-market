# HireTrends — Day 3 Data Cleaning, Normalization & Skill Extraction Report

**Pipeline Execution Timestamp:** 2026-11-25T19:03:18.640041+00:00  
**Input Source Dataset:** `data/raw/headcount/jobs_raw.jsonl`  
**Processed Outputs:** `jobs_cleaned.csv` (All Deduplicated) | `jobs_pakistan.csv` (Pakistan-Only) | `jobs_pakistan_tech.csv` (Confirmed Pakistan Tech)  
**Attribution & License:** Open Database License (ODbL 1.0 & DbCL 1.0 (Headcount Labs)  

---

## 1. Pipeline Execution & Scope Funnel Summary

| Stage / Metric | Count | % of Raw Input | Notes |
| :--- | :--- | :--- | :--- |
| **1. Raw Input Records** | **4,491** | 100.0% | Ingested from Headcount Labs Pakistan feed |
| **Duplicates Removed (URL)** | **784** | 17.5% | Normalized `job_url` primary deduplication |
| **Duplicates Removed (Fallback)** | **0** | 0.0% | Normalized `(title, company, city, posted_date)` for URL-less records |
| **2. Deduplicated Output (`jobs_cleaned.csv`)** | **3,707** | 82.5% | Unique job postings (all countries & roles) |
| **3. Confirmed Pakistan (`jobs_pakistan.csv`)** | **3,362** | 74.9% | Foreign: 345 | Unknown: 0 |
| **4. Confirmed Pakistan Tech (`jobs_pakistan_tech.csv`)** | **848** | 18.9% | All dates (`2019-10-02` to `2026-11-19`) |
| **5. Recent 12M Pakistan Tech (`jobs_pakistan_tech_recent.csv`)** | **685** | 15.3% | Primary 2025/26 window (`2025-11-20` to `2026-11-20`; 163 stale excluded) |
| **Technology Roles (All Countries)** | **921 Tech** | 24.8% of Deduplicated | Segmented via high-confidence taxonomy |
| **Non-Technology Roles (All Countries)** | **1,950 Non-Tech** | 52.6% of Deduplicated | Operations, sales, medical, customer service |
| **Manual Review Flagged (All Countries)** | **836** | 22.55% of Deduplicated | Ambiguous titles flagged transparently |

---

## 2. Salary & Compensation Extraction Analysis

| Metric | Total Value | Percentage | Observation |
| :--- | :--- | :--- | :--- |
| **Disclosed Salaries Parsed** | **152** | **4.10%** | Explicit compensation ranges |
| **Missing / Undisclosed Salaries** | **3,555** | **95.90%** | Preserved as null (`NaN`), never 0 |
| **Currency Conversion Standard** | Monthly PKR | - | SBP Mark-to-Market / Ready Reference, 20 Nov 2026 (USD = 276.5132 PKR) |
| **Annual & Hourly Normalization** | Applied | - | Annual ÷ 12.0; Hourly × 176.0 (8 hrs/day × 22 days/mo, analytical estimate) |

---

## 3. Experience Requirements Analysis

| Metric | Total Value | Percentage | Observation |
| :--- | :--- | :--- | :--- |
| **Parsed Experience Requirements** | **2,502** | **67.5%** | Extracted min/max years from text |
| **Missing Experience Requirements** | **1,205** | **32.5%** | Preserved as null, not guessed |

---

## 4. Technical Skill Extraction & Top 20 Demanded Skills

- **Total Skill Mentions Extracted:** 7,297
- **Unique Skills Identified:** 69
- **Listings with Technical Skills:** 1,758 (47.42%)

### Top 20 Most Demanded Skills in Pakistan Tech Jobs:

| Rank | Technical Skill | Category | Mentions Count | % of All Postings |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Excel** | Technical Taxonomy | 507 | 13.7% |
| 2 | **SQL** | Technical Taxonomy | 406 | 11.0% |
| 3 | **Python** | Technical Taxonomy | 381 | 10.3% |
| 4 | **Microsoft Azure** | Technical Taxonomy | 349 | 9.4% |
| 5 | **AWS** | Technical Taxonomy | 333 | 9.0% |
| 6 | **CI/CD** | Technical Taxonomy | 332 | 9.0% |
| 7 | **Git** | Technical Taxonomy | 318 | 8.6% |
| 8 | **JavaScript** | Technical Taxonomy | 301 | 8.1% |
| 9 | **Large Language Models** | Technical Taxonomy | 211 | 5.7% |
| 10 | **Machine Learning** | Technical Taxonomy | 201 | 5.4% |
| 11 | **Google Cloud Platform** | Technical Taxonomy | 187 | 5.0% |
| 12 | **React** | Technical Taxonomy | 186 | 5.0% |
| 13 | **Apache Spark** | Technical Taxonomy | 181 | 4.9% |
| 14 | **Docker** | Technical Taxonomy | 177 | 4.8% |
| 15 | **Java** | Technical Taxonomy | 164 | 4.4% |
| 16 | **CSS** | Technical Taxonomy | 161 | 4.3% |
| 17 | **HTML** | Technical Taxonomy | 160 | 4.3% |
| 18 | **PostgreSQL** | Technical Taxonomy | 159 | 4.3% |
| 19 | **TypeScript** | Technical Taxonomy | 148 | 4.0% |
| 20 | **Kubernetes** | Technical Taxonomy | 145 | 3.9% |

---

## 5. Geographic Normalization & City Distribution

Pakistani cities were normalized to standard canonical spellings. Foreign cities (e.g. Cairo, Turkey) were partitioned as foreign non-PK locations. Remote is tracked as a workplace arrangement.

| Standardized Pakistani City | Province / Region | Listings Count | % of Mapped Cities |
| :--- | :--- | :--- | :--- |
| **Lahore** | Pakistan | 957 | 39.7% |
| **Karachi** | Pakistan | 753 | 31.3% |
| **Islamabad** | Pakistan | 528 | 21.9% |
| **Rawalpindi** | Pakistan | 37 | 1.5% |
| **Peshawar** | Pakistan | 25 | 1.0% |
| **Multan** | Pakistan | 24 | 1.0% |
| **Faisalabad** | Pakistan | 20 | 0.8% |
| **Sukkur** | Pakistan | 13 | 0.5% |
| **Hyderabad** | Pakistan | 11 | 0.5% |
| **Larkana** | Pakistan | 9 | 0.4% |
| **Sialkot** | Pakistan | 9 | 0.4% |
| **Quetta** | Pakistan | 4 | 0.2% |

---

## 6. Workplace Arrangement Distribution

| Workplace Type | Count | % of Known Arrangements | Notes |
| :--- | :--- | :--- | :--- |
| **On-site** | 865 | 46.6% | Standardized |
| **Remote** | 860 | 46.3% | Standardized |
| **Hybrid** | 131 | 7.1% | Standardized |

---

## 7. Seniority Level Distribution

| Seniority Level | Listings Count | % of Total Postings |
| :--- | :--- | :--- |
| **Mid-Level** | 2,291 | 61.8% |
| **Lead / Principal** | 536 | 14.5% |
| **Senior** | 478 | 12.9% |
| **Junior / Entry-Level** | 303 | 8.2% |
| **Executive / Director** | 99 | 2.7% |

---

## 8. Data Quality Assurance Audit

- **Duplicate Job IDs:** 0
- **Duplicate Job URLs:** 0
- **Invalid Date Formats:** 0
- **Invalid Salary Ranges (min > max):** 0
- **Invalid Experience Ranges (min > max):** 0
- **Unmapped / Foreign Cities:** 1298 (predominantly remote or foreign roles)
- **Manual Review Flagged Records:** 836

---

## 9. Legal Attribution Notice

> *“Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps.”*
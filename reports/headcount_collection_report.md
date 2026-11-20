# HireTrends — Headcount Labs Pakistan Job Market Collection Report

**Extraction Timestamp:** 2026-11-20 16:17:33 UTC  
**Source Platform:** Headcount Labs Jobs API (`https://api.headcountlabs.com`)  
**Snapshot Watermark:** `2026-11-20T16:16:45.703Z`  
**License Standard:** Open Database License (ODbL) 1.0 & DbCL 1.0  

---

## 1. Executive Ingestion Overview

| Metric | Total Value | Percentage of Dataset | Notes |
| :--- | :--- | :--- | :--- |
| **Total Records Retrieved** | **4,491** | 100.0% | Across 18 paginated pages |
| **Unique Job Listings** | **4,491** | 100.00% | Deduplicated by UUIDv4 |
| **Duplicate Job IDs** | **0** | 0.00% | Filtered out during ingestion |
| **Technology Jobs** | **1,075** | **23.9%** | Core analytical cohort |
| **Non-Technology Jobs** | **3,416** | 76.1% | Operations, sales, logistics |
| **Uncertain / Review** | **0** | 0.0% | Insufficient text for auto-tag |

---

## 2. Data Completeness & Missing Value Analysis

Missing attributes are strictly preserved as `null` rather than artificial defaults or zeroes.

| Attribute | Present Count | Missing Count | Completeness Rate | Quality Impact & Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Job Title** | 4,491 | 0 | 100.0% | Essential primary identifier |
| **Employer / Company** | 4,454 | 37 | 99.2% | High confidence hiring entity tracking |
| **Job Description** | 4,340 | 151 | 96.6% | Rich input for Day 3 skill extraction |
| **Location (City)** | 3,003 | 1,488 | 66.9% | Unspecified roles predominantly remote |
| **Work Arrangement** | 2,234 | 2,257 | 49.7% | Explicit remote vs. on-site tags |
| **Salary / Compensation** | 177 | 4,314 | 3.9% | Reflects widespread employer opacity |

---

## 3. Technology Role Segmentation (16 Taxonomy Classes)

| Taxonomy Category | Total Count | % of All Jobs | % of Tech Jobs | Sample Roles |
| :--- | :--- | :--- | :--- | :--- |
| **Other Technology** | 317 | 7.1% | 29.5% | Classified via title/stack rules |
| **Software Engineering** | 146 | 3.3% | 13.6% | Classified via title/stack rules |
| **Frontend Development** | 95 | 2.1% | 8.8% | Classified via title/stack rules |
| **QA / Software Testing** | 94 | 2.1% | 8.7% | Classified via title/stack rules |
| **Full Stack Development** | 93 | 2.1% | 8.7% | Classified via title/stack rules |
| **Data Analytics** | 79 | 1.8% | 7.3% | Classified via title/stack rules |
| **Artificial Intelligence / Machine Learning** | 64 | 1.4% | 6.0% | Classified via title/stack rules |
| **Backend Development** | 46 | 1.0% | 4.3% | Classified via title/stack rules |
| **DevOps / SRE** | 46 | 1.0% | 4.3% | Classified via title/stack rules |
| **Cybersecurity** | 41 | 0.9% | 3.8% | Classified via title/stack rules |
| **Data Science** | 18 | 0.4% | 1.7% | Classified via title/stack rules |
| **Networking** | 17 | 0.4% | 1.6% | Classified via title/stack rules |
| **Database Engineering** | 11 | 0.2% | 1.0% | Classified via title/stack rules |
| **Cloud Engineering** | 8 | 0.2% | 0.7% | Classified via title/stack rules |
| **Non-Technology** | 3,416 | 76.1% | - | Operations, sales, marketing |
| **Uncertain / Review** | 0 | 0.0% | - | Short titles / ambiguous text |

---

## 4. Geographic & Workplace Distribution

### 4.1 Top Locations for Tech Jobs
| Location / Hub | Tech Job Count | % of Tech Jobs |
| :--- | :--- | :--- |
| Lahore | 313 | 29.1% |
| Remote | 248 | 23.1% |
| Karachi | 190 | 17.7% |
| Islamabad | 180 | 16.7% |
| Unspecified | 51 | 4.7% |
| Peshawar | 13 | 1.2% |
| Rawalpindi | 11 | 1.0% |
| Cairo | 9 | 0.8% |
| Turkey | 7 | 0.7% |
| KARACHI | 5 | 0.5% |

### 4.2 Work Arrangement Breakdown (Technology Roles)
| Arrangement | Count | % of Tech Jobs |
| :--- | :--- | :--- |
| Remote | 325 | 30.2% |
| In_person | 257 | 23.9% |
| Hybrid | 43 | 4.0% |

---

## 5. Employer Landscape (Top Hiring Tech Employers)

| Employer | Tech Listings | Key Tech Focus Areas |
| :--- | :--- | :--- |
| **Creative Chaos** | 159 | Active Tech Hiring |
| **Pavago** | 66 | Active Tech Hiring |
| **NorthBay Solutions** | 47 | Active Tech Hiring |
| **Abacus Consulting** | 45 | Active Tech Hiring |
| **Contour** | 33 | Active Tech Hiring |
| **Devsinc** | 31 | Active Tech Hiring |
| **Huzzle** | 27 | Active Tech Hiring |
| **Kombo** | 27 | Active Tech Hiring |
| **Mashreq** | 19 | Active Tech Hiring |
| **ITC WORLDWIDE** | 18 | Active Tech Hiring |

---

## 6. Date Range & Ingestion Watermark

- **Earliest Posting / Discovery Date:** `2019-10-02`
- **Latest Posting / Discovery Date:** `2026-11-20`
- **Snapshot Watermark:** `2026-11-20T16:16:45.703Z`

---

## 7. Licensing & Mandatory Attribution Notice

> *“Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps.”*

### Redistribution Safeguards:
1. **Raw JSONL Data Exclusion:** `data/raw/headcount/jobs_raw.jsonl` contains copyrighted employer descriptions and is strictly excluded from version control via `.gitignore`.
2. **Public Deliverables:** Only aggregated statistical distributions, taxonomies, and anonymized research findings are published to GitHub.
3. **Derivative Open Data Standards:** All derived analytical tables comply with ODbL 1.0 share-alike provisions.
# HireTrends — Day 3 Data Cleaning, Normalization & Skill Extraction Report

**Pipeline Execution Timestamp:** 2026-11-20T16:32:42.882385+00:00  
**Input Source Dataset:** `data/raw/headcount/jobs_raw.jsonl`  
**Processed Tabular Output:** `data/processed/jobs_cleaned.csv`  
**Attribution & License:** Open Database License (ODbL) 1.0 & DbCL 1.0 (Headcount Labs)  

---

## 1. Pipeline Execution Summary

| Metric | Count | % of Dataset | Notes |
| :--- | :--- | :--- | :--- |
| **Raw Input Records** | **4,491** | 100.0% | Ingested from Headcount Labs Pakistan feed |
| **Cleaned Output Records** | **4,491** | 100.0% | Standardized internal tabular schema |
| **Duplicates Removed** | **0** | 0.0% | Zero duplicates in input feed |
| **Technology Roles** | **1,075 Tech** | 23.9% Tech | Segmented via high-confidence taxonomy |
| **Non-Technology Roles** | **2,342 Non-Tech** | 52.1% Non-Tech | Operations, sales, medical, customer service |
| **Manual Review Flagged** | **1,074** | 23.91% | Ambiguous titles flagged transparently |

---

## 2. Salary & Compensation Extraction Analysis

| Metric | Total Value | Percentage | Observation |
| :--- | :--- | :--- | :--- |
| **Disclosed Salaries Parsed** | **174** | **3.87%** | Explicit compensation ranges |
| **Missing / Undisclosed Salaries** | **4,317** | **96.13%** | Preserved as null (`NaN`), never 0 |
| **Currency Conversion Standard** | Monthly PKR | - | Official State Bank of Pakistan rates (USD 278.50) |
| **Annual to Monthly Normalization** | Applied | - | Divided annual wages by 12.0 |

---

## 3. Experience Requirements Analysis

| Metric | Total Value | Percentage | Observation |
| :--- | :--- | :--- | :--- |
| **Parsed Experience Requirements** | **3,014** | **67.1%** | Extracted min/max years from text |
| **Missing Experience Requirements** | **1,477** | **32.9%** | Preserved as null, not guessed |

---

## 4. Technical Skill Extraction & Top 20 Demanded Skills

- **Total Skill Mentions Extracted:** 8,622
- **Unique Skills Identified:** 69
- **Listings with Technical Skills:** 2,106 (46.89%)

### Top 20 Most Demanded Skills in Pakistan Tech Jobs:

| Rank | Technical Skill | Category | Mentions Count | % of All Postings |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Excel** | Technical Taxonomy | 616 | 13.7% |
| 2 | **SQL** | Technical Taxonomy | 473 | 10.5% |
| 3 | **Python** | Technical Taxonomy | 444 | 9.9% |
| 4 | **Microsoft Azure** | Technical Taxonomy | 391 | 8.7% |
| 5 | **Git** | Technical Taxonomy | 389 | 8.7% |
| 6 | **AWS** | Technical Taxonomy | 383 | 8.5% |
| 7 | **CI/CD** | Technical Taxonomy | 376 | 8.4% |
| 8 | **JavaScript** | Technical Taxonomy | 355 | 7.9% |
| 9 | **Apache Spark** | Technical Taxonomy | 278 | 6.2% |
| 10 | **Large Language Models** | Technical Taxonomy | 243 | 5.4% |
| 11 | **Machine Learning** | Technical Taxonomy | 225 | 5.0% |
| 12 | **React** | Technical Taxonomy | 215 | 4.8% |
| 13 | **Google Cloud Platform** | Technical Taxonomy | 211 | 4.7% |
| 14 | **Docker** | Technical Taxonomy | 201 | 4.5% |
| 15 | **Java** | Technical Taxonomy | 194 | 4.3% |
| 16 | **CSS** | Technical Taxonomy | 193 | 4.3% |
| 17 | **HTML** | Technical Taxonomy | 193 | 4.3% |
| 18 | **PostgreSQL** | Technical Taxonomy | 190 | 4.2% |
| 19 | **Power BI** | Technical Taxonomy | 169 | 3.8% |
| 20 | **TypeScript** | Technical Taxonomy | 167 | 3.7% |

---

## 5. Geographic Normalization & City Distribution

Pakistani cities were normalized to standard canonical spellings. Foreign cities (e.g. Cairo, Turkey) were partitioned as foreign non-PK locations. Remote is tracked as a workplace arrangement.

| Standardized Pakistani City | Province / Region | Listings Count | % of Mapped Cities |
| :--- | :--- | :--- | :--- |
| **Lahore** | Pakistan | 1,027 | 38.3% |
| **Karachi** | Pakistan | 868 | 32.3% |
| **Islamabad** | Pakistan | 609 | 22.7% |
| **Rawalpindi** | Pakistan | 38 | 1.4% |
| **Peshawar** | Pakistan | 26 | 1.0% |
| **Multan** | Pakistan | 24 | 0.9% |
| **Faisalabad** | Pakistan | 20 | 0.7% |
| **Sukkur** | Pakistan | 13 | 0.5% |
| **Hyderabad** | Pakistan | 13 | 0.5% |
| **Larkana** | Pakistan | 10 | 0.4% |
| **Sialkot** | Pakistan | 9 | 0.3% |
| **Quetta** | Pakistan | 5 | 0.2% |

---

## 6. Workplace Arrangement Distribution

| Workplace Type | Count | % of Known Arrangements | Notes |
| :--- | :--- | :--- | :--- |
| **Remote** | 1,197 | 51.8% | Standardized |
| **On-site** | 943 | 40.8% | Standardized |
| **Hybrid** | 169 | 7.3% | Standardized |

---

## 7. Seniority Level Distribution

| Seniority Level | Listings Count | % of Total Postings |
| :--- | :--- | :--- |
| **Mid-Level** | 2,797 | 62.3% |
| **Lead / Principal** | 653 | 14.5% |
| **Senior** | 565 | 12.6% |
| **Junior / Entry-Level** | 355 | 7.9% |
| **Executive / Director** | 121 | 2.7% |

---

## 8. Data Quality Assurance Audit

- **Duplicate Job IDs:** 0
- **Duplicate Job URLs:** 777
- **Invalid Date Formats:** 0
- **Invalid Salary Ranges (min > max):** 0
- **Invalid Experience Ranges (min > max):** 0
- **Unmapped / Foreign Cities:** 1807 (predominantly remote or foreign roles)
- **Manual Review Flagged Records:** 1074

---

## 9. Legal Attribution Notice

> *“Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps.”*
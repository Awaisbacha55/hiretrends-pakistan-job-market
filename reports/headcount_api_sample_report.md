# Headcount Labs Pakistan Job Market API: Sample Ingestion & Feasibility Report

**Project:** HireTrends — Pakistan Tech Job Market Intelligence  
**Document:** Headcount Labs API Sample Evaluation & Feasibility Report  
**Date of Extraction:** November 20, 2026  
**Endpoint Tested:** `GET https://api.headcountlabs.com/v1/jobs?country=PK&currentness=current&limit=10`  
**License Compliance:** Open Database License (ODbL) 1.0 & Database Contents License (DbCL) 1.0  

---

## 1. Executive Summary

As part of the HireTrends data sourcing pipeline, an authorized sample of **exactly 10 real job records** for Pakistan (`country=PK`) was extracted from the **Headcount Labs Jobs API** using secure bearer token authentication. 

The purpose of this inspection is to assess:
1. Field coverage and schema alignment with the HireTrends 19-attribute data dictionary.
2. Salary transparency and compensation availability.
3. Geographical location granularity and workplace classification (remote vs. on-site).
4. Description depth for natural language processing and skill extraction.
5. Legal licensing, attribution compliance, and redistribution constraints.

---

## 2. Ingestion Summary & Statistics

| Metric | Result | Notes |
| :--- | :--- | :--- |
| **Total Sample Records** | **10** | Exactly 10 current, deduplicated listings retrieved |
| **HTTP Response Status** | `200 OK` | Fast response (< 2.5 seconds) via HTTPS |
| **Salary / Pay Data** | **0 / 10 (0%)** | Marked `state: extraction_failed` (omitted by employer) |
| **Description Data** | **10 / 10 (100%)** | Rich unstructured text (average length: ~3,200 chars) |
| **Location Data** | **10 / 10 (100%)** | Array of structured location objects with `country: PK` |
| **Work Arrangement** | **7 / 10 (70%) Remote, 3 / 10 (30%) Omitted** | Remote tech roles open to Pakistani engineers |
| **Employer Attribution** | **10 / 10 (100%)** | Identified hiring companies (DHL, Pavago) |

---

## 3. Schema & Field Availability Analysis

Headcount Labs represents fields as structured objects containing a `state` attribute (`known`, `source_omitted`, `extraction_failed`) and a `value` attribute.

### 3.1 Observed Fields in API Response
* `job_id`: Stable UUIDv4 string (e.g., `86c8e235-61c6-4086-ad4e-53c3150cca21`). Primary key.
* `employer_name`: Object `{"state": "known", "value": "DHL Pakistan (Private) Limited"}`.
* `title`: Object `{"state": "known", "value": "Director National & GMNC"}`.
* `description`: Object `{"state": "known", "value": "..."}` containing full job posting text.
* `work_arrangement`: Explicitly identifies `remote` vs. `source_omitted`.
* `locations`: Array of geographical objects containing `city`, `region`, `country`, and coordinate identifiers.
* `currentness`: Status string (`current`).
* `stale`: Boolean (`false`).
* `company_id`: Global company UUID.
* `job_first_seen_at`, `curated_at`, `job_updated_at`: ISO 8601 UTC timestamps.
* `postings`: Array of underlying ATS postings with `posting_url`, `application_url`, `source` (e.g., `phenom`, `workable`), and `source_posting_id`.

### 3.2 Missing or Unpopulated Fields
* **Salary / Pay (`pay`):** Absent in all 10 sample records. The employers in this sample did not disclose compensation figures on their career sites or ATS forms.
* **Experience Requirement (`experience`):** Not available as a standalone top-level field; must be parsed from the raw `description` text using Day 2 regular expressions.
* **Employment Type (`employment_type`):** Not populated as an explicit categorical field in this endpoint query; must be inferred or extracted from descriptions.

---

## 4. Location & Workplace Arrangement Coverage

1. **Physical / On-Site Roles:**
   * Postings for DHL Pakistan explicitly identified `city: Karachi`, `region: Sindh`, `country: PK`.
2. **Remote Roles:**
   * 7 of the 10 postings (from Pavago) are designated `work_arrangement: remote`. These represent international/regional tech companies hiring engineers resident in Pakistan (`country=PK`).
   * Roles include:
     * *Cloud / Network / Cybersecurity Engineer*
     * *Senior Backend Engineer*
     * *Full Stack AI Developer*
     * *Senior Software Engineer*

---

## 5. Licensing, Attribution & Redistribution Policy

### 5.1 Applicable Licenses
* **Database Structure:** **Open Database License (ODbL) 1.0**. Grants rights to share, adapt, and build upon the compiled dataset, subject to attribution and share-alike conditions.
* **Derived Database Contents:** **Database Contents License (DbCL) 1.0**. Governs derived values such as normalized job IDs, location linkages, and classifications.

### 5.2 Mandatory Attribution Notice
In accordance with Headcount Labs terms, any public presentation or derivative distribution must include the following notice:

> *"Job data: Headcount Labs (https://headcountlabs.com), ODbL 1.0. Job descriptions belong to their employers. Location data © OpenStreetMap contributors and Overture Maps."*

### 5.3 Redistribution Boundaries & Copyright Notice
* **Employer Description Copyright:** Raw job descriptions belong to their respective corporate employers. The Headcount Labs database license does **not** grant copyright ownership of employer text.
* **Compliance Action:** The 10-record sample in `data/samples/headcount_pakistan_sample.json` is retained strictly for technical integration validation, unit testing, and educational research. For broader data analysis, derived analytical metrics (skills arrays, city tallies, word frequencies) will be published rather than bulk raw text.

---

## 6. Analytical Implications for HireTrends

1. **High Quality for Skill & NLP Extraction:** The 100% availability of full-text descriptions provides rich input for regex extraction of technical skills (Python, Cloud, AI, Django, Kafka, etc.) planned for Day 3.
2. **Salary Sparsity Challenge:** As observed across global and Pakistani job portals, tech employers rarely advertise baseline compensation publicly. The HireTrends dashboard must transparently report sample size and confidence intervals when displaying wage benchmarks.
3. **Remote Tech Market Capture:** The API effectively indexes global companies actively seeking remote Pakistani engineering talent, complementing traditional domestic job portals.

---

## 7. Sample Data Storage Location
* Raw sample file: [`data/samples/headcount_pakistan_sample.json`](../data/samples/headcount_pakistan_sample.json)
* Historical labor dataset: Unmodified in project archive.

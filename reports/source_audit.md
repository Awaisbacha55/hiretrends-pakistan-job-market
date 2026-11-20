# HireTrends: Ethical Website Source Audit & Compliance Report

**Project:** HireTrends — Pakistan Tech Job Market Intelligence  
**Document:** Source Audit, Robots.txt Verification, and Terms of Use Analysis  
**Date of Audit:** November 20, 2026  
**Auditor:** HireTrends Engineering & Compliance Team  
**Compliance Standard:** Ethical Scraping Framework, Robot Exclusion Standard (RFC 9309), and Platform Terms of Service

---

## 1. Executive Summary & Ethical Principles

HireTrends is dedicated to establishing an ethical, transparent, and legally compliant data pipeline for analyzing the technology employment landscape in Pakistan. Automated data collection must balance research goals with platform rights, server loads, and data privacy.

### Core Ethical Guidelines:
1. **Terms of Service Supremacy:** A permissive `robots.txt` does not grant permission to violate platform Terms of Service (ToS). Both technical protocols and legal terms must align.
2. **Fail-Closed Architecture:** Any source whose legal terms or robots policy cannot be verified, or where permission is ambiguous, defaults to collection refusal (`PROHIBITED` or `REQUIRES_PERMISSION`).
3. **No Technical Circumvention:** HireTrends strictly forbids bypassing login walls, CAPTCHAs, paywalls, IP blocks, or Web Application Firewalls (WAFs).
4. **Data Minimization & Zero PII Policy:** No personally identifiable information (PII)—including candidate names, resumes, email addresses, phone numbers, or recruiter profiles—will be scraped or stored.
5. **Polite Crawling:** For any authorized endpoint, request rates must be strictly throttled (minimum 3–10 seconds between calls) with transparent User-Agent identification.

---

## 2. Detailed Source Audits

### Source 1: Mustakbil (Commercial Job Portal)
* **Official URL:** `https://www.mustakbil.com/`
* **Robots URL:** `https://www.mustakbil.com/robots.txt`
* **Terms URL:** `https://www.mustakbil.com/terms-of-service`
* **Source Type:** Commercial Job Board (Operated by TechnoBird)
* **Inspection Date:** 2026-11-20

#### Technical Audit (`robots.txt`):
* `robots.txt` is accessible (HTTP 200).
* Disallows specific query patterns, user account areas, and internal endpoints.
* Public job listings are indexed by standard web crawlers.

#### Legal & Terms of Service Audit:
* Mustakbil's Terms of Service explicitly prohibit automated data extraction. Specifically:
  * Users and third parties are forbidden from copying, scraping, framing, or mirroring platform content and services.
  * Prohibition against decompiling, reverse engineering, or scraping to build competing databases of jobseekers or employers.
  * Explicit restriction against extracting platform data to train machine learning models.

#### Decision & Rationale:
* **Final Permission Status:** `PROHIBITED`
* **Reasoning:** Even though certain listing paths do not have robots.txt disallow directives for general crawlers, the platform's Terms of Service unequivocally prohibit scraping, database compilation, and model training. In accordance with our ethical standard, automated collection is strictly banned.

---

### Source 2: Rozee.pk (Commercial Job Portal)
* **Official URL:** `https://www.rozee.pk/`
* **Robots URL:** `https://www.rozee.pk/robots.txt`
* **Terms URL:** `https://www.rozee.pk/terms-of-service`
* **Source Type:** Commercial Job Board (Operated by Naseeb Online Services)
* **Inspection Date:** 2026-11-20

#### Technical Audit (`robots.txt`):
* Automated HTTP requests to `https://www.rozee.pk/robots.txt` return **HTTP 403 Forbidden**.
* The platform employs Cloudflare WAF / anti-bot mechanisms that actively challenge and block non-browser automated requests.

#### Legal & Terms of Service Audit:
* Naseeb Online Services / Rozee.pk terms restrict unauthorized programmatic harvesting of platform data, candidate listings, and employer vacancies.
* Access is granted for genuine individual job seeking and corporate recruiting; mass extraction without explicit written agreement violates acceptable use guidelines.

#### Decision & Rationale:
* **Final Permission Status:** `REQUIRES_PERMISSION`
* **Reasoning:** The automated rejection of crawler requests (HTTP 403) signals strict technical protection against unauthorized bots. Combined with contractual restrictions on scraping, automated collection cannot proceed without formal written partnership or access to an official API. The HireTrends engine will refuse automated scraping of this source.

---

### Source 3: Open Data Pakistan — Job Market Dataset
* **Official URL:** `https://www.opendata.com.pk/dataset/pakistan-s-job-market`
* **Robots URL:** `https://www.opendata.com.pk/robots.txt`
* **Source Type:** Open Government / Civic Data Repository (CKAN-based)
* **Inspection Date:** 2026-11-20

#### Technical Audit (`robots.txt`):
* `robots.txt` returns HTTP 200.
* Defines `Crawl-delay: 10` for standard user agents.
* Disallows automated crawling of dynamic faceted search and individual resource views:
  * `Disallow: /dataset/*/resource/*/view/`
  * `Disallow: /organization/*?`
  * `Disallow: /*_tags_limit`

#### Legal & Licensing Audit:
* The dataset is released under the **Open Data Commons Open Database License (ODbL)**.
* Permitted for public research, academic study, and market intelligence, subject to attribution and open derivative standards.
* The dataset represents historical labor market records (primarily covering historical periods such as 2018–2020).

#### Decision & Rationale:
* **Final Permission Status:** `DATASET_ONLY`
* **Reasoning:** Live web scraping of portal pages is restricted by `robots.txt` (`Crawl-delay: 10` and view disallows). However, direct bulk download of the published ODbL tabular dataset is authorized and compliant. This source will be ingested via authorized file download rather than active HTML scraping.

---

## 3. Summary of Source Permissions

| Source Name | Platform Type | Permission Status | Allowed Collection Method | Rate Limit | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mustakbil** | Commercial Job Board | `PROHIBITED` | None (Blocked) | N/A | Hard block in scraper configuration; do not collect. |
| **Rozee.pk** | Commercial Job Board | `REQUIRES_PERMISSION` | Official API / Partner Agreement | N/A | Hard block; submit formal research data request. |
| **Open Data Pakistan** | Open Data Portal | `DATASET_ONLY` | Authorized Dataset Download | N/A | Download static CSV/XLSX release under ODbL license. |

---

## 4. Enforcement Mechanism in Code

The HireTrends data collection framework strictly enforces these statuses at runtime:
1. `config/sources.json` is the sole source of truth.
2. `src/collection/scraper.py` verifies both:
   * `permission_status == "APPROVED"`
   * Target URL is permitted by `RobotFileParser.can_fetch()`
3. Any attempt to scrape an unapproved source raises `PermissionError` and halts execution.
4. No command-line bypasses or override flags exist in the production codebase.

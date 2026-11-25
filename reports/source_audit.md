# Data Source Audit

## Overview

HireTrends collects Pakistan technology job postings through an authorized, structured API rather than scraping HTML job portals directly. All collection runs are governed by `config/sources.json`, which enforces allowlist/blocklist rules before any request is executed.

---

## Primary Active Source

| Attribute | Detail |
| :--- | :--- |
| **Source Name** | Headcount Labs Jobs API |
| **Base URL** | `https://api.headcountlabs.com` |
| **Endpoint Used** | `/v1/jobs?country=PK&currentness=current&limit=250` |
| **Collection Timestamp** | `2026-11-20 16:17:33 UTC` |
| **Snapshot Watermark** | `2026-11-20T16:16:45.703Z` |
| **Raw Records Collected** | `4,491` records across `18` API pages |
| **License** | Open Data Commons Open Database License (ODbL 1.0) and Database Contents License (DbCL 1.0) |
| **Status** | Active / Authorized |

### Why API Collection Over Direct Scraping
- **Compliance:** Accessing a documented JSON API with open-data licensing avoids violating portal Terms of Service or triggering anti-bot defenses.
- **Schema Consistency:** API responses provide structured fields (`job_title`, `company`, `city`, `country`, `posted_date`, `salary_text`, `job_url`), reducing HTML parser fragility.
- **Reproducibility:** The collection watermark (`2026-11-20T16:16:45.703Z`) and raw JSON/CSV artifacts allow deterministic downstream cleaning and verification.

### Known Source Limitations
1. **Single-Snapshot Survivorship Bias:** Querying `currentness=current` captures listings active and indexed at the snapshot time (`2026-11-20`). Postings that expired or were filled earlier are underrepresented, so longitudinal growth rates (such as "fastest-growing skills") cannot be measured from this snapshot alone.
2. **Geographic & Domain Noise:** Under `country=PK`, the API returns some international/remote-elsewhere listings (`345` Foreign records after deduplication) as well as non-technology roles (`1,950` Non-Technology and `836` Uncertain records after deduplication). Downstream classification and filtering isolate the Confirmed Pakistan Tech subset (`848` all-dates; `685` within the 12-month window `2025-11-20` to `2026-11-20`).
3. **Sparse Salary Disclosure:** Compensation is optional in source listings; only `8` of `685` (`1.17%`) Confirmed Pakistan Tech Recent 12M postings include parseable salary figures.

---

## Historical & Excluded Sources

| Source | Status in `config/sources.json` | Notes |
| :--- | :--- | :--- |
| **Open Data Pakistan** | `DATASET_ONLY` (ODbL) | Historical reference dataset context only; not part of the active Headcount Labs API collection snapshot. |
| **Mustakbil** | `PROHIBITED` | Explicitly blocked in `config/sources.json` due to scraping restrictions; no automated collection is permitted. |
| **Rozee.pk** | `REQUIRES_PERMISSION` | Explicitly blocked in `config/sources.json` without written authorization; excluded from automated collection. |

---

## Governance & Attribution
- All scripts check `config/sources.json` before fetching data.
- Outputs derived from the Headcount Labs Jobs API retain source attribution (`source = "headcount_labs_api"`) and preserve `job_url` links to original listings in accordance with ODbL 1.0 / DbCL 1.0 attribution requirements.

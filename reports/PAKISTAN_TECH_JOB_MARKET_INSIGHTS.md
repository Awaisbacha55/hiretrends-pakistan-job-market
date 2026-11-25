# Pakistan Tech Job Market Insights (Recent 12 Months)

**Primary Scope:** Confirmed Pakistan Tech, Recent 12 Months (`N = 685`)  
**Date Window:** `2025-11-20` through `2026-11-20`  
**Source Snapshot:** Headcount Labs Jobs API (`2026-11-20`)

---

## Executive Summary

From `4,491` raw job postings collected under `country=PK`, removing `784` exact URL duplicates yields `3,707` unique listings. Filtering to confirmed Pakistan locations (`3,362`), confirmed technology roles (`848`), and postings dated within the last 12 months (`2025-11-20` to `2026-11-20`) produces the primary analysis cohort of **`685` Confirmed Pakistan Tech postings** (`163` older postings excluded).

Across this cohort, employer demand is led by **Python (`39.12%`)**, **Microsoft Azure (`38.39%`)**, **CI/CD (`36.93%`)**, **SQL (`36.79%`)**, and **AWS (`33.58%`)**. Geographically, hiring remains concentrated in **Lahore (`45.55%`)**, **Islamabad (`26.68%`)**, and **Karachi (`24.14%`)**, which together account for **`96.37%`** of mapped Pakistan tech roles (`N = 551`).

---

## 1. Dataset Filtering Funnel

| Stage | Records | Excluded | Share Retained |
| :--- | ---: | ---: | ---: |
| Raw collected (`country=PK`) | `4,491` | — | `100.00%` |
| Deduplicated (unique `job_url`) | `3,707` | `784` duplicates | `82.54%` |
| Confirmed Pakistan (`country_classification == "Pakistan"`) | `3,362` | `345` Foreign | `90.69%` of dedup |
| Confirmed Pakistan Tech (`technology_category == "Tech"`) | `848` | `1,737` Non-tech, `777` Uncertain | `25.22%` of PK |
| **Recent 12M Pakistan Tech (`2025-11-20` to `2026-11-20`)** | **`685`** | **`163` older postings** | **`80.78%` of PK Tech** |

---

## 2. Top In-Demand Skills (`N = 685`)

| Rank | Skill | Postings | Share of Cohort |
| :---: | :--- | ---: | ---: |
| 1 | Python | `268` | `39.12%` |
| 2 | Microsoft Azure | `263` | `38.39%` |
| 3 | CI/CD | `253` | `36.93%` |
| 4 | SQL | `252` | `36.79%` |
| 5 | AWS | `230` | `33.58%` |
| 6 | Git | `211` | `30.80%` |
| 7 | JavaScript | `174` | `25.40%` |
| 8 | Large Language Models | `134` | `19.56%` |
| 9 | Google Cloud Platform | `132` | `19.27%` |
| 10 | Docker | `131` | `19.12%` |

Cloud platforms (Azure, AWS, GCP), automation (`CI/CD`, `Docker`), and data/AI foundations (`Python`, `SQL`, `Large Language Models`) sit at the core of recent Pakistan tech demand.

---

## 3. Skill Co-Occurrence Highlights (`N = 685`)

The strongest skill pairings reflect multi-cloud and DevOps-heavy production stacks:

| Rank | Skill Pair | Co-Occurrences | Share of Cohort | Jaccard Similarity |
| :---: | :--- | ---: | ---: | ---: |
| 1 | AWS + Microsoft Azure | `148` | `21.61%` | `0.429` |
| 2 | AWS + CI/CD | `142` | `20.73%` | `0.416` |
| 3 | AWS + Python | `142` | `20.73%` | `0.399` |

---

## 4. Target Role Distribution (`N = 685`)

Across the 12 tracked engineering and data role buckets:

| Role | Postings (`N`) | Role | Postings (`N`) |
| :--- | ---: | :--- | ---: |
| Software Engineer | `70` | Python Developer | `14` |
| Full Stack Developer | `32` | Backend Developer | `12` |
| AI Engineer | `30` | Machine Learning Engineer | `12` |
| Cybersecurity Engineer | `25` | Frontend Developer | `11` |
| DevOps Engineer | `20` | Data Scientist | `9` |
| Data Analyst | `15` | Cloud Engineer | `7` |

Generalist **Software Engineer** and **Full Stack Developer** roles represent the largest named buckets, followed closely by specialized **AI Engineer** (`N = 30`) and **Cybersecurity Engineer** (`N = 25`) demand. Remaining postings fall into broader or unmapped `"Other"` titles.

---

## 5. Geographic & Workplace Breakdown

### City Distribution (Mapped Pakistan Cities, `N = 551`)
- **Lahore:** `251` (`45.55%`)
- **Islamabad:** `147` (`26.68%`)
- **Karachi:** `133` (`24.14%`)
- **Other Cities:** `20` (`3.63%`)

Together, Lahore, Islamabad, and Karachi account for **`96.37%`** of mapped Pakistan tech postings.

### Workplace Model (`N = 356` with known arrangement; `329` unstated)
- **On-site:** `195` (`54.78%`)
- **Remote:** `128` (`35.96%`)
- **Hybrid:** `33` (`9.27%`)

---

## 6. Compensation Snapshot (Indicative Only, `N = 8`)

Only **`8` of `685` (`1.17%`)** recent Pakistan tech postings disclose parseable salary figures, so compensation statistics are indicative only and cannot be generalized across the full market:

- **PKR-denominated roles (`N = 6`):** Median **`PKR 175,000/month`**, IQR `PKR 97,500–312,500/month`, range `PKR 70,000–450,000/month`.
- **USD-denominated roles (`N = 2`, low sample):** Median **`$1,300/month`**, range `$600–$2,000/month`.

---

## 7. Methodological Limitations

1. **Single-Snapshot Limitation (No Growth Rates):** Data was collected in a single snapshot (`2026-11-20`) using `currentness=current`. Because no historical multi-period baseline is available, skill growth rates (e.g., "fastest-growing skills") cannot be reliably measured.
2. **Survivorship Bias:** Active/indexed postings at the collection timestamp overrepresent open, ongoing, or recently posted roles while undercounting postings filled or removed earlier in the 12-month window.
3. **Salary Sparsity:** With `98.83%` of recent Pakistan tech postings omitting compensation, salary figures reflect only the small subset of transparent employers.

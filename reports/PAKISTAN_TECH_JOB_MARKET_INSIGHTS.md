# Pakistan Tech Job Market Insights (Recent 12 Months)

**Primary Scope:** Confirmed Pakistan Tech, Recent 12 Months (`N = 685`)  
**Date Window:** `2025-11-20` through `2026-11-20`  
**Source Snapshot:** Headcount Labs Jobs API (`2026-11-20`)

---

## Executive Summary

From `4,491` raw job postings collected under `country=PK`, removing `784` exact URL duplicates yields `3,707` unique listings. Filtering to confirmed Pakistan locations (`3,362`), confirmed technology roles (`848`), and postings dated within the last 12 months (`2025-11-20` to `2026-11-20`) produces the primary analysis cohort of **`685` Confirmed Pakistan Tech postings** (`163` older postings excluded).

Across this cohort, employer demand is led by **Python (`39.12%`)**, **Microsoft Azure (`38.39%`)**, **CI/CD (`36.93%`)**, **SQL (`36.79%`)**, and **AWS (`33.58%`)**. Geographically, hiring remains concentrated in **Lahore (`45.18%`)**, **Islamabad (`26.25%`)**, and **Karachi (`23.93%`)**, which together account for **`95.36%`** of mapped Pakistan tech roles (`N = 560`; `125` / `18.25%` missing or unmapped).

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

### City Distribution (`N = 560` Mapped Pakistan Cities; `125` [`18.25%`] Missing/Unmapped)
- **Lahore:** `253` (`45.18%` of mapped; `36.93%` of all `685`)
- **Islamabad:** `147` (`26.25%` of mapped; `21.46%` of all `685`)
- **Karachi:** `134` (`23.93%` of mapped; `19.56%` of all `685`)
- **Other Mapped Cities:** `26` (`4.64%` of mapped — `Peshawar: 10`, `Rawalpindi: 7`, `Akora Khattak: 2`, `Faisalabad: 2`, `Hub: 2`, `Pakpattan: 2`, `Hyderabad: 1`)
- **Missing / Unmapped City:** `125` (`18.25%` of all `685` — `115` omitted in source, `6` multi-city delimited strings, `4` non-city noise)

Together, Lahore, Islamabad, and Karachi account for **`95.36%`** of mapped Pakistan tech postings (`77.96%` of all `685`).

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

## 7. Practical Recommendations for Students

Based on the `N = 685` Recent 12M Pakistan Tech snapshot (reflecting active/indexed postings in this dataset rather than the entire national job market):

1. **Build foundations in Python, SQL, and Git:** `Python` (`268`, `39.12%`), `SQL` (`252`, `36.79%`), and `Git` (`211`, `30.80%`) appear across software engineering, data, and AI listings, making them versatile core skills to learn early.
2. **Learn cloud and deployment skills alongside coding:** `Microsoft Azure` (`263`, `38.39%`), `CI/CD` (`253`, `36.93%`), and `AWS` (`230`, `33.58%`) rank near the top of the market, and skill pairs such as `AWS + Microsoft Azure` (`148`, `21.61%`, Jaccard `0.429`), `AWS + CI/CD` (`142`, `20.73%`), and `AWS + Python` (`142`, `20.73%`) frequently appear together.
3. **Choose a specialization based on observed role demand:** Generalist `Software Engineer` (`N = 70`) and `Full Stack Developer` (`N = 32`) roles lead named openings, while `AI Engineer` (`N = 30`), `Cybersecurity Engineer` (`N = 25`), and `DevOps Engineer` (`N = 20`) represent the largest specialized tracks in this cohort.
4. **Build a portfolio and prepare for remote work while recognizing geographic concentration:** Mapped Pakistan tech openings cluster heavily in Lahore, Islamabad, and Karachi (`95.36%` of `560` mapped cities), while `Remote` accounts for `128` of `356` (`35.96%`) listings with a stated workplace model. Demonstrating deployed projects on GitHub can help candidates outside major hubs compete for remote-friendly roles.

---

## 8. Methodological Limitations

1. **Single-Snapshot Limitation (No Growth Rates):** Data was collected in a single snapshot (`2026-11-20`) using `currentness=current`. Because no historical multi-period baseline is available, skill growth rates (e.g., "fastest-growing skills") cannot be reliably measured.
2. **Survivorship Bias:** Active/indexed postings at the collection timestamp overrepresent open, ongoing, or recently posted roles while undercounting postings filled or removed earlier in the 12-month window.
3. **Salary Sparsity:** With `98.83%` of recent Pakistan tech postings omitting compensation, salary figures reflect only the small subset of transparent employers.

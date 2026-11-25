# HireTrends — Pakistan Tech Job Market Intelligence

An ethical, data-driven intelligence platform tracking technology job vacancies, compensation benchmarks, and skill demands across Pakistan's evolving software landscape.

[![Live Dashboard](https://img.shields.io/badge/Streamlit%20App-Live%20Demo-ff4b4b?style=flat&logo=streamlit)](https://hiretrends-pakistan-job-market-zcyjuxxmt7gyyq3e6dfsl2.streamlit.app/skill_cooccurrence)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Video%20Demo-red?style=flat&logo=youtube)](https://youtu.be/Gcz30Iix90Q)
[![Automated Tests](https://img.shields.io/badge/Automated%20Tests-125%20Passing-brightgreen.svg)]()
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Development%20Status-Production%20Ready-brightgreen.svg)]()

---

## 1. Project Overview & Introduction

**HireTrends** is an applied data engineering and market intelligence platform developed during the **LogicBlaze Technologies 8-Week Internship Learning Path**. It collects, cleans, standardizes, models, and visualizes tech recruitment listings across Pakistan. By transforming noisy, unstructured job descriptions into structured tabular schemas and interactive analytics, HireTrends empowers computer science students, software engineers, and hiring managers with empirical market data.

> [!NOTE]
> **Week 3 Production Deployment Complete:** All Day 1–5 implementations have undergone an exhaustive quality assurance audit. From **4,491 raw API records** collected via the **Headcount Labs Jobs API** (ODbL 1.0), two-tier deduplication yields **3,707 unique records**, country classification isolates **3,362 Pakistan postings** (345 foreign), technology classification identifies **848 Confirmed Pakistan Tech** roles (all dates `2019–2026`), and filtering to the **Last 12 Months (`2025-11-20` to `2026-11-20`)** produces the primary **685 Confirmed Pakistan Tech** 2025/26 dataset (`163` stale 2019–2025 postings excluded; historical datasets preserved). The codebase features an extensible longitudinal trend engine (`src/analysis/trend_analysis.py`), a scope- and date-aware 8-page interactive Streamlit dashboard (`dashboard/app.py`), CSV export capabilities, Playwright-automated visual regression tests, and a **100% passing offline unit test suite**.

---

## 🚀 Explore HireTrends

### 🌐 Live Interactive Dashboard
The HireTrends dashboard is deployed on Streamlit Community Cloud.

👉 **[Open Live HireTrends Dashboard](https://hiretrends-pakistan-job-market-zcyjuxxmt7gyyq3e6dfsl2.streamlit.app/skill_cooccurrence)**

Explore job market insights, technology skills, job roles, salary analysis, workplace arrangements, location analysis, and skill co-occurrence across 8 interactive pages with zero local setup required.

### 🎥 Project Demonstration Video
Watch the complete project demonstration on YouTube:

👉 **[▶ Watch HireTrends Project Demo](https://youtu.be/Gcz30Iix90Q)**

The video demonstrates the dashboard, analytical features, visualizations, data methodology, and project workflow in an executive 2–3 minute walkthrough.

---

## 🔗 Quick Links

| Destination | Type | Link | Description |
| :--- | :---: | :---: | :--- |
| **Live Interactive Dashboard** | Web App | [Launch App](https://hiretrends-pakistan-job-market-zcyjuxxmt7gyyq3e6dfsl2.streamlit.app/skill_cooccurrence) | Deployed Streamlit Community Cloud analytics dashboard |
| **YouTube Video Demo** | Video | [Watch Video](https://youtu.be/Gcz30Iix90Q) | Full project presentation and dashboard walkthrough |
| **GitHub Repository** | Source Code | [View Repo](https://github.com/Awaisbacha55/hiretrends-pakistan-job-market) | Complete codebase, unit tests, and pipelines |
| **Market Insights Report** | Report | [Read Report](reports/PAKISTAN_TECH_JOB_MARKET_INSIGHTS.md) | *"What the Pakistani Tech Job Market Wants in 2025/26"* |
| **Statistical Validation Report** | Report | [Read Report](reports/STATISTICAL_VALIDATION_REPORT.md) | Census reconciliation, formulas, denominators & salary models |
| **Final Project Audit** | Report | [Read Report](reports/FINAL_PROJECT_AUDIT.md) | 22-requirement compliance verification matrix |
| **Deployment Guide** | Documentation | [View Guide](docs/DEPLOYMENT_GUIDE.md) | Streamlit Community Cloud step-by-step hosting guide |
| **Video Presentation Script** | Documentation | [View Script](docs/DEMO_VIDEO_SCRIPT.md) | Presentation storyboard and timed demo voiceover |

---

## 2. Interactive Dashboard Preview

The complete 8-page Streamlit dashboard runs live on Streamlit Cloud or locally:

| 📊 Market Overview | 🛠️ Skills Explorer |
| :---: | :---: |
| ![Market Overview](docs/screenshots/overview.png) | ![Skills Explorer](docs/screenshots/skills_explorer.png) |
| **💰 Salary Insights** | **📍 Location Analysis** |
| ![Salary Insights](docs/screenshots/salary_insights.png) | ![Location Analysis](docs/screenshots/location_analysis.png) |
| **🔗 Skill Co-occurrence Heatmap** | **💼 Role Explorer** |
| ![Skill Co-occurrence](docs/screenshots/skill_cooccurrence.png) | ![Role Explorer](docs/screenshots/role_explorer.png) |

*(Full gallery of all 8 pages captured via Playwright Chromium available in [`docs/screenshots/`](docs/screenshots/))*

---

## 3. Project Objectives

1. **Ethical & Compliant Data Ingestion:** Establish an automated collection pipeline respecting platform terms, avoiding unauthorized scraping, and utilizing official API licensing (ODbL 1.0).
2. **Standardized Target Baseline:** Ingest and curate a verified census with explicit scope and date separation: `4,491 raw collected` → `3,707 deduplicated` → `3,362 confirmed Pakistan` → `848 confirmed Pakistan tech (All Dates)` → **`685 confirmed Pakistan tech — Last 12 Months (2025-11-20 to 2026-11-20)`** (`jobs_pakistan_tech_recent.csv`).
3. **Data Cleaning & Normalization:** Standardize disparate job titles, parse seniority, canonicalize Pakistani cities, and normalize international compensation into Monthly PKR using official State Bank of Pakistan (SBP) exchange rates.
4. **NLP Skill Extraction:** Systematically extract 69 programming languages, cloud platforms, and developer frameworks using word-boundary regular expressions without substring false positives.
5. **Interactive Multipage Dashboard:** Deliver a modern SaaS analytics dashboard with global filtering, responsive Plotly visualizations, sample size transparency, and CSV data export.
6. **Academic & Statistical Rigor:** Non-parametric salary modeling (quartiles, medians, IQR), census reconciliation, and refusal to fabricate growth percentages from single-snapshot baselines.

---

## 4. Key Findings & Market Intelligence Summary

Empirical analysis of the **685 Recent (Last 12 Months: `2025-11-20` to `2026-11-20`) Confirmed Pakistan Technology** postings (`jobs_pakistan_tech_recent.csv`, with `163` stale 2019–2025 postings excluded from the `848` all-dates PK Tech cohort) reveals defining characteristics of Pakistan's 2025/2026 tech employment landscape (detailed in [`reports/PAKISTAN_TECH_JOB_MARKET_INSIGHTS.md`](reports/PAKISTAN_TECH_JOB_MARKET_INSIGHTS.md)):

1. **Most In-Demand Technical Skills (Recent 12M Confirmed Pakistan Tech, $N=685$):**
   - **Python leads overall:** Demanded in **39.1%** of recent confirmed Pakistan tech roles (268 unique jobs), driven by backend web services (FastAPI/Django) and AI/Data Science workloads.
   - **Cloud & Data Core:** Microsoft Azure (**38.4%**, 263 jobs), CI/CD (**36.9%**, 253 jobs), SQL (**36.8%**, 252 jobs), AWS (**33.6%**, 230 jobs), and Git (**30.8%**, 211 jobs).
   - **Modern Web, AI & Containers:** JavaScript (**25.4%**, 174 jobs), Large Language Models (**19.6%**, 134 jobs), Google Cloud Platform (**19.3%**, 132 jobs), and Docker (**19.1%**, 131 jobs).
   - *Skill-Growth Limitation:* Because this dataset is a single `currentness=current` snapshot, true longitudinal skill growth ("fastest-growing skills") cannot be measured reliably; `analyze_skill_growth()` explicitly returns `UNAVAILABLE_INSUFFICIENT_SNAPSHOTS` until multi-period snapshots are collected.
2. **The "Big Three" Metropolises Command 96.4% of Mapped Recent Pakistan Tech Demand ($N=551$ Mapped Cities):**
   - **Lahore (45.6% / 251 jobs):** Software export houses, agencies, and full-stack/mobile web.
   - **Islamabad (26.7% / 147 jobs):** AI/ML consultancies, cloud architecture, and multinational R&D.
   - **Karachi (24.1% / 133 jobs):** FinTech, corporate enterprise, banking, and data systems.
3. **Disclosed Compensation Within Recent 12M Confirmed Pakistan Tech ($N=8$ of $685$, 1.17% Disclosure Rate — *Indicative Only*):**
   - **Native PKR ($N=6$, monthly-normalized):** Median **PKR 175,000 / month** (IQR: 97.5k–312.5k PKR; range: 70k–450k PKR).
   - **Normalized USD ($N=2$, monthly-equivalent, low sample):** Median **\$1,300 / month** (range: \$600–\$2,000/mo).
   - **Broader Historical / All-Dates Context:** All-dates PK Tech ($N=848$): $N=11$ disclosed (`7` PKR median PKR 150,000/mo; `4` USD median \$1,300/mo). All deduplicated ($N=3,707$): $N=152$ disclosed (4.10%, incl. 70 hourly): Native PKR ($N=38$) median **PKR 70,000/mo**; Normalized USD ($N=113$, `hourly × 176` / `annual ÷ 12`) median **\$1,056/mo**; EUR ($N=1$) **€300/mo**.
   - **Conversion Methodology & Caveats:** Hourly rates assume **8 hrs/day × 22 working days/month = 176 hours/month** (analytical estimate only); annual salaries are divided by **12**. Converted PKR-equivalent figures use the fixed **State Bank of Pakistan (SBP) Mark-to-Market / Ready Reference** rate for **20 November 2026** (**1 USD = 276.5132 PKR**; actual transaction/remittance rates may differ). Because salary disclosure is very low and subject to selection bias, all salary findings are **indicative only**.
4. **Workplace Arrangements ($N=356$ Known; 329 Unstated):**
   - **54.8%** of known recent Pakistan tech postings are **on-site** (195), **36.0%** are **fully remote** (128), and **9.3%** are **hybrid** (33).

---

## 5. Reconciled Census & Statistical Integrity

Every stage from raw ingestion to the **Recent 12M Confirmed Pakistan Tech** analytical dataset is mathematically reconciled (see [`reports/STATISTICAL_VALIDATION_REPORT.md`](reports/STATISTICAL_VALIDATION_REPORT.md)):

```mermaid
flowchart TD
    Raw["1. Raw Ingested Postings (N=4,491)"] -->|"784 URL Duplicates Removed"| Dedup["2. Deduplicated Dataset (N=3,707)"]
    Dedup --> PK["3. Confirmed Pakistan (N=3,362)"]
    Dedup --> Foreign["Foreign Listings (N=345)"]
    PK --> PKTech["4. Confirmed PK Tech All Dates (N=848)"]
    PK --> PKNonTech["Pakistan Non-Tech (N=1,737)"]
    PK --> PKReview["Pakistan Uncertain / Review (N=777)"]
    PKTech -->|"Last 12M: 2025-11-20 to 2026-11-20"| Recent["5. Recent 12M PK Tech (N=685)"]
    PKTech -->|"163 Stale 2019–2025 Excluded"| Stale["Historical Only (N=163)"]
    
    Recent --> MappedLoc["Mapped PK Tech Cities (N=551)"]
    MappedLoc --> LHE["Lahore: 251 (45.55%)"]
    MappedLoc --> ISB["Islamabad: 147 (26.68%)"]
    MappedLoc --> KHI["Karachi: 133 (24.14%)"]
    MappedLoc --> Other["Other PK Cities: 20 (3.63%)"]
```

$$\begin{aligned}
\text{Deduplicated } (3,707) &= \text{Pakistan } (3,362) + \text{Foreign } (345) + \text{Unknown } (0) \\
\text{Pakistan-Only } (3,362) &= \text{Confirmed Tech } (848) + \text{Non-Tech } (1,737) + \text{Uncertain } (777) \\
\text{PK Tech All Dates } (848) &= \text{Recent 12M } (685) + \text{Stale 2019–2025 } (163) \\
\text{Recent PK Tech Mapped Cities } (551) &= \text{Lahore } (251) + \text{Islamabad } (147) + \text{Karachi } (133) + \text{Other } (20) \\
\text{Recent PK Tech Workplace Known } (356) &= \text{On-site } (195) + \text{Remote } (128) + \text{Hybrid } (33) \quad [329 \text{ unstated}]
\end{aligned}$$

---

## 6. Technology Stack

* **Language:** Python 3.12+ (verified: Python 3.12.10)
* **Data Processing & Analytics:** `pandas`, `numpy`
* **Visualization & Reporting:** `plotly`, `matplotlib`, `seaborn`
* **Interactive UI:** `streamlit` (multipage architecture via `st.Page` / `st.navigation`)
* **Automated Visual Testing:** `playwright` (Chromium headless engine)
* **API Ingestion & Resilience:** `requests`, `tenacity`, `python-dotenv`
* **Testing & Quality Assurance:** `pytest` (125 tests, 100% offline)
* **CI/CD & Version Control:** GitHub Actions, Git
* **Cloud Hosting:** Streamlit Community Cloud

---

## 7. Dashboard Features Across 8 Interactive Pages

1. **📊 Market Overview (`overview.py`):** Executive KPI cards, technology segmentation donut, regional density, and seniority breakdown.
2. **🛠️ Skills Explorer (`skills_explorer.py`):** Deep-dive into 69 technical skills with search, domain filtering (Cloud, AI, Languages), progress bars, and CSV download.
3. **💼 Role Explorer (`role_explorer.py`):** In-depth skill, experience, location, and salary profiles for 12 key tech occupations with CSV download.
4. **💰 Salary Insights (`salary_insights.py`):** Non-parametric compensation benchmarking, currency distribution (USD vs. PKR), experience scaling, and quartile tables with CSV download.
5. **📍 Location Analysis (`location_analysis.py`):** Geographic tech hub rankings (Lahore, Karachi, Islamabad), interactive city comparison, and foreign posting isolation.
6. **🏢 Workplace Analysis (`workplace_analysis.py`):** Remote vs. On-site vs. Hybrid trends computed against verified known denominators ($N=1,856$) with transparent unstated disclosures.
7. **🔗 Skill Co-occurrence (`skill_cooccurrence.py`):** 12x12 symmetric correlation heatmap, Jaccard affinity index, and companion technology stack explorer.
8. **📜 Data & Methodology (`methodology.py`):** Complete data lineage, census balance equations, official SBP exchange rate benchmarks, and legal attribution notices.

---

## 8. Repository Structure

```text
hiretrends-pakistan-job-market/
│
├── data/
│   ├── raw/                  # Raw ingestion records (watermark locked; excluded from Git)
│   ├── processed/            # Cleaned, standardized tabular dataset (jobs_cleaned.csv, 2.2MB)
│   └── samples/              # Anonymized sample records for unit testing
│
├── dashboard/                # Interactive Streamlit multi-page analytics platform
│   ├── __init__.py           # Dashboard package marker
│   ├── app.py                # Main application entry point (st.navigation + sys.path bootstrap)
│   ├── data_loader.py        # Cached data ingestion and multi-criteria filters
│   ├── components.py         # Standardized KPI cards, sidebar filters, layout & footers
│   └── pages/                # Modern multipage architecture (with pathlib root bootstrap)
│       ├── overview.py       # Market overview & executive KPIs
│       ├── skills_explorer.py # Deep-dive into 69 technical skills with CSV export
│       ├── role_explorer.py  # 12-target occupation skill profiles with CSV export
│       ├── salary_insights.py # Disclosed salary benchmarking (PKR & USD) with CSV export
│       ├── location_analysis.py # Geographic hub analysis & foreign partition
│       ├── workplace_analysis.py # Remote vs on-site vs hybrid trends with known denominators
│       ├── skill_cooccurrence.py # Pairwise co-occurrence heatmap & companion stack explorer
│       └── methodology.py    # Dataset provenance, census reconciliation & SBP rates
│
├── .streamlit/
│   └── config.toml           # Streamlit professional light SaaS theme & server config
│
├── docs/                     # Project documentation, guides, and screenshot assets
│   ├── DEPLOYMENT_GUIDE.md   # Step-by-step Streamlit Community Cloud deployment instructions
│   ├── DEMO_VIDEO_SCRIPT.md  # 2-3 minute presentation walkthrough script
│   └── screenshots/          # Real 1440x950 Playwright PNG screenshots (8 files)
│
├── reports/                  # Technical audit, empirical validation & intelligence reports
│   ├── FINAL_PROJECT_AUDIT.md # 22-requirement verification matrix
│   ├── STATISTICAL_VALIDATION_REPORT.md # Formulas, denominators & census reconciliation
│   ├── PAKISTAN_TECH_JOB_MARKET_INSIGHTS.md # Comprehensive 2025/26 market intelligence
│   ├── FINAL_COMPLETION_REPORT.md # Master 20-point quality audit sign-off
│   ├── data_cleaning_report.md # Cleaning, normalization & skills extraction report
│   ├── market_analysis_report.md # EDA & market intelligence findings
│   └── figures/              # Rendered Plotly HTML and PNG charts (14 publication figures)
│
├── src/                      # Production Python modules
│   ├── __init__.py           # Top-level package marker
│   ├── collection/           # Ingestion, source compliance, Headcount Labs API
│   ├── cleaning/             # Data cleaning, normalization, and NLP skill extraction
│   └── analysis/             # Statistical modeling, location, salary & trend engines
│       └── trend_analysis.py # Extensible longitudinal multi-snapshot growth engine
│
├── tests/                    # Automated unit test suite (125 tests passing offline)
├── .github/workflows/        # GitHub Actions continuous integration workflow
├── requirements.txt          # Production dependencies
├── .env.example              # Environment variable template
└── README.md                 # Project documentation
```

---

## 9. Quickstart & Installation (Windows PowerShell / Linux)

### Prerequisites
* Windows 10/11 with PowerShell (or Linux/macOS bash)
* Python 3.12 (verified: Python 3.12.10)
* Git

### Step-by-Step Setup

1. **Clone the Repository:**
   ```powershell
   git clone https://github.com/Awaisbacha55/hiretrends-pakistan-job-market.git
   cd hiretrends-pakistan-job-market
   ```

2. **Create Python Virtual Environment:**
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard Locally:**
   ```powershell
   streamlit run dashboard/app.py
   ```
   The dashboard opens immediately at `http://localhost:8501`. Because the pre-processed dataset is committed in `data/processed/jobs_cleaned.csv`, **no scraping, external databases, or API keys are required to run the dashboard!**

---

## 10. Running Automated Tests

HireTrends includes a comprehensive test suite covering source checking, API mapping, data cleaning, statistical modeling, trend analysis, and dashboard UI logic. All tests run **100% offline**:

```powershell
pytest -v
```

Verification output:
```text
tests/test_analysis_pipeline.py .............                           [ 10%]
tests/test_bulk_collection.py .....................                     [ 27%]
tests/test_cleaning_pipeline.py ...................................     [ 55%]
tests/test_dashboard.py ..............                                  [ 66%]
tests/test_headcount_api.py ..........                                  [ 74%]
tests/test_headcount_sample.py ........                                 [ 80%]
tests/test_scraper.py ...........                                       [ 89%]
tests/test_source_checker.py .............                              [100%]
============================= 125 passed in 4.14s =============================
```

---

## 11. Data Ethics & Responsible Use Charter

- **Terms of Service Supremacy:** Automated collection respects platform terms. Prohibited sources (e.g. Mustakbil) are blocked fail-closed; commercial job boards (e.g. Rozee.pk) requiring permission are never harvested without authorization.
- **Official API Ingestion:** Live data is sourced under official Open Database License (ODbL 1.0) and Database Contents License (DbCL 1.0) courtesy of [Headcount Labs](https://headcountlabs.com).
- **Privacy & Copyright Protection:** Candidate PII is never harvested. Full-text employer job descriptions are strictly excluded from git version control to protect employer copyright.
- **Exchange Rate Normalization:** Foreign salaries are standardized to monthly PKR equivalents (indicative only) using the fixed State Bank of Pakistan (SBP) Mark-to-Market / Ready Reference snapshot for 20 November 2026 (`USD = 276.5132 PKR`, `EUR = 295.00 PKR`).

---

## 12. Author & Acknowledgements

* **Author:** **Awais Bacha**  
  *Data Engineering Intern — LogicBlaze Technologies*  
  GitHub: [@Awaisbacha55](https://github.com/Awaisbacha55)
* **Program:** LogicBlaze Technologies 8-Week Internship Learning Path (Week 3 Capstone)
* **Dataset Provider:** [Headcount Labs](https://headcountlabs.com) (ODbL 1.0 / DbCL 1.0)
* **Geographic Data:** © OpenStreetMap contributors and Overture Maps
* **License:** Source code distributed under the open-source [MIT License](LICENSE).

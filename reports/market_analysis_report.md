# HireTrends — Pakistan Tech Job Market Intelligence Report
## Exploratory Data Analysis & Statistical Modeling (Day 4)

**Document Date:** November 20, 2026  
**Analytical Pipeline:** HireTrends Advanced Analytics Subsystem (`src/analysis/`)  
**Ingestion Source:** Headcount Labs Pakistan Jobs Dataset (`data/raw/headcount/jobs_raw.jsonl`)  
**Tabular Processed Cohort:** `data/processed/jobs_cleaned.csv`  
**License & Attribution:** Open Database License (ODbL) 1.0 & DbCL 1.0 (Headcount Labs); Location Entities © OpenStreetMap & Overture Maps.

---

## 1. Executive Summary

This report delivers empirical market intelligence on Pakistan's technology recruitment landscape based on **4,491 total job postings** collected via the Headcount Labs API on November 20, 2026. Through rigorous normalization, entity resolution, and NLP taxonomy matching across 69 technical skills, the analysis reveals a dual-tier market dynamic:

1. **Disclosed Compensation (Indicative Only — Low Disclosure):** Within Confirmed Pakistan Tech (`N=848`), only **11 postings (1.30%)** disclose salary (`7` native PKR, median **PKR 150,000/mo**; `4` USD, median **\$1,300/mo**, low sample). Across all deduplicated postings (`N=3,707`), **152 (4.10%)** disclose salary (`38` PKR, `113` USD incl. `70` hourly, `1` EUR).
2. **The "Big Three" Geographic Concentration:** 93.3% of all mapped local Pakistani tech vacancies are concentrated in just three cities: **Lahore** (38.3%), **Karachi** (32.3%), and **Islamabad** (22.7%).
3. **Core Engineering Stack Dominance (Recent 12M PK Tech, $N=685$):** Technical demand is anchored by **Python** (39.1%), **Microsoft Azure** (38.4%), **CI/CD** (36.9%), **SQL** (36.8%), **AWS** (33.6%), **Git** (30.8%), and **JavaScript** (25.4%).
4. **Generative AI Presence in Current Postings:** **Large Language Models (LLMs)** appear in **19.56%** (`134` of `685`) of recent 12-month Confirmed Pakistan Tech postings. *(Note: Because this is a single snapshot, no longitudinal growth rate or adoption velocity is claimed.)*

---

## 2. Dataset Scope, Period & Limitations

| Dimension | Scope / Bound | Methodological Safeguards |
| :--- | :--- | :--- |
| **Observation Timestamp** | November 20, 2026 (Snapshot Watermark `2026-11-20T16:16:45.703Z`) | Static snapshot ensuring total analytical reproducibility. |
| **Total Ingested Postings** | **4,491** | Validated via SHA-256 deduplication (0 duplicate Job IDs). |
| **Classified Technology Roles** | **1,075** (23.94% high-confidence tech cohort) | Segmented via transparent 16-tier taxonomy matching. |
| **Manual Review Flagged** | **1,074** (23.91% ambiguous or generic titles) | Tagged transparently; not forced into assumptions. |
| **Non-Technology Postings** | **2,342** (52.15% operations, medical, sales, retail) | Filtered out during role-specific technical evaluations. |
| **Salary Disclosure Rate** | **11** PK Tech (1.30%) / **152** Dedup (4.10%) | Indicative only; reported separately by currency with explicit sample sizes. |
| **Workplace Arrangement Known** | **2,309** postings (51.4% completeness) | Percentages calculated strictly using known records as denominator. |

---

## 3. Classification Reconciliation (Day 2 vs. Day 3)

During the transition from Day 2 Ingestion to Day 3 Cleaning, the reported technology job count in summary text shifted from 1,075 to 2,149. An exhaustive audit resolved this discrepancy:

* **Classifier Version Consistency:** The underlying core classification engine produced exactly **1,075 technology postings** in both Day 2 and Day 3 (`is_technology_job == True`).
* **The Reconciliation Finding:** In Day 3, ambiguous roles (e.g. "Operations Specialist", "Associate", "Coordinator", "Director") were explicitly isolated into an `Uncertain / Manual Review` category (1,074 postings) rather than defaulted to `Non-Technology`.
* **The Reporting Artifact:** The Day 3 Markdown summary table computed technical listings using the subtraction formula `total_records - non_tech_count` (`4,491 - 2,342 = 2,149`), which inadvertently grouped the 1,074 ambiguous manual-review records with the 1,075 verified technology records.
* **Resolution:** All Day 4 analyses strictly distinguish between **Confirmed Technology Jobs** ($N=1,075$), **Manual Review Postings** ($N=1,074$), and **Non-Technology Postings** ($N=2,342$).

---

## 4. Top Technical Skills Demanded in Recent Pakistan Tech Jobs ($N=685$)

Evaluated strictly on the **Recent 12-Month Confirmed Pakistan Tech** dataset (`2025-11-20` to `2026-11-20`, $N=685$), skills are ranked by the number of **unique job postings** requiring them:

| Rank | Technical Skill | Unique Postings | % of Recent PK Tech ($N=685$) | Primary Domain |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Python** | 268 | 39.12% | General / Backend / AI |
| **2** | **Microsoft Azure** | 263 | 38.39% | Cloud Infrastructure |
| **3** | **CI/CD** | 253 | 36.93% | DevOps & Automation |
| **4** | **SQL** | 252 | 36.79% | Databases & Querying |
| **5** | **AWS** | 230 | 33.58% | Cloud Infrastructure |
| **6** | **Git** | 211 | 30.80% | Core Version Control |
| **7** | **JavaScript** | 174 | 25.40% | Web Engineering |
| **8** | **Large Language Models** | 134 | 19.56% | Generative AI |
| **9** | **Google Cloud Platform** | 132 | 19.27% | Cloud Infrastructure |
| **10** | **Docker** | 131 | 19.12% | Containerization |
| **11** | **Kubernetes** | 117 | 17.08% | Cloud & Orchestration |
| **12** | **React** | 114 | 16.64% | Frontend Frameworks |
| **13** | **Java** | 114 | 16.64% | Enterprise Backend |
| **14** | **Machine Learning** | 113 | 16.50% | Artificial Intelligence |
| **15** | **PostgreSQL** | 110 | 16.06% | Relational Databases |
| **16** | **TypeScript** | 102 | 14.89% | Modern Frontend/Backend |
| **17** | **Linux** | 94 | 13.72% | Systems & Infrastructure |
| **18** | **Terraform** | 70 | 10.22% | Infrastructure as Code |
| **19** | **HTML** | 67 | 9.78% | Web Foundations |
| **20** | **Node.js** | 64 | 9.34% | Backend Runtime |

![Top 20 Skills](figures/top_20_skills.png)

---

## 5. Domain-Specific Cluster Demand (Recent 12M PK Tech, $N=685$)

### A. Programming Languages Demand
1. **Python:** 268 jobs (39.12% of Recent PK Tech)
2. **SQL:** 252 jobs (36.79%)
3. **JavaScript:** 174 jobs (25.40%)
4. **Java:** 114 jobs (16.64%)
5. **TypeScript:** 102 jobs (14.89%)
6. **HTML:** 67 jobs (9.78%)
7. **CSS:** 63 jobs (9.20%)
8. **PHP:** 21 jobs (3.07%)

### B. Cloud & DevOps Infrastructure Demand
1. **Microsoft Azure:** 263 jobs (38.39%)
2. **CI/CD:** 253 jobs (36.93%)
3. **AWS:** 230 jobs (33.58%)
4. **Git:** 211 jobs (30.80%)
5. **Google Cloud Platform:** 132 jobs (19.27%)
6. **Docker:** 131 jobs (19.12%)
7. **Kubernetes:** 117 jobs (17.08%)
8. **Linux:** 94 jobs (13.72%)

### C. Artificial Intelligence & Data Science Demand
1. **Large Language Models (LLMs):** 134 jobs (19.56%)
2. **Machine Learning:** 113 jobs (16.50%)
3. **PyTorch:** 54 jobs (7.88%)
4. **TensorFlow:** 50 jobs (7.30%)
5. **Deep Learning:** 38 jobs (5.55%)
6. **LangChain:** 28 jobs (4.09%)
7. **Computer Vision:** 21 jobs (3.07%)

### D. Databases & Big Data Demand
1. **SQL:** 252 jobs (36.79%)
2. **PostgreSQL:** 110 jobs (16.06%)
3. **MySQL:** 61 jobs (8.91%)
4. **Apache Spark:** 61 jobs (8.91%)
5. **MongoDB:** 50 jobs (7.30%)
6. **Redis:** 46 jobs (6.72%)

---

## 6. Role-Wise Skill Demand (12 Target Occupations — Recent 12M PK Tech, $N=685$)

![Skills by Role](figures/skills_by_role.png)

### 1. Software Engineer ($N=70$)
* JavaScript (55.7%, 39 jobs)
* Git (55.7%, 39 jobs)
* SQL (47.1%, 33 jobs)
* AWS (45.7%, 32 jobs)
* Python (40.0%, 28 jobs)
* React (40.0%, 28 jobs)
* CI/CD (38.6%, 27 jobs)
* Microsoft Azure (38.6%, 27 jobs)

### 2. Full Stack Developer ($N=32$)
* JavaScript (71.9%, 23 jobs)
* React (68.8%, 22 jobs)
* Python (59.4%, 19 jobs)
* PostgreSQL (56.2%, 18 jobs)
* CI/CD (46.9%, 15 jobs)
* TypeScript (43.8%, 14 jobs)
* SQL (40.6%, 13 jobs)
* Next.js (37.5%, 12 jobs)

### 3. AI Engineer ($N=30$)
* Python (93.3%, 28 jobs)
* Large Language Models (80.0%, 24 jobs)
* Machine Learning (50.0%, 15 jobs)
* Microsoft Azure (50.0%, 15 jobs)
* AWS (46.7%, 14 jobs)
* SQL (43.3%, 13 jobs)
* PyTorch (40.0%, 12 jobs)
* CI/CD (33.3%, 10 jobs)

### 4. Cybersecurity Engineer ($N=25$)
* AWS (44.0%, 11 jobs)
* Google Cloud Platform (28.0%, 7 jobs)
* Microsoft Azure (28.0%, 7 jobs)
* Linux (16.0%, 4 jobs)
* CI/CD (8.0%, 2 jobs)
* SQL (8.0%, 2 jobs)
* Git (8.0%, 2 jobs)
* Docker (4.0%, 1 job)

### 5. DevOps Engineer ($N=20$)
* CI/CD (100.0%, 20 jobs)
* Terraform (85.0%, 17 jobs)
* Kubernetes (75.0%, 15 jobs)
* Linux (75.0%, 15 jobs)
* Python (75.0%, 15 jobs)
* AWS (70.0%, 14 jobs)
* Docker (70.0%, 14 jobs)
* Git (70.0%, 14 jobs)

### 6. Data Analyst ($N=15$)
* SQL (73.3%, 11 jobs)
* Excel (66.7%, 10 jobs)
* Python (46.7%, 7 jobs)
* Tableau (46.7%, 7 jobs)
* R (40.0%, 6 jobs)
* Power BI (40.0%, 6 jobs)
* Apache Spark (13.3%, 2 jobs)
* BigQuery (13.3%, 2 jobs)

### 7. Python Developer ($N=14$)
* Python (100.0%, 14 jobs)
* FastAPI (71.4%, 10 jobs)
* Django (64.3%, 9 jobs)
* Microsoft Azure (64.3%, 9 jobs)
* Docker (57.1%, 8 jobs)
* PostgreSQL (50.0%, 7 jobs)
* SQL (50.0%, 7 jobs)
* CI/CD (50.0%, 7 jobs)

### 8. Backend Developer ($N=12$)
* Python (58.3%, 7 jobs)
* PostgreSQL (50.0%, 6 jobs)
* AWS (50.0%, 6 jobs)
* Git (50.0%, 6 jobs)
* Apache Kafka (33.3%, 4 jobs)
* CI/CD (33.3%, 4 jobs)
* JavaScript (33.3%, 4 jobs)
* Large Language Models (33.3%, 4 jobs)

### 9. Machine Learning Engineer ($N=12$)
* Machine Learning (100.0%, 12 jobs)
* Python (83.3%, 10 jobs)
* Large Language Models (75.0%, 9 jobs)
* Scikit-Learn (66.7%, 8 jobs)
* CI/CD (66.7%, 8 jobs)
* PyTorch (58.3%, 7 jobs)
* AWS (58.3%, 7 jobs)
* Pandas (50.0%, 6 jobs)

### 10. Frontend Developer ($N=11$)
* JavaScript (81.8%, 9 jobs)
* React (63.6%, 7 jobs)
* TypeScript (63.6%, 7 jobs)
* Git (45.5%, 5 jobs)
* CSS (36.4%, 4 jobs)
* HTML (27.3%, 3 jobs)
* Angular (27.3%, 3 jobs)
* Next.js (18.2%, 2 jobs)

### 11. Data Scientist ($N=9$)
* Machine Learning (88.9%, 8 jobs)
* Python (88.9%, 8 jobs)
* SQL (77.8%, 7 jobs)
* PyTorch (55.6%, 5 jobs)
* TensorFlow (55.6%, 5 jobs)
* Deep Learning (55.6%, 5 jobs)
* Pandas (44.4%, 4 jobs)
* Scikit-Learn (44.4%, 4 jobs)

### 12. Cloud Engineer ($N=7$)
* AWS (85.7%, 6 jobs)
* Terraform (85.7%, 6 jobs)
* Microsoft Azure (85.7%, 6 jobs)
* CI/CD (71.4%, 5 jobs)
* Kubernetes (71.4%, 5 jobs)
* Linux (71.4%, 5 jobs)
* Docker (57.1%, 4 jobs)
* Git (57.1%, 4 jobs)

---

## 7. Salary & Compensation Benchmarks

![Salary Distribution](figures/salary_distribution.png)
![Salary by Experience](figures/salary_by_experience.png)

### Summary Statistics of Disclosed Compensation (Indicative Only — Currency-Separated)

Pay periods are normalized to monthly equivalents (`hourly × 176` assuming `8 hrs/day × 22 working days/month`; `annual ÷ 12`). Where PKR-equivalent conversions are shown, the fixed **State Bank of Pakistan (SBP) Mark-to-Market / Ready Reference** snapshot for **20 November 2026** is used (`1 USD = 276.5132 PKR`, `1 EUR = 295.00 PKR`). All salary findings are **indicative only** due to low disclosure and selection bias.

| Compensation Cohort | Sample Size ($N$) | Min | Q1 (25th) | Median (50th) | Q3 (75th) | Max | IQR |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **PK Tech: Native PKR (Monthly)** | **7** | PKR 70,000 | PKR 115,000 | **PKR 150,000** | PKR 275,000 | PKR 450,000 | PKR 160,000 |
| **PK Tech: Normalized USD (Monthly)** | **4** *(low N)* | \$92 | \$473 | **\$1,300** | \$3,167 | \$6,667 | \$2,694 |
| **All Dedup: Native PKR (Monthly)** | **38** | PKR 50 | PKR 50,000 | **PKR 70,000** | PKR 150,000 | PKR 2,922,000 | PKR 100,000 |
| **All Dedup: Normalized USD (Monthly)** | **113** *(70 hr)* | \$58 | \$880 | **\$1,056** | \$1,760 | \$50,000 | \$880 |
| **All Dedup: EUR (Separate)** | **1** | €300 | €300 | **€300** | €300 | €300 | €0 |

### Key Compensation Findings & Caveats:
* **Currency Separation:** In Confirmed Pakistan Tech (`N=848`), `7` native PKR roles have a median of **PKR 150,000/month**, while `4` normalized USD roles have a median of **\$1,300/month** (low sample). Across all deduplicated postings (`N=3,707`), `38` native PKR roles have a median of **PKR 70,000/month** and `113` normalized USD roles (70 hourly) have a median of **\$1,056/month**; `1` EUR role is **€300/month**.
* **Low & High Outliers:** In the full deduplicated cohort, extreme entries (e.g., PKR 50.0 micro-tasks up to \$50,000 USD/month executive roles) reflect non-standard postings.
* **Small-Sample Subgroup Caution:** Experience and city salary breakdowns within Confirmed Pakistan Tech (`N=11`) are omitted due to insufficient cell sample sizes (`N < 5`).

---

## 8. Geographic Hub Concentration

![Top Hiring Cities](figures/top_hiring_cities.png)

Pakistan's tech hiring is overwhelmingly concentrated within three metropolitan clusters, accounting for **93.3%** of all 2,684 localized vacancies:

| Ranking | Pakistani City | Province / Region | Listings Count | % of Mapped Cities | % of All Postings |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Lahore** | Punjab | **1,027** | **38.26%** | 22.87% |
| **2** | **Karachi** | Sindh | **868** | **32.34%** | 19.33% |
| **3** | **Islamabad** | Federal Capital | **609** | **22.69%** | 13.56% |
| **4** | **Rawalpindi** | Punjab | 38 | 1.42% | 0.85% |
| **5** | **Peshawar** | Khyber Pakhtunkhwa | 26 | 0.97% | 0.58% |
| **6** | **Multan** | Punjab | 24 | 0.89% | 0.53% |
| **7** | **Faisalabad** | Punjab | 20 | 0.75% | 0.45% |
| **8** | **Sukkur** | Sindh | 13 | 0.48% | 0.29% |
| **9** | **Hyderabad** | Sindh | 13 | 0.48% | 0.29% |
| **10**| **Larkana** | Sindh | 10 | 0.37% | 0.22% |
| **11**| **Sialkot** | Punjab | 9 | 0.34% | 0.20% |
| **12**| **Quetta** | Balochistan | 5 | 0.19% | 0.11% |
| - | **Other / Secondary**| Pakistan | 24 | 0.89% | 0.53% |

* **Foreign Listings Partition:** 453 postings (10.1% of the overall dataset) originated from foreign operating entities (United States, United Kingdom, UAE, Saudi Arabia, Germany) recruiting Pakistani talent for cross-border engineering teams.

---

## 9. Workplace Arrangement Distribution

![Workplace Distribution](figures/workplace_distribution.png)

Among the **2,309 job postings** containing explicit workplace classifications:

* **Remote:** **1,197 postings (51.84% of known arrangements)** — Demonstrates that remote work has transitioned from an emergency arrangement into the primary recruiting model for Pakistani technology professionals.
* **On-site:** **943 postings (40.84% of known arrangements)** — Predominantly traditional manufacturing, banking, and physical operations roles.
* **Hybrid:** **169 postings (7.32% of known arrangements)** — Concentrated in multinational offices and established domestic banks in Karachi and Islamabad.
* **Unspecified Workplace:** **2,182 postings (48.59% of total dataset)** — Preserved as unknown.

---

## 10. Technical Skill Co-occurrence Network

![Co-occurrence Heatmap](figures/skill_cooccurrence_heatmap.png)

Analyzing pairs of skills required within the same job posting reveals critical synergistic tech stacks:

| Rank | Skill Pair Combination | Shared Postings | Jaccard Similarity | Dominant Stack Architecture |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **AWS + Microsoft Azure** | 226 | 0.412 | Multi-Cloud Enterprise Infrastructure |
| **2** | **AWS + Python** | 205 | 0.330 | Cloud-Native Backend & Data Engineering |
| **3** | **AWS + CI/CD** | 197 | 0.351 | Modern Automated Cloud Deployments |
| **4** | **Python + SQL** | 192 | 0.265 | Data Analytics, Science & Data Pipelines |
| **5** | **CI/CD + Git** | 189 | 0.328 | Core DevOps & Source Code Automation |
| **6** | **CI/CD + Python** | 180 | 0.281 | Automated Testing & Infrastructure as Code |
| **7** | **AWS + Google Cloud Platform** | 178 | 0.428 | Multi-Cloud Architecture |
| **8** | **CI/CD + Microsoft Azure** | 174 | 0.293 | Enterprise Azure DevOps Pipelines |
| **9** | **Git + JavaScript** | 171 | 0.298 | Modern Web & Frontend Versioning |
| **10**| **Microsoft Azure + Python** | 167 | 0.250 | Enterprise Cloud Analytics & Serverless |
| **11**| **Docker + Python** | 166 | 0.347 | Microservices & Model Containerization |
| **12**| **JavaScript + React** | 166 | 0.411 | Standard Frontend Web Stack |
| **13**| **Docker + Kubernetes** | 154 | **0.542** | High-Coupling Orchestration Cluster |

---

## 11. Actionable Recommendations for Pakistani Students and Job Seekers

### 1. For Aspiring Software Engineers
* **Pair Languages with DevOps:** Knowing Python or JavaScript alone is no longer sufficient. Over 60% of software engineer postings require **Git**, **CI/CD**, and **Docker**.
* **Target Multi-Cloud Proficiency:** Microsoft Azure (263 recent PK tech jobs) and AWS (230 jobs) lead the cloud market alongside CI/CD (253 jobs). Focus on acquiring foundational certifications in either ecosystem.

### 2. For Data Analysts and Aspiring Data Scientists
* **Master the Core Stack:** SQL (252 recent PK tech jobs) and Python (268 jobs) form the core technical foundation for data engineering and analytics roles.
* **Python for Transitioning:** Python appears in 46.7% of Data Analyst roles (`N=15`) and 88.9% of Data Scientist roles (`N=9`), making it the primary bridge between analytics and ML modeling.

### 3. For AI and Machine Learning Engineers
* **Adopt LLMs and Generative AI Frameworks:** Postings requiring **Large Language Models (134 recent PK tech jobs)** appear alongside traditional Machine Learning (113 jobs). Experience with LangChain, LlamaIndex, and API orchestration is a key differentiator.
* **Production ML & Cloud:** 66.7% of Machine Learning Engineer roles (`N=12`) require CI/CD and Scikit-Learn, and 58.3% require PyTorch and AWS.

### 4. For Remote Job Seekers
* **Target US-Dollar & Export-Oriented Roles:** Remote international contracts (normalized USD median **\$1,056/month** across `N=113` deduplicated postings, indicative only) often pay substantially above local PKR-quoted roles (`N=38` median **PKR 70,000/month**, or `N=7` PK Tech median **PKR 150,000/month**), though sample sizes are small and subject to selection bias.

---

## 12. Verification & Reproducibility Notice

All metrics presented in this document were computed deterministically via automated pipeline modules:
* Skills & Roles: `src/analysis/skills_analysis.py`
* Salary Benchmarks: `src/analysis/salary_analysis.py`
* Geographic Clustering: `src/analysis/location_analysis.py`
* Workplace Distributions: `src/analysis/workplace_analysis.py`
* Skill Co-occurrences: `src/analysis/cooccurrence.py`
* Visualizations: `src/analysis/generate_visualizations.py`
* Verified Offline Unit Tests: `tests/test_analysis_pipeline.py` (109 passing tests).

# HireTrends — Streamlit Community Cloud Deployment Guide
## Step-by-Step Instructions for Public Production Hosting

**Project:** HireTrends — Pakistan Tech Job Market Intelligence  
**Repository:** [https://github.com/Awaisbacha55/hiretrends-pakistan-job-market](https://github.com/Awaisbacha55/hiretrends-pakistan-job-market)  
**Main Dashboard Path:** `dashboard/app.py`  
**Target Platform:** [Streamlit Community Cloud](https://share.streamlit.io/)  

---

## 1. Overview & Architecture Readiness

HireTrends has been built and audited to ensure seamless, zero-configuration deployment to **Streamlit Community Cloud**:
- **Zero API Key Requirement in Production:** The interactive dashboard operates on pre-processed, high-integrity data stored in `data/processed/jobs_cleaned.csv` (~2.2 MB). The live web application requires **no external API secrets** or database servers to run.
- **Privacy & Copyright Compliance:** Full-text employer job descriptions are strictly excluded from the processed dataset, keeping the repository well within GitHub and Streamlit Cloud file size thresholds.
- **Multipage Architecture:** Uses native Streamlit multipage navigation (`st.Page` / `st.navigation`) configured in `dashboard/app.py`.
- **Pre-configured Theme:** The `.streamlit/config.toml` file enforces a clean SaaS light aesthetic, responsive layouts, and proper font stacks.

---

## 2. Prerequisites

Before deploying, ensure you have:
1. A **GitHub account** containing the `hiretrends-pakistan-job-market` repository (branch: `main`).
2. A free **Streamlit Community Cloud** account at [share.streamlit.io](https://share.streamlit.io/).
3. Streamlit Cloud connected to your GitHub account with read permissions for your repository.

---

## 3. Step-by-Step Deployment Walkthrough

### Step 1: Sign in to Streamlit Community Cloud
1. Open your browser and navigate to [https://share.streamlit.io/](https://share.streamlit.io/).
2. Click **"Sign in with GitHub"** and authenticate.

### Step 2: Create a New App
1. From the Streamlit Community Cloud workspace, click the **"Create app"** (or **"New app"**) button located in the top-right corner.
2. Select **"Yup, I have an existing app"** (or choose repository directly).

### Step 3: Configure App Deployment Parameters
Fill in the deployment form with the following exact settings:

| Field | Configuration Value | Notes |
| :--- | :--- | :--- |
| **Repository** | `Awaisbacha55/hiretrends-pakistan-job-market` | Select your repository |
| **Branch** | `main` | Default production branch |
| **Main file path** | `dashboard/app.py` | Entry point of multipage dashboard |
| **App URL (optional)** | `hiretrends-pakistan.streamlit.app` | Custom subdomain (if available) |

### Step 4: Advanced Settings (Python Version)
1. Click **"Advanced settings..."** before deploying.
2. Under **Python version**, select **`3.12`** (or `3.11`).
3. Under **Secrets**:
   - *Leave empty.* The production dashboard reads from the pre-processed dataset committed at `data/processed/jobs_cleaned.csv`.
   - *(Optional)* If you plan to trigger automated live Headcount API refreshes from inside the cloud container in the future, you may add:
     ```toml
     HEADCOUNTLABS_API_KEY = "your_private_api_key_here"
     ```
4. Click **"Save"**.

### Step 5: Deploy
1. Click the blue **"Deploy!"** button.
2. Streamlit Cloud will automatically:
   - Provision a secure Linux container.
   - Clone your `main` branch.
   - Read `requirements.txt` and install all pinned dependencies (`pandas`, `numpy`, `plotly`, `streamlit`).
   - Launch `dashboard/app.py`.
3. In approximately 1–2 minutes, your live URL will open!

---

## 4. Post-Deployment Verification Checklist

Once the dashboard is live, perform this 8-point smoke test:

- [ ] **Market Overview:** Verify KPI cards show Total Postings ($4,491$), Confirmed Tech Roles ($1,075$), Disclosed Salaries ($174$), and Localized Cities ($2,684$).
- [ ] **Skills Explorer:** Check that the top 20 skills bar chart loads. Test search for "Docker". Click **"Download Skills Demand Table (CSV)"**.
- [ ] **Role Explorer:** Select "Full Stack Engineer" and confirm skill and location distributions update instantly.
- [ ] **Salary Insights:** Verify the box plots and quartile benchmarks table render properly. Test CSV download.
- [ ] **Location Analysis:** Confirm the Big Three distribution chart (Lahore 38%, Karachi 32%, Islamabad 23%) renders with tooltip interactions.
- [ ] **Workplace Analysis:** Verify the remote work percentage ($51.8\%$) and unspecified disclaimer card appear.
- [ ] **Skill Co-occurrence:** Verify the 12x12 heatmap loads cleanly.
- [ ] **Data & Methodology:** Verify the reconciliation balance equation and ODbL attribution notice are displayed.

---

## 5. Alternative: Local Docker Deployment

If you wish to containerize and run the dashboard locally or on a private server:

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t hiretrends:latest .
docker run -p 8501:8501 hiretrends:latest
```
Open `http://localhost:8501` in your browser.

---

## 6. Updating the Live Application

Streamlit Community Cloud is continuously integrated with GitHub:
1. Every time you push a new commit to the `main` branch:
   ```bash
   git push origin main
   ```
2. Streamlit Community Cloud will automatically detect the push and reload the application with zero manual intervention.

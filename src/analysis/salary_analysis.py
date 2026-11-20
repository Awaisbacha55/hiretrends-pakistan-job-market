"""HireTrends Salary and Compensation Analysis Engine.

Analyzes disclosed remuneration data, segregating native PKR and foreign currencies,
computing robust non-parametric summary statistics (median, IQR, quartiles),
investigating outliers, and slicing by experience and geography.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def compute_series_stats(series: pd.Series) -> Dict[str, Any]:
    """Compute parametric and robust non-parametric statistics for a numeric Series."""
    clean = series.dropna().astype(float)
    n = len(clean)
    if n == 0:
        return {
            "sample_size": 0,
            "min": None,
            "q1": None,
            "median": None,
            "mean": None,
            "q3": None,
            "max": None,
            "std": None,
            "iqr": None,
        }

    q1 = float(np.percentile(clean, 25))
    median = float(np.percentile(clean, 50))
    q3 = float(np.percentile(clean, 75))
    iqr = q3 - q1

    return {
        "sample_size": n,
        "min": round(float(clean.min()), 2),
        "q1": round(q1, 2),
        "median": round(median, 2),
        "mean": round(float(clean.mean()), 2),
        "q3": round(q3, 2),
        "max": round(float(clean.max()), 2),
        "std": round(float(clean.std()), 2) if n > 1 else 0.0,
        "iqr": round(iqr, 2),
    }


def analyze_salary_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform comprehensive compensation benchmarking across disclosed salary records.

    Note: Less than 4% of job postings disclose compensation. All results must be
    interpreted within their explicit sample size boundaries.
    """
    total_listings = len(df)
    salary_df = df[df["salary_min_pkr"].notna()].copy()
    disclosed_count = len(salary_df)

    if disclosed_count == 0:
        return {
            "total_listings": total_listings,
            "disclosed_count": 0,
            "disclosure_rate_pct": 0.0,
            "status": "NO_DISCLOSED_SALARIES",
        }

    # 1. Currency Breakdown
    currency_counts = salary_df["salary_currency"].value_counts().to_dict()

    # 2. Native PKR Postings Only
    pkr_df = salary_df[salary_df["salary_currency"] == "PKR"]
    pkr_min_stats = compute_series_stats(pkr_df["salary_min_original"])
    pkr_max_stats = compute_series_stats(pkr_df["salary_max_original"])

    # 3. Foreign Currency Postings (predominantly USD)
    foreign_df = salary_df[salary_df["salary_is_converted"] == True]
    usd_df = salary_df[salary_df["salary_currency"] == "USD"]
    usd_original_stats = compute_series_stats(usd_df["salary_min_original"])

    # 4. Overall Standardized Monthly PKR Postings (Combined)
    overall_min_pkr_stats = compute_series_stats(salary_df["salary_min_pkr"])
    overall_max_pkr_stats = compute_series_stats(salary_df["salary_max_pkr"])

    # 5. Outlier Detection (Suspiciously low or extreme high)
    # Low outliers: < 10,000 PKR / month (likely hourly / micro-tasks / test data)
    low_outliers = salary_df[salary_df["salary_min_pkr"] < 10000][
        ["job_title", "company", "salary_text", "salary_currency", "salary_interval", "salary_min_pkr"]
    ].to_dict(orient="records")

    # High outliers: > 5,000,000 PKR / month (executive / international remote contracts)
    high_outliers = salary_df[salary_df["salary_min_pkr"] > 5000000][
        ["job_title", "company", "salary_text", "salary_currency", "salary_interval", "salary_min_pkr"]
    ].to_dict(orient="records")

    # Trimmed / Inlier statistics (excluding low < 10k and extreme > 5M)
    inliers_df = salary_df[(salary_df["salary_min_pkr"] >= 10000) & (salary_df["salary_min_pkr"] <= 5000000)]
    inlier_pkr_stats = compute_series_stats(inliers_df["salary_min_pkr"])

    # 6. Salary by Experience Band
    exp_brackets = {
        "Entry / Junior (0-1 yrs)": salary_df[salary_df["experience_min_years"] <= 1.0]["salary_min_pkr"],
        "Mid-Level (2-4 yrs)": salary_df[(salary_df["experience_min_years"] >= 2.0) & (salary_df["experience_min_years"] <= 4.0)]["salary_min_pkr"],
        "Senior (5+ yrs)": salary_df[salary_df["experience_min_years"] >= 5.0]["salary_min_pkr"],
        "Unspecified Experience": salary_df[salary_df["experience_min_years"].isna()]["salary_min_pkr"],
    }
    salary_by_exp = {
        bracket: compute_series_stats(series) for bracket, series in exp_brackets.items()
    }

    # 7. Salary by Top Cities / Remote
    city_brackets = {
        "Remote": salary_df[salary_df["workplace_type"] == "remote"]["salary_min_pkr"],
        "Lahore": salary_df[salary_df["normalized_city"] == "Lahore"]["salary_min_pkr"],
        "Karachi": salary_df[salary_df["normalized_city"] == "Karachi"]["salary_min_pkr"],
        "Islamabad": salary_df[salary_df["normalized_city"] == "Islamabad"]["salary_min_pkr"],
        "On-site (All Cities)": salary_df[salary_df["workplace_type"] == "on-site"]["salary_min_pkr"],
        "Hybrid": salary_df[salary_df["workplace_type"] == "hybrid"]["salary_min_pkr"],
    }
    salary_by_city = {
        loc: compute_series_stats(series) for loc, series in city_brackets.items()
    }

    # 8. Interval Breakdown (Monthly vs Annual vs Hourly assumptions)
    interval_counts = salary_df["salary_interval"].fillna("unspecified").value_counts().to_dict()

    return {
        "total_listings": total_listings,
        "disclosed_count": disclosed_count,
        "disclosure_rate_pct": round(disclosed_count / total_listings * 100, 2),
        "currency_distribution": currency_counts,
        "interval_distribution": interval_counts,
        "native_pkr_stats": {
            "min_salary": pkr_min_stats,
            "max_salary": pkr_max_stats,
        },
        "usd_original_stats": usd_original_stats,
        "overall_monthly_pkr": {
            "min_salary": overall_min_pkr_stats,
            "max_salary": overall_max_pkr_stats,
        },
        "inliers_monthly_pkr": inlier_pkr_stats,
        "outlier_analysis": {
            "low_outliers_count": len(low_outliers),
            "high_outliers_count": len(high_outliers),
            "sample_low_outliers": low_outliers[:5],
            "sample_high_outliers": high_outliers[:5],
        },
        "salary_by_experience": salary_by_exp,
        "salary_by_location": salary_by_city,
        "methodological_notes": {
            "exchange_rate_source": "State Bank of Pakistan official reference rates (Nov 20, 2026)",
            "conversion_rates": {"USD": 278.50, "EUR": 295.00, "GBP": 352.00, "AED": 75.80},
            "annual_normalization": "Annual salaries divided by 12.0",
            "hourly_assumption": "Full-time hourly rates converted using 176 monthly hours (40 hrs/wk * 4.4 wks)",
            "representativeness_warning": "Salary disclosures represent 3.87% of all postings, skewed heavily towards remote US-dollar contracts.",
        },
    }

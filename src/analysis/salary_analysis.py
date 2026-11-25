"""HireTrends Salary and Compensation Analysis Engine.

Analyzes disclosed remuneration data, strictly separating native PKR, normalized
monthly USD, and EUR compensation, computing robust non-parametric summary
statistics (median, IQR, quartiles), and enforcing small-sample disclosures.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

MIN_RELIABLE_SAMPLE_SIZE = 5  # Threshold below which subgroup medians are flagged as low-sample
STANDARD_MONTHLY_HOURS = 176.0  # 8 hours/day * 22 working days/month
USD_TO_PKR_RATE = 276.5132  # SBP Mark-to-Market / Ready Reference (20 Nov 2026)


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
        "is_sufficient_sample": n >= MIN_RELIABLE_SAMPLE_SIZE,
        "min": round(float(clean.min()), 2),
        "q1": round(q1, 2),
        "median": round(median, 2),
        "mean": round(float(clean.mean()), 2),
        "q3": round(q3, 2),
        "max": round(float(clean.max()), 2),
        "std": round(float(clean.std()), 2) if n > 1 else 0.0,
        "iqr": round(iqr, 2),
    }


def _normalize_original_to_monthly(df: pd.DataFrame, col: str = "salary_min_original") -> pd.Series:
    """Normalize original-currency salary amounts into monthly equivalents.

    - hour -> amount * 176.0 (8 hrs/day * 22 working days/month)
    - year -> amount / 12.0
    - month -> amount * 1.0
    """
    if len(df) == 0 or col not in df.columns:
        return pd.Series(dtype=float)

    vals = df[col].astype(float)
    intervals = df["salary_interval"].fillna("month").astype(str).str.lower()
    factors = np.where(
        intervals == "hour",
        STANDARD_MONTHLY_HOURS,
        np.where(intervals == "year", 1.0 / 12.0, 1.0),
    )
    return vals * factors


def analyze_salary_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform compensation benchmarking with strict currency and period separation.

    Note: Disclosed salaries represent a small, self-selected subset (indicative only).
    Native PKR and normalized monthly USD are reported separately; any combined
    PKR-equivalent view is explicitly labeled as converted and indicative only.
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

    # 1. Currency & Interval Breakdown
    currency_counts = salary_df["salary_currency"].value_counts().to_dict()
    interval_counts = salary_df["salary_interval"].fillna("unspecified").value_counts().to_dict()

    # 2. Native PKR Postings Only (normalized to monthly PKR: annual / 12)
    pkr_df = salary_df[salary_df["salary_currency"] == "PKR"].copy()
    pkr_min_monthly = _normalize_original_to_monthly(pkr_df, "salary_min_original")
    pkr_max_monthly = _normalize_original_to_monthly(pkr_df, "salary_max_original")
    pkr_min_stats = compute_series_stats(pkr_min_monthly)
    pkr_max_stats = compute_series_stats(pkr_max_monthly)

    # 3. USD Postings Only (normalized to monthly-equivalent USD: hourly * 176, annual / 12)
    usd_df = salary_df[salary_df["salary_currency"] == "USD"].copy()
    usd_min_monthly = _normalize_original_to_monthly(usd_df, "salary_min_original")
    usd_monthly_stats = compute_series_stats(usd_min_monthly)

    # 4. EUR Postings Only (reported separately)
    eur_df = salary_df[salary_df["salary_currency"] == "EUR"].copy()
    eur_min_monthly = _normalize_original_to_monthly(eur_df, "salary_min_original")
    eur_monthly_stats = compute_series_stats(eur_min_monthly)
    eur_converted_pkr_stats = compute_series_stats(eur_df["salary_min_pkr"])

    # 5. Converted PKR Equivalent (Combined — Indicative Only)
    overall_min_pkr_stats = compute_series_stats(salary_df["salary_min_pkr"])
    overall_max_pkr_stats = compute_series_stats(salary_df["salary_max_pkr"])

    # 6. Outlier Detection (Suspiciously low < 10k or extreme > 5M PKR/mo equivalent)
    low_outliers = salary_df[salary_df["salary_min_pkr"] < 10000][
        ["job_title", "company", "salary_text", "salary_currency", "salary_interval", "salary_min_pkr"]
    ].to_dict(orient="records")

    high_outliers = salary_df[salary_df["salary_min_pkr"] > 5000000][
        ["job_title", "company", "salary_text", "salary_currency", "salary_interval", "salary_min_pkr"]
    ].to_dict(orient="records")

    inliers_df = salary_df[(salary_df["salary_min_pkr"] >= 10000) & (salary_df["salary_min_pkr"] <= 5000000)]
    inlier_pkr_stats = compute_series_stats(inliers_df["salary_min_pkr"])

    # 7. Currency-Separated Breakdowns by Experience & Location
    def _exp_masks(sub: pd.DataFrame) -> Dict[str, pd.Series]:
        return {
            "Entry / Junior (0-1 yrs)": sub["experience_min_years"] <= 1.0,
            "Mid-Level (2-4 yrs)": (sub["experience_min_years"] >= 2.0) & (sub["experience_min_years"] <= 4.0),
            "Senior (5+ yrs)": sub["experience_min_years"] >= 5.0,
            "Unspecified Experience": sub["experience_min_years"].isna(),
        }

    salary_by_exp: Dict[str, Dict[str, Any]] = {}
    pkr_masks = _exp_masks(pkr_df)
    usd_masks = _exp_masks(usd_df)
    for bracket in pkr_masks:
        pkr_b = _normalize_original_to_monthly(pkr_df[pkr_masks[bracket]], "salary_min_original")
        usd_b = _normalize_original_to_monthly(usd_df[usd_masks[bracket]], "salary_min_original")
        comb_b = salary_df[_exp_masks(salary_df)[bracket]]["salary_min_pkr"]
        stats_comb = compute_series_stats(comb_b)
        stats_comb["native_pkr"] = compute_series_stats(pkr_b)
        stats_comb["usd_monthly"] = compute_series_stats(usd_b)
        salary_by_exp[bracket] = stats_comb

    def _loc_masks(sub: pd.DataFrame) -> Dict[str, pd.Series]:
        return {
            "Remote": sub["workplace_type"] == "remote",
            "Lahore": sub["normalized_city"] == "Lahore",
            "Karachi": sub["normalized_city"] == "Karachi",
            "Islamabad": sub["normalized_city"] == "Islamabad",
            "On-site (All Cities)": sub["workplace_type"] == "on-site",
            "Hybrid": sub["workplace_type"] == "hybrid",
        }

    salary_by_city: Dict[str, Dict[str, Any]] = {}
    pkr_lmasks = _loc_masks(pkr_df)
    usd_lmasks = _loc_masks(usd_df)
    for loc_name in pkr_lmasks:
        pkr_l = _normalize_original_to_monthly(pkr_df[pkr_lmasks[loc_name]], "salary_min_original")
        usd_l = _normalize_original_to_monthly(usd_df[usd_lmasks[loc_name]], "salary_min_original")
        comb_l = salary_df[_loc_masks(salary_df)[loc_name]]["salary_min_pkr"]
        stats_comb = compute_series_stats(comb_l)
        stats_comb["native_pkr"] = compute_series_stats(pkr_l)
        stats_comb["usd_monthly"] = compute_series_stats(usd_l)
        salary_by_city[loc_name] = stats_comb

    disclosure_rate = round(disclosed_count / max(total_listings, 1) * 100, 2)

    return {
        "total_listings": total_listings,
        "disclosed_count": disclosed_count,
        "disclosure_rate_pct": disclosure_rate,
        "indicative_only": True,
        "min_reliable_sample_size": MIN_RELIABLE_SAMPLE_SIZE,
        "currency_distribution": currency_counts,
        "interval_distribution": interval_counts,
        "native_pkr_stats": {
            "min_salary": pkr_min_stats,
            "max_salary": pkr_max_stats,
        },
        "usd_original_stats": usd_monthly_stats,
        "usd_monthly_stats": usd_monthly_stats,
        "eur_monthly_stats": eur_monthly_stats,
        "eur_converted_pkr_stats": eur_converted_pkr_stats,
        "overall_monthly_pkr": {
            "label": "Converted PKR Equivalent — Indicative Only",
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
            "exchange_rate_source": "State Bank of Pakistan (SBP) Mark-to-Market / Ready Reference (20 November 2026)",
            "exchange_rate_date": "2026-11-20",
            "conversion_rates": {"USD": USD_TO_PKR_RATE, "EUR": 295.00, "GBP": 352.00, "AED": 75.80},
            "annual_normalization": "Annual salaries divided by 12.0",
            "hourly_assumption": "Hourly rates converted to monthly equivalents assuming 8 hours/day × 22 working days/month = 176 hours/month (analytical estimate, not guaranteed earnings)",
            "indicative_only_notice": (
                f"Salary findings are indicative only ({disclosure_rate}% disclosure rate; N={disclosed_count}/{total_listings}) "
                "and are subject to selection bias."
            ),
        },
    }

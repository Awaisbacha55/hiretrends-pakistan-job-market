"""HireTrends Dashboard — Salary Insights Page.

Analyzes disclosed remuneration data, isolating native PKR postings from
foreign-currency remote contracts, exploring experience tiers and geographic variances.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.components import (
    render_attribution_footer,
    render_empty_state,
    render_header,
    render_kpi_card,
    render_sidebar_filters,
)
from dashboard.data_loader import format_number, format_pct, format_pkr, load_clean_data
from src.analysis.salary_analysis import analyze_salary_data, compute_series_stats

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

render_header("Salary Insights", "Empirical compensation benchmarks, currency breakdowns, and experience scaling")

# Disclosed salary sub-cohort
sal_df = df[df["has_salary"] == True].copy()
disclosed_count = len(sal_df)

if disclosed_count == 0:
    render_empty_state("No postings in your current filter selection disclose explicit compensation figures.")
    render_attribution_footer()
    st.stop()

# 2. Critical Methodological Caution
st.warning(
    "⚠️ **Important Compensation Methodological Note:** "
    f"Only **{disclosed_count} postings ({disclosed_count/len(df)*100:.1f}%)** disclose explicit compensation in the active selection. "
    "Over 75% of disclosed salaries are international remote roles quoted in US Dollars (converted at SBP rate USD = PKR 278.50). "
    "Do NOT assume these figures represent the domestic wage standard for typical on-site Pakistani firms."
)

# 3. KPI Cards
sal_analysis = analyze_salary_data(sal_df)
overall_stats = sal_analysis["overall_monthly_pkr"]["min_salary"]
native_pkr_stats = sal_analysis["native_pkr_stats"]["min_salary"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Disclosed Postings", format_number(disclosed_count), delta=f"{disclosed_count/len(df)*100:.1f}% disclosure rate", help_text="Total roles stating salary", color_accent="#2563eb")
with col2:
    render_kpi_card("Overall Median Pay", format_pkr(overall_stats["median"]), delta=f"IQR: {format_pkr(overall_stats['iqr'], compact=True)}", help_text="Monthly PKR equivalent (All)", color_accent="#059669")
with col3:
    render_kpi_card("Domestic PKR Median", format_pkr(native_pkr_stats["median"]), delta=f"N={native_pkr_stats['sample_size']} native PKR jobs", help_text="Pure PKR quoted openings", color_accent="#d97706")
with col4:
    usd_stats = sal_analysis.get("usd_original_stats", {})
    usd_median = f"${usd_stats.get('median', 0):,.0f}" if usd_stats.get("median") else "N/A"
    render_kpi_card("USD Remote Median", usd_median, delta=f"N={usd_stats.get('sample_size', 0)} USD jobs", help_text="International remote postings", color_accent="#7c3aed")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 4. Currency Breakdown & Log Distribution
col_dist, col_curr = st.columns([1.2, 0.8])

with col_dist:
    st.subheader("📊 Compensation Distribution (PKR Equivalent)")
    # Trim extreme outliers for clean visualization
    inliers = sal_df[(sal_df["salary_min_pkr"] >= 20000) & (sal_df["salary_min_pkr"] <= 3000000)]
    fig_hist = px.histogram(
        inliers,
        x="salary_min_pkr",
        nbins=25,
        color="salary_currency",
        title=f"Monthly PKR Compensation Distribution (20k–3.0M PKR, N={len(inliers)})",
        labels={"salary_min_pkr": "Monthly Salary (PKR)", "salary_currency": "Currency"},
        color_discrete_map={"PKR": "#d97706", "USD": "#2563eb", "EUR": "#059669"},
    )
    fig_hist.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20))
    st.plotly_chart(fig_hist, use_container_width=True)

with col_curr:
    st.subheader("💵 Quoted Currency Comparison")
    fig_box = px.box(
        sal_df,
        x="salary_currency",
        y="salary_min_pkr",
        color="salary_currency",
        log_y=True,
        title="Compensation by Quoted Currency (Log Scale)",
        labels={"salary_min_pkr": "Monthly PKR Equivalent (Log Scale)", "salary_currency": "Currency"},
        color_discrete_map={"PKR": "#d97706", "USD": "#2563eb", "EUR": "#059669"},
    )
    fig_box.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 5. Salary by Experience Tier & City
col_exp_sal, col_city_sal = st.columns([1, 1])

with col_exp_sal:
    st.subheader("🎓 Monthly Salary by Experience Level")
    exp_sal_df = sal_df[sal_df["experience_bracket"] != "Unspecified"]
    if len(exp_sal_df) > 0:
        fig_exp_box = px.box(
            exp_sal_df,
            x="experience_bracket",
            y="salary_min_pkr",
            color="experience_bracket",
            category_orders={"experience_bracket": ["Entry / Junior (0-1 yrs)", "Mid-Level (2-4 yrs)", "Senior (5+ yrs)"]},
            title=f"Salary Scaling by Experience Tier (N={len(exp_sal_df)})",
            labels={"salary_min_pkr": "Monthly PKR", "experience_bracket": "Level"},
        )
        fig_exp_box.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_exp_box, use_container_width=True)
    else:
        st.info("Insufficient experience tags with disclosed compensation.")

with col_city_sal:
    st.subheader("📍 Monthly Salary by Location / Remote")
    loc_sal_df = sal_df[sal_df["normalized_city"].isin(["Lahore", "Karachi", "Islamabad"]) | (sal_df["workplace_type"] == "remote")].copy()
    loc_sal_df["Location Group"] = loc_sal_df["normalized_city"]
    loc_sal_df.loc[loc_sal_df["workplace_type"] == "remote", "Location Group"] = "Remote (All)"

    if len(loc_sal_df) > 0:
        fig_loc_box = px.box(
            loc_sal_df,
            x="Location Group",
            y="salary_min_pkr",
            color="Location Group",
            title=f"Compensation by Tech Hub vs. Remote (N={len(loc_sal_df)})",
            labels={"salary_min_pkr": "Monthly PKR", "Location Group": "Location"},
        )
        fig_loc_box.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_loc_box, use_container_width=True)
    else:
        st.info("Insufficient localized salary records.")

# 6. Detailed Non-Parametric Quartile Table
st.subheader("📋 Compensation Quartile Benchmarks")
quartiles_data = [
    {
        "Cohort": "All Disclosed Postings",
        "Sample Size": overall_stats["sample_size"],
        "Min": format_pkr(overall_stats["min"]),
        "Q1 (25th)": format_pkr(overall_stats["q1"]),
        "Median (50th)": format_pkr(overall_stats["median"]),
        "Mean": format_pkr(overall_stats["mean"]),
        "Q3 (75th)": format_pkr(overall_stats["q3"]),
        "Max": format_pkr(overall_stats["max"]),
        "IQR": format_pkr(overall_stats["iqr"], compact=True),
    },
    {
        "Cohort": "Domestic PKR Only",
        "Sample Size": native_pkr_stats["sample_size"],
        "Min": format_pkr(native_pkr_stats["min"]),
        "Q1 (25th)": format_pkr(native_pkr_stats["q1"]),
        "Median (50th)": format_pkr(native_pkr_stats["median"]),
        "Mean": format_pkr(native_pkr_stats["mean"]),
        "Q3 (75th)": format_pkr(native_pkr_stats["q3"]),
        "Max": format_pkr(native_pkr_stats["max"]),
        "IQR": format_pkr(native_pkr_stats["iqr"], compact=True),
    },
]
inliers_stats = sal_analysis.get("inliers_monthly_pkr", {})
if inliers_stats.get("sample_size", 0) > 0:
    quartiles_data.append({
        "Cohort": "Inlier Bracket (20k - 5M PKR)",
        "Sample Size": inliers_stats["sample_size"],
        "Min": format_pkr(inliers_stats["min"]),
        "Q1 (25th)": format_pkr(inliers_stats["q1"]),
        "Median (50th)": format_pkr(inliers_stats["median"]),
        "Mean": format_pkr(inliers_stats["mean"]),
        "Q3 (75th)": format_pkr(inliers_stats["q3"]),
        "Max": format_pkr(inliers_stats["max"]),
        "IQR": format_pkr(inliers_stats["iqr"], compact=True),
    })

q_df = pd.DataFrame(quartiles_data)
st.dataframe(q_df, use_container_width=True, hide_index=True)

render_attribution_footer()

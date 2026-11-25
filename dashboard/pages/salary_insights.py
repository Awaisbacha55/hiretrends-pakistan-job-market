"""HireTrends Dashboard — Salary Insights Page.

Analyzes disclosed remuneration data, isolating native PKR postings from
foreign-currency remote contracts, exploring experience tiers and geographic variances.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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

active_scope = st.session_state.get("filter_dataset_scope", "Confirmed Pakistan Tech")
render_header("Salary Insights (Indicative Only)", f"Currency-separated compensation benchmarks — Scope: {active_scope} (N={len(df):,})")

# Disclosed salary sub-cohort
sal_df = df[df["has_salary"] == True].copy()
disclosed_count = len(sal_df)

if disclosed_count == 0:
    render_empty_state("No postings in your current filter selection disclose explicit compensation figures.")
    render_attribution_footer()
    st.stop()

# 2. Dynamic Methodological Caution & Conversion Disclosure
sal_analysis = analyze_salary_data(df)
curr_dist = sal_analysis.get("currency_distribution", {})
intv_dist = sal_analysis.get("interval_distribution", {})
curr_str = ", ".join(f"{k}: {v}" for k, v in curr_dist.items())
intv_str = ", ".join(f"{k}: {v}" for k, v in intv_dist.items())

st.warning(
    f"⚠️ **Indicative Only — Low Disclosure & Selection Bias (Scope: {active_scope}):** "
    f"Only **{disclosed_count} of {len(df):,} postings ({disclosed_count/max(len(df),1)*100:.2f}%)** disclose salary "
    f"(**Currencies:** {curr_str} | **Pay Periods:** {intv_str}). "
    "These figures are **indicative estimates only** and are **not representative** of the broader Pakistan tech market.\n\n"
    "**Conversion Methodology:** Hourly rates normalized using `hourly × 176` (`8 hrs/day × 22 working days/month`, analytical estimate); "
    "annual salaries normalized using `annual ÷ 12`. PKR-equivalent conversions use the fixed **SBP Mark-to-Market / Ready Reference** rate "
    "for **20 November 2026** (**1 USD = 276.5132 PKR**); actual transaction/remittance rates may differ."
)

# 3. Currency-Separated KPI Cards
native_pkr_stats = sal_analysis["native_pkr_stats"]["min_salary"]
usd_stats = sal_analysis.get("usd_monthly_stats", {})
eur_stats = sal_analysis.get("eur_monthly_stats", {})
overall_stats = sal_analysis["overall_monthly_pkr"]["min_salary"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        "Disclosed Postings",
        f"{format_number(disclosed_count)} / {format_number(len(df))}",
        delta=f"{disclosed_count/max(len(df),1)*100:.2f}% disclosure rate",
        help_text=f"Scope: {active_scope}",
        color_accent="#2563eb",
    )
with col2:
    pkr_n = native_pkr_stats["sample_size"]
    render_kpi_card(
        "Native PKR Median (Monthly)",
        format_pkr(native_pkr_stats["median"]) if pkr_n > 0 else "N/A",
        delta=f"N={pkr_n} native PKR jobs (annual ÷ 12)",
        help_text="Pure PKR postings only (Indicative)",
        color_accent="#d97706",
    )
with col3:
    usd_n = usd_stats.get("sample_size", 0)
    usd_median = f"${usd_stats['median']:,.0f}/mo" if usd_stats.get("median") else "N/A"
    render_kpi_card(
        "Normalized USD Median",
        usd_median,
        delta=f"N={usd_n} USD jobs (hr×176, yr÷12)",
        help_text="Monthly-equivalent USD (Indicative)",
        color_accent="#7c3aed",
    )
with col4:
    eur_n = eur_stats.get("sample_size", 0)
    if eur_n > 0:
        render_kpi_card(
            "Normalized EUR (Separate)",
            f"€{eur_stats['median']:,.0f}/mo",
            delta=f"N={eur_n} EUR job (≈ PKR {sal_analysis['eur_converted_pkr_stats']['median']:,.0f})",
            help_text="Converted at EUR = 295.00 PKR",
            color_accent="#059669",
        )
    else:
        render_kpi_card(
            "Converted PKR Equiv. (All)",
            format_pkr(overall_stats["median"]),
            delta=f"N={overall_stats['sample_size']} ({curr_str}) — Indicative",
            help_text="Combined PKR-equiv. (USD=276.5132)",
            color_accent="#059669",
        )

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
    if len(exp_sal_df) >= 5:
        fig_exp_box = px.box(
            exp_sal_df,
            x="experience_bracket",
            y="salary_min_pkr",
            color="salary_currency",
            category_orders={"experience_bracket": ["Entry / Junior (0-1 yrs)", "Mid-Level (2-4 yrs)", "Senior (5+ yrs)"]},
            title=f"Converted PKR Equiv. by Experience & Currency — Indicative Only (N={len(exp_sal_df)})",
            labels={"salary_min_pkr": "Monthly PKR Equiv. (Indicative)", "experience_bracket": "Level", "salary_currency": "Currency"},
        )
        fig_exp_box.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20))
        st.plotly_chart(fig_exp_box, use_container_width=True)
    else:
        st.info(f"Experience breakdown suppressed/insufficient in current scope (N={len(exp_sal_df)} with experience tags < minimum threshold 5).")

with col_city_sal:
    st.subheader("📍 Monthly Salary by Location / Remote")
    loc_sal_df = sal_df[sal_df["normalized_city"].isin(["Lahore", "Karachi", "Islamabad"]) | (sal_df["workplace_type"] == "remote")].copy()
    loc_sal_df["Location Group"] = loc_sal_df["normalized_city"]
    loc_sal_df.loc[loc_sal_df["workplace_type"] == "remote", "Location Group"] = "Remote (All)"

    if len(loc_sal_df) >= 5:
        fig_loc_box = px.box(
            loc_sal_df,
            x="Location Group",
            y="salary_min_pkr",
            color="salary_currency",
            title=f"Converted PKR Equiv. by Hub vs. Remote — Indicative Only (N={len(loc_sal_df)})",
            labels={"salary_min_pkr": "Monthly PKR Equiv. (Indicative)", "Location Group": "Location", "salary_currency": "Currency"},
        )
        fig_loc_box.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=20))
        st.plotly_chart(fig_loc_box, use_container_width=True)
    else:
        st.info(f"Location breakdown suppressed/insufficient in current scope (N={len(loc_sal_df)} < minimum threshold 5).")

# 6. Detailed Currency-Separated Quartile Table
st.subheader("📋 Currency-Separated Compensation Benchmarks (Indicative Only)")
quartiles_data = []
if native_pkr_stats["sample_size"] > 0:
    quartiles_data.append({
        "Cohort": "Native PKR Only (Monthly Equiv.)",
        "Sample Size": f"N={native_pkr_stats['sample_size']}",
        "Min": format_pkr(native_pkr_stats["min"]),
        "Q1 (25th)": format_pkr(native_pkr_stats["q1"]),
        "Median (50th)": format_pkr(native_pkr_stats["median"]),
        "Mean": format_pkr(native_pkr_stats["mean"]),
        "Q3 (75th)": format_pkr(native_pkr_stats["q3"]),
        "Max": format_pkr(native_pkr_stats["max"]),
        "IQR": format_pkr(native_pkr_stats["iqr"], compact=True),
    })
if usd_stats.get("sample_size", 0) > 0:
    quartiles_data.append({
        "Cohort": "Normalized USD Only (Monthly Equiv.)",
        "Sample Size": f"N={usd_stats['sample_size']}",
        "Min": f"${usd_stats['min']:,.0f}",
        "Q1 (25th)": f"${usd_stats['q1']:,.0f}",
        "Median (50th)": f"${usd_stats['median']:,.0f}",
        "Mean": f"${usd_stats['mean']:,.0f}",
        "Q3 (75th)": f"${usd_stats['q3']:,.0f}",
        "Max": f"${usd_stats['max']:,.0f}",
        "IQR": f"${usd_stats['iqr']:,.0f}",
    })
if eur_stats.get("sample_size", 0) > 0:
    quartiles_data.append({
        "Cohort": "EUR Only (Monthly Equiv., Separate)",
        "Sample Size": f"N={eur_stats['sample_size']}",
        "Min": f"€{eur_stats['min']:,.0f}",
        "Q1 (25th)": f"€{eur_stats['q1']:,.0f}",
        "Median (50th)": f"€{eur_stats['median']:,.0f}",
        "Mean": f"€{eur_stats['mean']:,.0f}",
        "Q3 (75th)": f"€{eur_stats['q3']:,.0f}",
        "Max": f"€{eur_stats['max']:,.0f}",
        "IQR": f"€{eur_stats['iqr']:,.0f}",
    })
quartiles_data.append({
    "Cohort": f"Converted PKR Equivalent — Indicative Only ({curr_str})",
    "Sample Size": f"N={overall_stats['sample_size']}",
    "Min": format_pkr(overall_stats["min"]),
    "Q1 (25th)": format_pkr(overall_stats["q1"]),
    "Median (50th)": format_pkr(overall_stats["median"]),
    "Mean": format_pkr(overall_stats["mean"]),
    "Q3 (75th)": format_pkr(overall_stats["q3"]),
    "Max": format_pkr(overall_stats["max"]),
    "IQR": format_pkr(overall_stats["iqr"], compact=True),
})

q_df = pd.DataFrame(quartiles_data)
st.dataframe(q_df, use_container_width=True, hide_index=True)
st.download_button(
    label="📥 Download Salary Quartile Benchmarks (CSV)",
    data=q_df.to_csv(index=False),
    file_name="hiretrends_salary_quartiles.csv",
    mime="text/csv",
)

render_attribution_footer()

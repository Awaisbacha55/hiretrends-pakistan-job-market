"""HireTrends Dashboard — Market Overview Page.

Displays high-level KPI cards, technical role segmentation, geographic concentration,
and workplace distribution across Pakistan's job market.
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
from src.analysis.location_analysis import analyze_locations
from src.analysis.skills_analysis import get_top_skills
from src.analysis.workplace_analysis import analyze_workplace_distribution

# 1. Load Data & Apply Global Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

render_header("Market Overview", "Executive summary of Pakistan's technology recruitment landscape")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Executive KPI Cards
total_jobs = len(df)
tech_jobs = int((df["is_technology_job"] == True).sum())
non_tech_jobs = int((df["technology_category"] == "Non-Technology").sum())
manual_review_jobs = int((df["needs_manual_review"] == True).sum())
salary_disclosed = int(df["has_salary"].sum())

# Remote count within current selection
known_wp = df[df["workplace_type"].notna()]
remote_count = int((df["workplace_type"] == "remote").sum())
remote_pct = (remote_count / len(known_wp) * 100) if len(known_wp) > 0 else 0.0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    render_kpi_card("Total Listings", format_number(total_jobs), delta=None, help_text="Total active records in filter", color_accent="#2563eb")
with col2:
    render_kpi_card("Tech Roles", format_number(tech_jobs), delta=f"{tech_jobs/total_jobs*100:.1f}% share", help_text="High-confidence tech taxonomy", color_accent="#059669")
with col3:
    render_kpi_card("Non-Tech Roles", format_number(non_tech_jobs), delta=f"{non_tech_jobs/total_jobs*100:.1f}% share", help_text="Operations, medical, sales", color_accent="#d97706")
with col4:
    render_kpi_card("Manual Review", format_number(manual_review_jobs), delta=f"{manual_review_jobs/total_jobs*100:.1f}% ambiguous", help_text="Generic role titles", color_accent="#dc2626")
with col5:
    render_kpi_card("Disclosed Pay", format_number(salary_disclosed), delta=f"{salary_disclosed/total_jobs*100:.1f}% disclosed", help_text="Explicit salary ranges", color_accent="#7c3aed")
with col6:
    render_kpi_card("Remote Openings", format_number(remote_count), delta=f"{remote_pct:.1f}% of known", help_text="Fully remote arrangements", color_accent="#0891b2")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 3. Two-Column Analytics Layout
left_col, right_col = st.columns([1.1, 0.9])

with left_col:
    st.subheader("🛠️ Top 10 Technical Skills Demanded")
    top_skills_data = get_top_skills(df, n=10)
    if top_skills_data:
        top_skills_df = pd.DataFrame(top_skills_data)
        fig_skills = px.bar(
            top_skills_df,
            x="job_count",
            y="skill",
            orientation="h",
            text="job_count",
            color="percentage_of_jobs",
            color_continuous_scale="Viridis",
            labels={"job_count": "Unique Job Postings", "skill": "Skill", "percentage_of_jobs": "% of Postings"},
        )
        fig_skills.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=420,
            margin=dict(l=10, r=20, t=20, b=20),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No skill mentions found in the current selection.")

with right_col:
    st.subheader("🏢 Workplace Arrangement Distribution")
    wp_data = analyze_workplace_distribution(df)
    dist = wp_data["distribution"]
    if wp_data["known_workplace_count"] > 0:
        wp_chart_df = pd.DataFrame([
            {"Type": "Remote", "Count": dist["remote"]["count"]},
            {"Type": "On-site", "Count": dist["on-site"]["count"]},
            {"Type": "Hybrid", "Count": dist["hybrid"]["count"]},
        ])
        fig_wp = px.pie(
            wp_chart_df,
            names="Type",
            values="Count",
            hole=0.5,
            color="Type",
            color_discrete_map={"Remote": "#0891b2", "On-site": "#d97706", "Hybrid": "#059669"},
        )
        fig_wp.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        )
        fig_wp.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_wp, use_container_width=True)
        st.caption(f"Denominator: {wp_data['known_workplace_count']:,} known listings | {wp_data['unknown_workplace_count']:,} listings with unspecified arrangement.")
    else:
        st.info("No workplace records available in the current selection.")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 4. Regional Hub Density & Seniority Breakdown
col_city, col_sen = st.columns([1, 1])

with col_city:
    st.subheader("📍 Top Hiring Tech Hubs in Pakistan")
    loc_data = analyze_locations(df)
    cities = [c for c in loc_data["city_distribution"] if c["city"] != "Other Pakistani Cities"][:6]
    if cities:
        city_df = pd.DataFrame(cities)
        fig_city = px.bar(
            city_df,
            x="city",
            y="count",
            text="count",
            color="percentage_of_mapped_cities",
            color_continuous_scale="Blues",
            labels={"count": "Postings", "city": "City", "percentage_of_mapped_cities": "% of Mapped"},
        )
        fig_city.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_city, use_container_width=True)
        st.caption(
            f"Mapped Pakistani cities: {loc_data['total_mapped_pk_cities']:,} | "
            f"Missing/unmapped PK cities: {loc_data['unmapped_pk_city_count']:,} "
            f"({loc_data['missing_city_percentage_of_pk']:.2f}%) | "
            f"Foreign origin: {loc_data['foreign_listings']['total_foreign_jobs']:,}"
        )
    else:
        st.info("No mapped Pakistani cities in the current selection.")

with col_sen:
    st.subheader("🎓 Career Level / Seniority Distribution")
    sen_counts = df["seniority_level"].value_counts().reset_index()
    sen_counts.columns = ["Seniority Level", "Count"]
    if len(sen_counts) > 0:
        fig_sen = px.bar(
            sen_counts,
            x="Count",
            y="Seniority Level",
            orientation="h",
            text="Count",
            color="Seniority Level",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_sen.update_layout(yaxis={"categoryorder": "total ascending"}, height=380, margin=dict(l=10, r=10, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_sen, use_container_width=True)
    else:
        st.info("No seniority data available in current selection.")

# 5. Dataset Attribution & Time-Period Clarification Callout
active_scope = st.session_state.get("filter_dataset_scope", "Confirmed Pakistan Tech")
active_date_scope = st.session_state.get("filter_date_scope", "Last 12 Months (2025-11-20 to 2026-11-20)")
st.info(
    f"💡 **Dataset Scope & Date-Window Notice:** "
    f"Currently viewing **{active_scope}** | **{active_date_scope}** (**{len(df):,}** postings out of **{len(raw_df):,}** deduplicated records from the November 20, 2026 Headcount Labs Pakistan feed). "
    "The default 12-month window (`2025-11-20` to `2026-11-20`, anchored to the snapshot date) excludes stale 2019–2025 listings while keeping them accessible via the sidebar **Date Window** selector."
)

render_attribution_footer()

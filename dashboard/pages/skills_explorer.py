"""HireTrends Dashboard — Skills Explorer Page.

Interactive technical skills demand browser with category filters, search capabilities,
frequency rankings, and cross-tabulations.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from collections import Counter
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components import (
    render_attribution_footer,
    render_empty_state,
    render_header,
    render_kpi_card,
    render_sidebar_filters,
)
from dashboard.data_loader import format_number, format_pct, load_clean_data
from src.analysis.skills_analysis import (
    get_domain_skill_demand,
    get_skills_by_category,
    get_top_skills,
    parse_job_skills,
)

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

active_scope = st.session_state.get("filter_dataset_scope", "Confirmed Pakistan Tech")
active_date_scope = st.session_state.get("filter_date_scope", "Last 12 Months (2025-11-20 to 2026-11-20)")
render_header("Skills Explorer", f"Skill demand & frequency across 69 technical tools — Scope: {active_scope} | {active_date_scope} (N={len(df):,})")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Controls & Search
col_search, col_domain = st.columns([1.2, 0.8])

with col_search:
    skill_search = st.text_input("🔎 Search Technical Skill", placeholder="e.g. Python, Docker, React, AWS, SQL...")

with col_domain:
    domain_choice = st.selectbox(
        "Domain Cluster",
        options=["All Domains", "Programming Languages", "Cloud & DevOps", "AI & Machine Learning", "Databases & Big Data"],
        index=0,
    )

# 3. Top Skills Computation
total_evaluated = len(df)
top_skills = get_top_skills(df, n=69)
skills_df = pd.DataFrame(top_skills)

if domain_choice != "All Domains":
    domains_data = get_domain_skill_demand(df)
    target_skills = [s["skill"] for s in domains_data.get(domain_choice, [])]
    skills_df = skills_df[skills_df["skill"].isin(target_skills)]

if skill_search.strip():
    skills_df = skills_df[skills_df["skill"].str.contains(skill_search.strip(), case=False, na=False)]

# 4. Summary Metrics
m1, m2, m3, m4 = st.columns(4)
unique_skills_present = len(skills_df)
top_skill_name = skills_df.iloc[0]["skill"] if len(skills_df) > 0 else "None"
top_skill_count = skills_df.iloc[0]["job_count"] if len(skills_df) > 0 else 0
top_skill_pct = skills_df.iloc[0]["percentage_of_jobs"] if len(skills_df) > 0 else 0.0

with m1:
    render_kpi_card("Matching Skills", str(unique_skills_present), help_text="Number of distinct skills matching search", color_accent="#2563eb")
with m2:
    render_kpi_card("#1 Top Skill", top_skill_name, delta=f"{top_skill_count:,} jobs", help_text="Highest demanded skill", color_accent="#059669")
with m3:
    render_kpi_card("Peak Penetration", format_pct(top_skill_pct), help_text="Highest proportion of job postings", color_accent="#d97706")
with m4:
    render_kpi_card("Evaluated Postings", format_number(total_evaluated), help_text="Active sample denominator", color_accent="#7c3aed")

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# 5. Top 20 Interactive Bar Chart
if len(skills_df) > 0:
    st.subheader(f"📊 Top Skills Ranking ({min(len(skills_df), 20)} displayed)")
    chart_df = skills_df.head(20).sort_values("job_count", ascending=True)

    fig = px.bar(
        chart_df,
        x="job_count",
        y="skill",
        orientation="h",
        text="job_count",
        color="percentage_of_jobs",
        color_continuous_scale="Blues",
        labels={"job_count": "Unique Job Postings Count", "skill": "Skill", "percentage_of_jobs": "% of Sample Postings"},
    )
    fig.update_layout(height=max(450, len(chart_df) * 26), margin=dict(l=10, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # 6. Detailed Data Table
    st.subheader("📋 Skills Demand Data Table")
    display_df = skills_df[["rank", "skill", "job_count", "percentage_of_jobs"]].copy()
    display_df.columns = ["Rank", "Technical Skill", "Matching Postings", "% of Sample Postings"]
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "% of Sample Postings": st.column_config.ProgressColumn(
                "% of Sample Postings",
                format="%.1f%%",
                min_value=0,
                max_value=max(100.0, float(skills_df["percentage_of_jobs"].max())),
            ),
        },
    )
    st.download_button(
        label="📥 Download Skills Demand Table (CSV)",
        data=display_df.to_csv(index=False),
        file_name="hiretrends_skills_demand.csv",
        mime="text/csv",
    )
else:
    render_empty_state("No technical skills match your search query or domain selection.")

render_attribution_footer()

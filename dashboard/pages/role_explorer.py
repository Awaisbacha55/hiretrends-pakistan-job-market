"""HireTrends Dashboard — Role Explorer Page.

Role-centric occupational intelligence drilling down into skills, experience,
geographic hubs, workplace arrangements, and compensation for 12 key tech occupations.
"""

from collections import Counter
import re
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
from dashboard.data_loader import format_number, format_pct, format_pkr, load_clean_data
from src.analysis.skills_analysis import TARGET_ROLES, parse_job_skills

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

render_header("Role Explorer", "Occupational skill profiles, career paths, and requirements across 12 tech roles")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Role Selector
role_names = list(TARGET_ROLES.keys())
selected_role = st.selectbox(
    "🎯 Select Target Job Role",
    options=role_names,
    index=0,
    help="Select an occupation to filter skills, experience, locations, and salaries.",
)

# 3. Filter Dataset for Selected Role
role_pattern = TARGET_ROLES[selected_role]
role_mask = (
    df["normalized_title"].fillna("").str.contains(role_pattern) |
    df["job_title"].fillna("").str.contains(role_pattern)
)
role_df = df[role_mask].copy()
sample_size = len(role_df)

if sample_size == 0:
    render_empty_state(f"No postings found matching '{selected_role}' in the current global filter selection.")
    render_attribution_footer()
    st.stop()

# 4. Summary KPI Cards for Selected Role
exp_clean = role_df["experience_min_years"].dropna()
median_exp = f"{exp_clean.median():.1f} yrs" if len(exp_clean) > 0 else "N/A"

sal_clean = role_df["salary_min_pkr"].dropna()
median_sal = format_pkr(sal_clean.median()) if len(sal_clean) > 0 else "N/A"
sal_sample = len(sal_clean)

# Calculate top skill
all_role_skills = []
for skills in role_df["parsed_skills"]:
    all_role_skills.extend(skills)
skill_counts = Counter(all_role_skills)
top_skill_name = skill_counts.most_common(1)[0][0] if skill_counts else "None"
top_skill_pct = (skill_counts.most_common(1)[0][1] / sample_size * 100) if skill_counts else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Matching Listings", format_number(sample_size), delta=f"{sample_size/len(df)*100:.1f}% of active sample", help_text=f"Total jobs for {selected_role}", color_accent="#2563eb")
with c2:
    render_kpi_card("Top Required Skill", top_skill_name, delta=f"{top_skill_pct:.1f}% of postings", help_text="Most frequently demanded skill", color_accent="#059669")
with c3:
    render_kpi_card("Typical Experience", median_exp, delta=f"N={len(exp_clean)} stated", help_text="Median minimum required years", color_accent="#d97706")
with c4:
    render_kpi_card("Median Salary", median_sal, delta=f"N={sal_sample} disclosed", help_text="Monthly PKR equivalent", color_accent="#7c3aed")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 5. Top 10 Required Skills Chart
col_skills, col_exp = st.columns([1.1, 0.9])

with col_skills:
    st.subheader(f"🛠️ Top 10 Skills for {selected_role}")
    top10_skills = skill_counts.most_common(10)
    if top10_skills:
        skill_chart_df = pd.DataFrame([
            {
                "Skill": s,
                "Job Count": c,
                "% of Role Postings": round(c / sample_size * 100, 1),
            }
            for s, c in top10_skills
        ]).sort_values("% of Role Postings", ascending=True)

        fig_skills = px.bar(
            skill_chart_df,
            x="% of Role Postings",
            y="Skill",
            orientation="h",
            text="% of Role Postings",
            color="% of Role Postings",
            color_continuous_scale="Viridis",
            labels={"% of Role Postings": "% of Postings Requiring Skill"},
        )
        fig_skills.update_layout(height=420, margin=dict(l=10, r=20, t=20, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No skill mentions extracted for this role.")

with col_exp:
    st.subheader("🎓 Experience Requirements")
    exp_brackets = role_df["experience_bracket"].value_counts().reset_index()
    exp_brackets.columns = ["Experience Bracket", "Count"]
    fig_exp = px.pie(
        exp_brackets,
        names="Experience Bracket",
        values="Count",
        hole=0.45,
        color="Experience Bracket",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig_exp.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
    st.plotly_chart(fig_exp, use_container_width=True)

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 6. Geography and Workplace for Selected Role
col_loc, col_wp = st.columns([1, 1])

with col_loc:
    st.subheader(f"📍 Top Hiring Cities for {selected_role}")
    city_counts = role_df["normalized_city"].dropna().value_counts().head(6).reset_index()
    city_counts.columns = ["City", "Postings"]
    if len(city_counts) > 0:
        fig_city = px.bar(
            city_counts,
            x="City",
            y="Postings",
            text="Postings",
            color="City",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_city.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_city, use_container_width=True)
    else:
        st.info("No localized city data available for this role (likely remote or foreign).")

with col_wp:
    st.subheader("🏢 Workplace Distribution")
    wp_counts = role_df["workplace_display"].value_counts().reset_index()
    wp_counts.columns = ["Workplace Arrangement", "Postings"]
    fig_wp = px.bar(
        wp_counts,
        x="Postings",
        y="Workplace Arrangement",
        orientation="h",
        text="Postings",
        color="Workplace Arrangement",
        color_discrete_map={"Remote": "#0891b2", "On-site": "#d97706", "Hybrid": "#059669", "Unspecified": "#94a3b8"},
    )
    fig_wp.update_layout(yaxis={"categoryorder": "total ascending"}, height=360, margin=dict(l=10, r=10, t=20, b=20), showlegend=False)
    st.plotly_chart(fig_wp, use_container_width=True)

# 7. Sample Matching Roles Table
st.subheader(f"💼 Recent Sample Postings for {selected_role} (Sample size: N={sample_size})")
sample_table = role_df[["job_title", "company", "normalized_city", "workplace_display", "experience_bracket", "salary_text"]].head(10).copy()
sample_table.columns = ["Job Title", "Company", "City", "Workplace", "Experience Tier", "Salary (if disclosed)"]
sample_table["Salary (if disclosed)"] = sample_table["Salary (if disclosed)"].fillna("Not Disclosed")
st.dataframe(sample_table, use_container_width=True, hide_index=True)

render_attribution_footer()

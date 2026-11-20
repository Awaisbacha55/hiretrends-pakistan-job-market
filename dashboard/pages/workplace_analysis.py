"""HireTrends Dashboard — Workplace Analysis Page.

Analyzes remote vs. on-site vs. hybrid arrangements, ensuring accurate denominators
and transparency regarding unspecified workplace listings.
"""

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
from src.analysis.workplace_analysis import analyze_workplace_distribution

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

render_header("Workplace Analysis", "Remote, on-site, and hybrid flexibility trends in the Pakistan tech market")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Workplace Distribution Calculations
wp_data = analyze_workplace_distribution(df)
known_count = wp_data["known_workplace_count"]
unknown_count = wp_data["unknown_workplace_count"]
dist = wp_data["distribution"]

# 3. KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Known Workplace Records", format_number(known_count), delta=f"{known_count/len(df)*100:.1f}% completeness", help_text="Roles specifying arrangement", color_accent="#2563eb")
with c2:
    r_count = dist["remote"]["count"]
    r_pct = dist["remote"]["pct_of_known"]
    render_kpi_card("Remote Openings", format_number(r_count), delta=f"{r_pct:.1f}% of known", help_text="Fully flexible / WFH roles", color_accent="#0891b2")
with c3:
    o_count = dist["on-site"]["count"]
    o_pct = dist["on-site"]["pct_of_known"]
    render_kpi_card("On-site Openings", format_number(o_count), delta=f"{o_pct:.1f}% of known", help_text="Traditional in-office presence", color_accent="#d97706")
with c4:
    h_count = dist["hybrid"]["count"]
    h_pct = dist["hybrid"]["pct_of_known"]
    render_kpi_card("Hybrid Openings", format_number(h_count), delta=f"{h_pct:.1f}% of known", help_text="Combined office & remote", color_accent="#059669")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 4. Donut Chart & Seniority Crosstab
col_pie, col_seniority = st.columns([1, 1])

with col_pie:
    st.subheader("🏢 Workplace Breakdown (Known Denominator)")
    if known_count > 0:
        wp_chart_df = pd.DataFrame([
            {"Arrangement": "Remote", "Count": r_count, "Pct": r_pct},
            {"Arrangement": "On-site", "Count": o_count, "Pct": o_pct},
            {"Arrangement": "Hybrid", "Count": h_count, "Pct": h_pct},
        ])
        fig_pie = px.pie(
            wp_chart_df,
            names="Arrangement",
            values="Count",
            hole=0.45,
            color="Arrangement",
            color_discrete_map={"Remote": "#0891b2", "On-site": "#d97706", "Hybrid": "#059669"},
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption(f"Denominator: {known_count:,} known arrangements | Excluded: {unknown_count:,} unstated ({unknown_count/len(df)*100:.1f}%)")
    else:
        st.info("No workplace arrangements specified in current selection.")

with col_seniority:
    st.subheader("🎓 Workplace Arrangement by Seniority Tier")
    known_df = df[df["workplace_type"].notna()]
    if len(known_df) > 0:
        sen_wp = known_df.groupby(["seniority_level", "workplace_display"]).size().reset_index(name="Postings")
        fig_sen_wp = px.bar(
            sen_wp,
            x="seniority_level",
            y="Postings",
            color="workplace_display",
            barmode="stack",
            labels={"seniority_level": "Seniority", "workplace_display": "Workplace"},
            color_discrete_map={"Remote": "#0891b2", "On-site": "#d97706", "Hybrid": "#059669"},
        )
        fig_sen_wp.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
        st.plotly_chart(fig_sen_wp, use_container_width=True)
    else:
        st.info("Insufficient seniority-workplace cross-data.")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 5. Technology Roles Workplace Distribution
st.subheader("💻 Workplace Arrangements Within Confirmed Tech Roles")
tech_wp_data = wp_data.get("technology_workplace_distribution", {})
if tech_wp_data:
    t_cols = st.columns(3)
    with t_cols[0]:
        st.metric("Tech Remote Share", f"{tech_wp_data.get('remote', {}).get('pct_of_known_tech', 0.0):.1f}%", f"{tech_wp_data.get('remote', {}).get('count', 0):,} postings")
    with t_cols[1]:
        st.metric("Tech On-site Share", f"{tech_wp_data.get('on-site', {}).get('pct_of_known_tech', 0.0):.1f}%", f"{tech_wp_data.get('on-site', {}).get('count', 0):,} postings")
    with t_cols[2]:
        st.metric("Tech Hybrid Share", f"{tech_wp_data.get('hybrid', {}).get('pct_of_known_tech', 0.0):.1f}%", f"{tech_wp_data.get('hybrid', {}).get('count', 0):,} postings")

render_attribution_footer()

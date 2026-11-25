"""HireTrends Dashboard — Location Analysis Page.

Geographic clustering of technology employment across Pakistani metropolitan hubs,
cross-city comparisons, and segregation of foreign hiring entities.
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
from src.analysis.location_analysis import analyze_locations

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

render_header("Location Analysis", "Geographic tech clusters across Pakistani cities and foreign recruitment entities")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Location Intelligence Analysis
loc_data = analyze_locations(df)
pakistan_jobs = loc_data["pakistan_listings_count"]
foreign_jobs = loc_data["foreign_listings"]["total_foreign_jobs"]
mapped_pk_cities = loc_data["total_mapped_pk_cities"]
unmapped_pk = loc_data["unmapped_pk_city_count"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Domestic Postings", format_number(pakistan_jobs), delta=f"{pakistan_jobs/len(df)*100:.1f}% of active sample", help_text="Pakistan-located openings", color_accent="#2563eb")
with c2:
    render_kpi_card("Mapped City Vacancies", format_number(mapped_pk_cities), delta=f"{mapped_pk_cities/max(pakistan_jobs,1)*100:.1f}% localized", help_text="Specific city named in posting", color_accent="#059669")
with c3:
    render_kpi_card("Missing / Unmapped City PK", format_number(unmapped_pk), delta=f"{unmapped_pk/max(pakistan_jobs,1)*100:.1f}% unmapped", help_text="Missing, remote-only, multi-city, or unmapped city strings", color_accent="#d97706")
with c4:
    render_kpi_card("Foreign Origin Listings", format_number(foreign_jobs), delta=f"{foreign_jobs/len(df)*100:.1f}% cross-border", help_text="US, UK, UAE, international firms", color_accent="#7c3aed")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 3. Top Pakistani Cities Bar Chart
st.subheader("📍 Pakistani Technology Hubs (Ranked by Job Postings)")
city_list = [c for c in loc_data["city_distribution"] if c["city"] != "Other Pakistani Cities"]

if city_list:
    city_chart_df = pd.DataFrame(city_list).sort_values("count", ascending=True)
    fig_city = px.bar(
        city_chart_df,
        x="count",
        y="city",
        orientation="h",
        text="count",
        color="percentage_of_mapped_cities",
        color_continuous_scale="Teal",
        labels={"count": "Job Postings", "city": "City", "percentage_of_mapped_cities": "% of Mapped Postings"},
    )
    fig_city.update_layout(height=420, margin=dict(l=10, r=20, t=20, b=20))
    st.plotly_chart(fig_city, use_container_width=True)
    st.caption(
        f"Mapped Pakistani cities: {mapped_pk_cities:,} ({mapped_pk_cities/max(pakistan_jobs,1)*100:.2f}%) | "
        f"Missing / unmapped city: {unmapped_pk:,} ({unmapped_pk/max(pakistan_jobs,1)*100:.2f}%)"
    )
else:
    st.info("No localized Pakistani cities in current filter selection.")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 4. Cross-City Comparison Tool
st.subheader("⚖️ Interactive City Comparison Tool")
available_cities = [c["city"] for c in city_list if c["count"] >= 5]
if len(available_cities) >= 2:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        city1 = st.selectbox("Compare City A", options=available_cities, index=0, key="compare_city_1")
    with col_sel2:
        city2 = st.selectbox("Compare City B", options=available_cities, index=1 if len(available_cities) > 1 else 0, key="compare_city_2")

    df_city1 = df[df["normalized_city"] == city1]
    df_city2 = df[df["normalized_city"] == city2]

    # Metrics comparison
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        tech1 = int((df_city1["is_technology_job"] == True).sum())
        st.markdown(f"#### 🏙️ {city1} ({len(df_city1):,} total vacancies)")
        st.write(f"- **Tech Job Share:** {tech1:,} ({tech1/max(len(df_city1),1)*100:.1f}%)")
        st.write(f"- **Top Roles:** {', '.join(df_city1['normalized_title'].value_counts().head(3).index.tolist())}")

        # Top 5 skills
        c1_skills = []
        for s in df_city1["parsed_skills"]:
            c1_skills.extend(s)
        top_c1_skills = [s for s, _ in Counter(c1_skills).most_common(5)]
        st.write(f"- **Top 5 Skills:** {', '.join(top_c1_skills)}")

    with col_c2:
        tech2 = int((df_city2["is_technology_job"] == True).sum())
        st.markdown(f"#### 🏙️ {city2} ({len(df_city2):,} total vacancies)")
        st.write(f"- **Tech Job Share:** {tech2:,} ({tech2/max(len(df_city2),1)*100:.1f}%)")
        st.write(f"- **Top Roles:** {', '.join(df_city2['normalized_title'].value_counts().head(3).index.tolist())}")

        # Top 5 skills
        c2_skills = []
        for s in df_city2["parsed_skills"]:
            c2_skills.extend(s)
        top_c2_skills = [s for s, _ in Counter(c2_skills).most_common(5)]
        st.write(f"- **Top 5 Skills:** {', '.join(top_c2_skills)}")
else:
    st.info("Fewer than two cities have sufficient listings for side-by-side comparison.")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 5. Foreign Listings Partition
if foreign_jobs > 0:
    st.subheader(f"🌐 Cross-Border / Foreign Origin Postings (N={foreign_jobs})")
    foreign_breakdown = loc_data["foreign_listings"]["country_breakdown"]
    f_chart_df = pd.DataFrame([
        {"Country": k, "Postings": v} for k, v in foreign_breakdown.items()
    ]).head(8)
    fig_foreign = px.bar(
        f_chart_df,
        x="Country",
        y="Postings",
        text="Postings",
        color="Country",
        title="Foreign Recruitment Entities Sourcing Pakistani Engineering Talent",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_foreign.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_foreign, use_container_width=True)

render_attribution_footer()

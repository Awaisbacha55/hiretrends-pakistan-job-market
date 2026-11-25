"""HireTrends Dashboard — Skill Co-occurrence Page.

Analyzes synergistic technology combinations appearing within the same job postings,
computes Jaccard affinity metrics, renders interactive heatmaps, and provides stack builders.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
from src.analysis.cooccurrence import compute_skill_cooccurrence

# 1. Load Data & Filters
raw_df = load_clean_data()
df = render_sidebar_filters(raw_df)

active_scope = st.session_state.get("filter_dataset_scope", "Confirmed Pakistan Tech")
active_date_scope = st.session_state.get("filter_date_scope", "Last 12 Months (2025-11-20 to 2026-11-20)")
render_header("Skill Co-occurrence", f"Technical stack combinations & Jaccard affinity — Scope: {active_scope} | {active_date_scope} (N={len(df):,})")

if len(df) == 0:
    render_empty_state()
    st.stop()

# 2. Compute Co-occurrences
co_data = compute_skill_cooccurrence(df, top_n_pairs=40, matrix_top_skills=12)
top_pairs = co_data["top_cooccurring_pairs"]

c1, c2, c3, c4 = st.columns(4)
top_pair_name = top_pairs[0]["pair_name"] if top_pairs else "None"
top_pair_count = top_pairs[0]["cooccurrence_count"] if top_pairs else 0
top_pair_jaccard = top_pairs[0]["jaccard_similarity"] if top_pairs else 0.0

with c1:
    render_kpi_card("Distinct Skill Pairs", format_number(co_data["total_distinct_pairs"]), help_text="Total co-occurring technology combinations", color_accent="#2563eb")
with c2:
    render_kpi_card("#1 Dominant Stack", top_pair_name, delta=f"{top_pair_count:,} shared listings", help_text="Most frequent pair in postings", color_accent="#059669")
with c3:
    render_kpi_card("Top Stack Jaccard", f"{top_pair_jaccard:.3f}", help_text="Intersection over union affinity score", color_accent="#d97706")
with c4:
    render_kpi_card("Evaluated Postings", format_number(len(df)), help_text="Active sample denominator", color_accent="#7c3aed")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 3. Interactive Plotly Heatmap
st.subheader("🔥 Skill Co-occurrence Heatmap (Top 12 Demanded Skills)")
matrix_skills = co_data["matrix_skills"]
matrix_records = co_data["cooccurrence_matrix_records"]

if matrix_skills and matrix_records:
    matrix_df = pd.DataFrame(matrix_records).set_index("index")[matrix_skills]

    fig_heat = px.imshow(
        matrix_df,
        labels=dict(x="Skill B", y="Skill A", color="Shared Jobs"),
        x=matrix_skills,
        y=matrix_skills,
        color_continuous_scale="Viridis",
        text_auto=True,
    )
    fig_heat.update_layout(height=580, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Diagonal values represent the total postings demanding that individual skill. Off-diagonal cells represent postings requiring both skills simultaneously.")
else:
    st.info("Insufficient skill diversity in current selection to construct co-occurrence matrix.")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# 4. Searchable Co-occurrence Table & Companion Stack Explorer
col_table, col_companion = st.columns([1.1, 0.9])

with col_table:
    st.subheader("📋 Top Co-occurring Skill Pairs")
    if top_pairs:
        pairs_df = pd.DataFrame(top_pairs)[["rank", "pair_name", "cooccurrence_count", "pct_of_all_jobs", "jaccard_similarity"]]
        pairs_df.columns = ["Rank", "Skill Combination", "Shared Postings", "% of Sample Postings", "Jaccard Affinity"]
        st.dataframe(
            pairs_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Jaccard Affinity": st.column_config.ProgressColumn(
                    "Jaccard Affinity",
                    format="%.3f",
                    min_value=0.0,
                    max_value=1.0,
                ),
            },
        )
    else:
        st.info("No skill pairs found.")

with col_companion:
    st.subheader("🔍 Tech Companion Explorer")
    st.write("Select a primary skill to discover which complementary skills are most commonly required alongside it:")

    skill_candidates = sorted(list(set([p["skill_a"] for p in top_pairs] + [p["skill_b"] for p in top_pairs]))) if top_pairs else []
    if skill_candidates:
        default_idx = skill_candidates.index("Python") if "Python" in skill_candidates else 0
        primary_skill = st.selectbox("Primary Skill", options=skill_candidates, index=default_idx)

        # Filter pairs containing this skill
        related = [
            {
                "Companion Skill": p["skill_b"] if p["skill_a"] == primary_skill else p["skill_a"],
                "Shared Postings": p["cooccurrence_count"],
                "Jaccard Index": p["jaccard_similarity"],
            }
            for p in top_pairs
            if p["skill_a"] == primary_skill or p["skill_b"] == primary_skill
        ]
        if related:
            related_df = pd.DataFrame(related).sort_values("Shared Postings", ascending=False).head(8)
            fig_comp = px.bar(
                related_df,
                x="Shared Postings",
                y="Companion Skill",
                orientation="h",
                text="Shared Postings",
                color="Jaccard Index",
                color_continuous_scale="Blues",
            )
            fig_comp.update_layout(yaxis={"categoryorder": "total ascending"}, height=360, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info(f"No companion skills recorded for {primary_skill} in top pairs.")
    else:
        st.info("No companion skill data available.")

render_attribution_footer()

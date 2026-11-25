"""HireTrends Reusable UI Components & Page Layout Elements.

Provides standardized metric cards, sidebar filter panels, header banners,
empty-state alerts, and attribution footers.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st

from .data_loader import DATE_SCOPE_OPTIONS, SCOPE_OPTIONS, apply_global_filters, format_number, format_pct, format_pkr


def render_header(title: str, subtitle: str = "Pakistan Tech Job Market Intelligence") -> None:
    """Render consistent application header."""
    st.markdown(
        f"""
        <div style="padding-bottom: 12px; margin-bottom: 20px; border-bottom: 2px solid #e9ecef;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <h1 style="margin: 0; font-size: 2.1rem; color: #1e293b; font-weight: 700;">📈 HireTrends</h1>
                <span style="background-color: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">Pakistan Market Intel</span>
            </div>
            <h3 style="margin: 4px 0 0 0; font-size: 1.35rem; color: #3b82f6; font-weight: 600;">{title}</h3>
            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.95rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
    color_accent: str = "#2563eb",
) -> None:
    """Render modern high-contrast KPI metric card."""
    delta_html = f'<div style="font-size: 0.85rem; color: #16a34a; font-weight: 500; margin-top: 4px;">{delta}</div>' if delta else ""
    help_html = f'<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 6px;">{help_text}</div>' if help_text else ""
    st.markdown(
        f"""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 4px solid {color_accent}; height: 100%;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.025em;">{title}</div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #0f172a; margin-top: 4px; line-height: 1.2;">{value}</div>
            {delta_html}
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render global sidebar filters and return filtered DataFrame."""
    st.sidebar.markdown(
        """
        <div style="padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
            <h2 style="margin: 0; font-size: 1.25rem; color: #1e293b;">🔍 Global Filter Panel</h2>
            <p style="margin: 0; font-size: 0.8rem; color: #64748b;">Refine dataset across all metrics</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dataset Scope Selector (defaults to Confirmed Pakistan Tech)
    scope_select = st.sidebar.selectbox(
        "Dataset Scope",
        options=SCOPE_OPTIONS,
        index=0,
        key="filter_dataset_scope",
        help="Default: Confirmed Pakistan Tech jobs. Switch scope to inspect Pakistan-only, Foreign, Non-Tech, or Manual Review subsets.",
    )

    # Date Window Selector (defaults to Last 12 Months: 2025-11-20 to 2026-11-20)
    date_scope_select = st.sidebar.selectbox(
        "Date Window",
        options=DATE_SCOPE_OPTIONS,
        index=0,
        key="filter_date_scope",
        help="Default: Last 12 Months (2025-11-20 to 2026-11-20, anchored to snapshot date). Switch to All Dates to inspect historical 2019–2026 records.",
    )

    with st.sidebar.expander("⚙️ Refine Filters", expanded=True):
        # 1. Tech jobs only toggle (only meaningful when scope is broader than Confirmed Pakistan Tech)
        tech_only = st.checkbox(
            "💻 Confirmed Tech Roles Only",
            value=st.session_state.get("tech_only", False),
            key="filter_tech_only",
            help="Restrict current scope to high-confidence technology listings",
        )

        # 2. Technology Category filter
        valid_cats = ["All Categories"] + sorted([c for c in df["technology_category"].dropna().unique() if c != "Non-Technology"])
        cat_select = st.selectbox(
            "Category",
            options=valid_cats,
            index=0,
            key="filter_category",
        )

        # 3. City filter
        valid_cities = ["All Cities"] + sorted([c for c in df["normalized_city"].dropna().unique()])
        city_select = st.selectbox(
            "Pakistani City",
            options=valid_cities,
            index=0,
            key="filter_city",
        )

        # 4. Workplace filter
        valid_workplace = ["All Workplaces", "Remote", "On-site", "Hybrid"]
        workplace_select = st.selectbox(
            "Workplace Type",
            options=valid_workplace,
            index=0,
            key="filter_workplace",
        )

        # 5. Experience Bracket
        valid_exp = ["All Levels", "Entry / Junior (0-1 yrs)", "Mid-Level (2-4 yrs)", "Senior (5+ yrs)"]
        exp_select = st.selectbox(
            "Experience Bracket",
            options=valid_exp,
            index=0,
            key="filter_experience",
        )

        # 6. Salary filter
        salary_count = int(df["has_salary"].sum()) if "has_salary" in df.columns else 0
        salary_only = st.checkbox(
            "💵 Disclosed Salary Only",
            value=st.session_state.get("salary_only", False),
            key="filter_salary_only",
            help=f"Filter for records with explicit compensation ranges (N={salary_count:,})",
        )

        # 7. Keyword search
        role_search = st.text_input(
            "Search Role Keyword",
            value="",
            key="filter_role_keyword",
            placeholder="e.g. Python, React, DevOps...",
        )

    # Compute pre-date-filter count for transparent retained/excluded reporting
    scope_all_dates_df = apply_global_filters(
        df,
        scope=scope_select,
        date_scope="All Dates (2019–2026 Historical)",
        category=cat_select,
        city=city_select,
        workplace=workplace_select,
        experience_bracket=exp_select,
        salary_only=salary_only,
        tech_only=tech_only,
        role_keyword=role_search,
    )

    # Apply filters including selected date window
    filtered_df = apply_global_filters(
        df,
        scope=scope_select,
        date_scope=date_scope_select,
        category=cat_select,
        city=city_select,
        workplace=workplace_select,
        experience_bracket=exp_select,
        salary_only=salary_only,
        tech_only=tech_only,
        role_keyword=role_search,
    )

    all_dates_n = len(scope_all_dates_df)
    retained_n = len(filtered_df)
    excluded_stale_n = max(all_dates_n - retained_n, 0)
    excluded_pct = (excluded_stale_n / all_dates_n * 100) if all_dates_n > 0 else 0.0
    date_note = (
        f"Cutoff: 2025-11-20 to 2026-11-20 | Excluded stale: {excluded_stale_n:,} ({excluded_pct:.1f}%)"
        if date_scope_select.startswith("Last 12 Months")
        else "All Dates (2019–2026 Historical included)"
    )

    st.sidebar.markdown(
        f"""
        <div style="background-color: #f1f5f9; padding: 10px 14px; border-radius: 6px; margin-top: 14px; font-size: 0.85rem; color: #334155;">
            <b>Scope:</b> {scope_select}<br/>
            <b>Date Window:</b> {date_scope_select}<br/>
            <b>Active Selection:</b> <span style="color: #2563eb; font-weight: 700;">{retained_n:,}</span> of {all_dates_n:,} in scope ({retained_n/max(all_dates_n,1)*100:.1f}%)<br/>
            <span style="font-size: 0.78rem; color: #64748b;">{date_note}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df


def render_empty_state(message: str = "No job postings match your selected filter criteria.") -> None:
    """Render friendly empty state alert."""
    st.markdown(
        f"""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 24px; text-align: center; margin: 20px 0;">
            <h3 style="color: #991b1b; margin: 0 0 6px 0; font-size: 1.1rem;">⚠️ No Matching Records</h3>
            <p style="color: #b91c1c; margin: 0; font-size: 0.9rem;">{message}</p>
            <p style="color: #7f1d1d; margin: 8px 0 0 0; font-size: 0.8rem;">Try resetting your filters in the sidebar to expand results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_attribution_footer() -> None:
    """Render ethical attribution and license disclaimer."""
    st.markdown(
        """
        <div style="margin-top: 50px; padding: 18px 0; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; text-align: center;">
            <p style="margin: 0 0 4px 0;">
                <b>HireTrends — Pakistan Tech Job Market Intelligence</b> | Built with Python, Streamlit & Plotly
            </p>
            <p style="margin: 0;">
                Data source: <b>Headcount Labs</b> (ODbL 1.0 & DbCL 1.0) | Historical baseline: Open Data Pakistan | Location data © OpenStreetMap & Overture Maps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

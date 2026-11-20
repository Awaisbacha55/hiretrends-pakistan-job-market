"""HireTrends — Pakistan Tech Job Market Intelligence Dashboard.

Main Streamlit multipage application entry point.
Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="HireTrends — Pakistan Tech Job Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Multipage Navigation Architecture using st.Page and st.navigation
pages = [
    st.Page("pages/overview.py", title="Market Overview", icon="📊", default=True),
    st.Page("pages/skills_explorer.py", title="Skills Explorer", icon="🛠️"),
    st.Page("pages/role_explorer.py", title="Role Explorer", icon="💼"),
    st.Page("pages/salary_insights.py", title="Salary Insights", icon="💰"),
    st.Page("pages/location_analysis.py", title="Location Analysis", icon="📍"),
    st.Page("pages/workplace_analysis.py", title="Workplace Analysis", icon="🏢"),
    st.Page("pages/skill_cooccurrence.py", title="Skill Co-occurrence", icon="🔗"),
    st.Page("pages/methodology.py", title="Data & Methodology", icon="📜"),
]

# Run navigation
pg = st.navigation(pages)
pg.run()

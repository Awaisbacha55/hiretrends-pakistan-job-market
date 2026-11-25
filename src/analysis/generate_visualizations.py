"""HireTrends Visualization Generator.

Generates high-fidelity Plotly interactive HTML visualizations and Matplotlib/Seaborn
static publication-quality PNG figures for all Day 4 analytical findings.
Outputs saved to reports/figures/.
"""

import json
import os
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

from .cooccurrence import compute_skill_cooccurrence
from .location_analysis import analyze_locations
from .salary_analysis import analyze_salary_data
from .skills_analysis import (
    get_skills_by_role,
    get_top_skills,
    parse_job_skills,
)
from .workplace_analysis import analyze_workplace_distribution

# Set publication style for matplotlib
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
})


def generate_all_visualizations(
    csv_path: str = "data/processed/jobs_pakistan_tech.csv",
    output_dir: str = "reports/figures",
) -> List[str]:
    """Generate the complete suite of 7 interactive Plotly & static PNG charts on Confirmed Pakistan Tech jobs."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {csv_path}")

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    generated_files = []

    # -------------------------------------------------------------
    # 1. Top 20 Skills Bar Chart
    # -------------------------------------------------------------
    top_skills = get_top_skills(df, n=20)
    skills_df = pd.DataFrame(top_skills)

    # Plotly
    fig1 = px.bar(
        skills_df,
        x="job_count",
        y="skill",
        orientation="h",
        text="job_count",
        color="percentage_of_jobs",
        color_continuous_scale="Viridis",
        title=f"Top 20 Technical Skills — Confirmed Pakistan Tech Jobs (N={len(df):,})",
        labels={"job_count": "Unique Job Postings Count", "skill": "Technical Skill", "percentage_of_jobs": "% of Pakistan Tech Postings"},
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"}, height=700, margin={"l": 150, "r": 30, "t": 60, "b": 50})
    p1_html = os.path.join(output_dir, "top_20_skills.html")
    fig1.write_html(p1_html, include_plotlyjs="cdn")
    generated_files.append(p1_html)

    # Matplotlib PNG
    fig_m1, ax_m1 = plt.subplots(figsize=(10, 8))
    sns.barplot(data=skills_df, x="job_count", y="skill", ax=ax_m1, palette="mako")
    ax_m1.set_title(f"Top 20 Technical Skills — Confirmed Pakistan Tech (N={len(df):,})", weight="bold")
    ax_m1.set_xlabel("Unique Job Postings Count")
    ax_m1.set_ylabel("Technical Skill")
    for p in ax_m1.patches:
        width = p.get_width()
        ax_m1.annotate(f"{int(width)}", (width + 5, p.get_y() + p.get_height() / 2),
                       va="center", ha="left", fontsize=9, color="#333333")
    fig_m1.tight_layout()
    p1_png = os.path.join(output_dir, "top_20_skills.png")
    fig_m1.savefig(p1_png, dpi=300)
    plt.close(fig_m1)
    generated_files.append(p1_png)

    # -------------------------------------------------------------
    # 2. Skills by Role Chart (Top 5 target roles)
    # -------------------------------------------------------------
    role_analysis = get_skills_by_role(df, top_n=5)
    role_chart_data = []
    for r_name in ["Software Engineer", "Full Stack Developer", "AI Engineer", "DevOps Engineer", "Data Analyst"]:
        r_info = role_analysis.get(r_name, {})
        s_size = r_info.get("sample_size", 0)
        for s in r_info.get("top_skills", [])[:5]:
            role_chart_data.append({
                "Role (Sample Size)": f"{r_name} (N={s_size})",
                "Skill": s["skill"],
                "Percentage": s["percentage"],
                "Count": s["count"],
            })
    role_df = pd.DataFrame(role_chart_data)

    # Plotly
    fig2 = px.bar(
        role_df,
        x="Percentage",
        y="Skill",
        color="Role (Sample Size)",
        barmode="group",
        title="Top Skills by Role (% of Postings Demanding Skill)",
        labels={"Percentage": "% Postings Requiring Skill", "Skill": "Technical Skill"},
    )
    fig2.update_layout(height=650, margin={"l": 120, "r": 30, "t": 60, "b": 50})
    p2_html = os.path.join(output_dir, "skills_by_role.html")
    fig2.write_html(p2_html, include_plotlyjs="cdn")
    generated_files.append(p2_html)

    # Matplotlib PNG
    fig_m2, ax_m2 = plt.subplots(figsize=(11, 7))
    sns.barplot(data=role_df, x="Percentage", y="Skill", hue="Role (Sample Size)", ax=ax_m2, palette="tab10")
    ax_m2.set_title("Top In-Demand Skills Across Representative Tech Roles", weight="bold")
    ax_m2.set_xlabel("% of Role Postings Requiring Skill")
    ax_m2.legend(title="Role & Sample Size", loc="lower right")
    fig_m2.tight_layout()
    p2_png = os.path.join(output_dir, "skills_by_role.png")
    fig_m2.savefig(p2_png, dpi=300)
    plt.close(fig_m2)
    generated_files.append(p2_png)

    # -------------------------------------------------------------
    # 3. Salary Distribution Chart (Log scale & Inlier histogram)
    # -------------------------------------------------------------
    sal_sub = df[df["salary_min_pkr"].notna()].copy()
    sal_inliers = sal_sub[(sal_sub["salary_min_pkr"] >= 20000) & (sal_sub["salary_min_pkr"] <= 2500000)].copy()

    # Plotly Box & Histogram
    fig3 = px.box(
        sal_sub,
        x="salary_currency",
        y="salary_min_pkr",
        color="salary_currency",
        log_y=True,
        title=f"Disclosed Monthly Salary Distribution by Currency (PKR Equivalent, Log Scale, N={len(sal_sub):,})",
        labels={"salary_min_pkr": "Monthly Equivalent (PKR, Log Scale)", "salary_currency": "Native Quoted Currency"},
    )
    fig3.update_layout(height=550)
    p3_html = os.path.join(output_dir, "salary_distribution.html")
    fig3.write_html(p3_html, include_plotlyjs="cdn")
    generated_files.append(p3_html)

    # Matplotlib PNG
    fig_m3, (ax_m3_1, ax_m3_2) = plt.subplots(1, 2, figsize=(13, 5))
    sns.histplot(data=sal_inliers, x="salary_min_pkr", bins=25, kde=True, ax=ax_m3_1, color="#2b5c8f")
    ax_m3_1.set_title(f"Monthly PKR Compensation (20k - 2.5M PKR, N={len(sal_inliers):,})", weight="bold")
    ax_m3_1.set_xlabel("Monthly Compensation (PKR)")
    ax_m3_1.set_ylabel("Job Postings Count")

    sns.boxplot(data=sal_sub, x="salary_currency", y="salary_min_pkr", ax=ax_m3_2, palette="Set2")
    ax_m3_2.set_yscale("log")
    ax_m3_2.set_title(f"Quoted Currency Comparison (Log-10 Scale, N={len(sal_sub):,})", weight="bold")
    ax_m3_2.set_ylabel("Monthly Equivalent (PKR)")
    fig_m3.tight_layout()
    p3_png = os.path.join(output_dir, "salary_distribution.png")
    fig_m3.savefig(p3_png, dpi=300)
    plt.close(fig_m3)
    generated_files.append(p3_png)

    # -------------------------------------------------------------
    # 4. Salary by Experience Chart
    # -------------------------------------------------------------
    sal_sub["experience_bracket"] = "Unspecified"
    sal_sub.loc[sal_sub["experience_min_years"] <= 1.0, "experience_bracket"] = "0-1 yrs (Junior)"
    sal_sub.loc[(sal_sub["experience_min_years"] >= 2.0) & (sal_sub["experience_min_years"] <= 4.0), "experience_bracket"] = "2-4 yrs (Mid)"
    sal_sub.loc[sal_sub["experience_min_years"] >= 5.0, "experience_bracket"] = "5+ yrs (Senior)"

    exp_filtered = sal_sub[sal_sub["experience_bracket"] != "Unspecified"]
    fig4 = px.box(
        exp_filtered,
        x="experience_bracket",
        y="salary_min_pkr",
        color="experience_bracket",
        category_orders={"experience_bracket": ["0-1 yrs (Junior)", "2-4 yrs (Mid)", "5+ yrs (Senior)"]},
        title=f"Monthly PKR Salary by Experience Bracket (N={len(exp_filtered):,} Disclosed with Experience)",
        labels={"salary_min_pkr": "Monthly Salary (PKR)", "experience_bracket": "Experience Level"},
    )
    fig4.update_layout(height=550)
    p4_html = os.path.join(output_dir, "salary_by_experience.html")
    fig4.write_html(p4_html, include_plotlyjs="cdn")
    generated_files.append(p4_html)

    # Matplotlib PNG
    fig_m4, ax_m4 = plt.subplots(figsize=(9, 6))
    sns.boxplot(
        data=exp_filtered,
        x="experience_bracket",
        y="salary_min_pkr",
        order=["0-1 yrs (Junior)", "2-4 yrs (Mid)", "5+ yrs (Senior)"],
        ax=ax_m4,
        palette="Blues_d",
    )
    ax_m4.set_yscale("log")
    ax_m4.set_title("Compensation Scaling Across Experience Tiers (Log Scale)", weight="bold")
    ax_m4.set_xlabel("Experience Level")
    ax_m4.set_ylabel("Monthly Salary (PKR Equivalent)")
    fig_m4.tight_layout()
    p4_png = os.path.join(output_dir, "salary_by_experience.png")
    fig_m4.savefig(p4_png, dpi=300)
    plt.close(fig_m4)
    generated_files.append(p4_png)

    # -------------------------------------------------------------
    # 5. Top Hiring Cities
    # -------------------------------------------------------------
    loc_analysis = analyze_locations(df)
    top_cities = [c for c in loc_analysis["city_distribution"] if c["city"] != "Other Pakistani Cities"][:10]
    cities_df = pd.DataFrame(top_cities)

    # Plotly Bar
    fig5 = px.bar(
        cities_df,
        x="city",
        y="count",
        text="count",
        color="percentage_of_mapped_cities",
        color_continuous_scale="Teal",
        title=f"Top Hiring Hubs — Confirmed Pakistan Tech Jobs (N={loc_analysis['total_mapped_pk_cities']:,} Mapped Cities)",
        labels={"count": "Job Postings Count", "city": "City", "percentage_of_mapped_cities": "% of Mapped Cities"},
    )
    fig5.update_layout(height=550)
    p5_html = os.path.join(output_dir, "top_hiring_cities.html")
    fig5.write_html(p5_html, include_plotlyjs="cdn")
    generated_files.append(p5_html)

    # Matplotlib PNG
    fig_m5, ax_m5 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=cities_df, x="city", y="count", ax=ax_m5, palette="rocket")
    ax_m5.set_title("Geographic Concentration of Employment in Pakistan", weight="bold")
    ax_m5.set_xlabel("City")
    ax_m5.set_ylabel("Job Postings Count")
    plt.xticks(rotation=30, ha="right")
    for p in ax_m5.patches:
        h = p.get_height()
        ax_m5.annotate(f"{int(h)}", (p.get_x() + p.get_width() / 2, h + 15),
                       ha="center", va="bottom", fontsize=9)
    fig_m5.tight_layout()
    p5_png = os.path.join(output_dir, "top_hiring_cities.png")
    fig_m5.savefig(p5_png, dpi=300)
    plt.close(fig_m5)
    generated_files.append(p5_png)

    # -------------------------------------------------------------
    # 6. Workplace Distribution (Remote, On-site, Hybrid)
    # -------------------------------------------------------------
    wp_analysis = analyze_workplace_distribution(df)
    wp_data = [
        {"Workplace Arrangement": "Remote", "Count": wp_analysis["distribution"]["remote"]["count"], "Percentage": wp_analysis["distribution"]["remote"]["pct_of_known"]},
        {"Workplace Arrangement": "On-site", "Count": wp_analysis["distribution"]["on-site"]["count"], "Percentage": wp_analysis["distribution"]["on-site"]["pct_of_known"]},
        {"Workplace Arrangement": "Hybrid", "Count": wp_analysis["distribution"]["hybrid"]["count"], "Percentage": wp_analysis["distribution"]["hybrid"]["pct_of_known"]},
    ]
    wp_df = pd.DataFrame(wp_data)

    # Plotly Donut
    fig6 = px.pie(
        wp_df,
        names="Workplace Arrangement",
        values="Count",
        hole=0.45,
        title=f"Workplace Arrangements Distribution (Known N={wp_analysis['known_workplace_count']:,}, Unknown={wp_analysis['unknown_workplace_count']:,})",
        color="Workplace Arrangement",
        color_discrete_map={"Remote": "#1f77b4", "On-site": "#ff7f0e", "Hybrid": "#2ca02c"},
    )
    fig6.update_traces(textposition="inside", textinfo="percent+label")
    p6_html = os.path.join(output_dir, "workplace_distribution.html")
    fig6.write_html(p6_html, include_plotlyjs="cdn")
    generated_files.append(p6_html)

    # Matplotlib Donut PNG
    fig_m6, ax_m6 = plt.subplots(figsize=(7, 7))
    colors = ["#2b5c8f", "#e28743", "#388e3c"]
    ax_m6.pie(wp_df["Count"], labels=wp_df["Workplace Arrangement"], autopct="%1.1f%%",
              startangle=140, colors=colors, wedgeprops=dict(width=0.45, edgecolor="w"))
    ax_m6.set_title(f"Workplace Arrangement Distribution\n(Known Postings N={wp_analysis['known_workplace_count']:,})", weight="bold")
    fig_m6.tight_layout()
    p6_png = os.path.join(output_dir, "workplace_distribution.png")
    fig_m6.savefig(p6_png, dpi=300)
    plt.close(fig_m6)
    generated_files.append(p6_png)

    # -------------------------------------------------------------
    # 7. Skill Co-occurrence Heatmap
    # -------------------------------------------------------------
    co_analysis = compute_skill_cooccurrence(df, top_n_pairs=25, matrix_top_skills=12)
    matrix_skills = co_analysis["matrix_skills"]
    matrix_records = co_analysis["cooccurrence_matrix_records"]
    matrix_df = pd.DataFrame(matrix_records).set_index("index")[matrix_skills]

    # Plotly Heatmap
    fig7 = px.imshow(
        matrix_df,
        labels=dict(x="Skill B", y="Skill A", color="Shared Jobs Count"),
        x=matrix_skills,
        y=matrix_skills,
        color_continuous_scale="Viridis",
        title="Technical Skill Co-occurrence Matrix (Top 12 Demanded Skills)",
    )
    fig7.update_layout(height=650, width=700)
    p7_html = os.path.join(output_dir, "skill_cooccurrence_heatmap.html")
    fig7.write_html(p7_html, include_plotlyjs="cdn")
    generated_files.append(p7_html)

    # Matplotlib Heatmap PNG
    fig_m7, ax_m7 = plt.subplots(figsize=(10, 8))
    sns.heatmap(matrix_df, annot=True, fmt="d", cmap="YlGnBu", ax=ax_m7, cbar_kws={"label": "Shared Jobs Count"})
    ax_m7.set_title("Skill Pair Co-occurrence Matrix (Top 12 Skills)", weight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    fig_m7.tight_layout()
    p7_png = os.path.join(output_dir, "skill_cooccurrence_heatmap.png")
    fig_m7.savefig(p7_png, dpi=300)
    plt.close(fig_m7)
    generated_files.append(p7_png)

    return generated_files


if __name__ == "__main__":
    generated = generate_all_visualizations()
    print(f"Generated {len(generated)} visualization artifacts in reports/figures/:")
    for f in generated:
        print(f"  - {f}")

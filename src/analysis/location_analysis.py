"""HireTrends Location and Regional Tech Hub Analysis Engine.

Analyzes geographic distribution across Pakistani technology hubs (Lahore, Karachi,
Islamabad, Rawalpindi, Peshawar, Faisalabad, etc.), isolates foreign employment listings,
and computes occupational role distributions per city.
"""

from collections import Counter
from typing import Any, Dict, List, Optional
import pandas as pd


def analyze_locations(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze geographic distribution of job postings.

    Ensures:
    - Remote is treated as a workplace arrangement, not a city.
    - Foreign locations are partitioned and reported separately.
    - Role-by-city distributions are computed for major tech centers.
    """
    total_listings = len(df)

    # 1. Foreign vs Pakistan Partition
    pakistan_df = df[df["is_pakistan_location"] == True].copy()
    foreign_df = df[df["is_pakistan_location"] == False].copy()

    # Foreign breakdown by country
    foreign_countries = foreign_df["country"].fillna("Unknown Foreign").value_counts().to_dict()

    # 2. Pakistan City Distribution
    known_pk_cities_df = pakistan_df[pakistan_df["normalized_city"].notna()]
    total_mapped_cities = len(known_pk_cities_df)
    unmapped_pk_city_count = len(pakistan_df) - total_mapped_cities

    city_counts = known_pk_cities_df["normalized_city"].value_counts()
    major_target_cities = [
        "Lahore", "Karachi", "Islamabad", "Rawalpindi", "Peshawar",
        "Faisalabad", "Multan", "Sukkur", "Hyderabad", "Larkana",
        "Sialkot", "Quetta",
    ]

    city_distribution = []
    other_cities_count = 0

    for city, count in city_counts.items():
        pct_of_mapped = round(count / max(total_mapped_cities, 1) * 100, 2)
        pct_of_all = round(count / total_listings * 100, 2)
        entry = {
            "city": city,
            "count": int(count),
            "percentage_of_mapped_cities": pct_of_mapped,
            "percentage_of_all_jobs": pct_of_all,
            "is_major_hub": city in major_target_cities,
        }
        if city in major_target_cities:
            city_distribution.append(entry)
        else:
            other_cities_count += count

    if other_cities_count > 0:
        city_distribution.append({
            "city": "Other Pakistani Cities",
            "count": int(other_cities_count),
            "percentage_of_mapped_cities": round(other_cities_count / max(total_mapped_cities, 1) * 100, 2),
            "percentage_of_all_jobs": round(other_cities_count / total_listings * 100, 2),
            "is_major_hub": False,
        })

    # 3. Role-by-City Distribution for Top 3 Hubs (Lahore, Karachi, Islamabad)
    top_3_hubs = ["Lahore", "Karachi", "Islamabad"]
    role_by_city = {}

    for hub in top_3_hubs:
        hub_df = known_pk_cities_df[known_pk_cities_df["normalized_city"] == hub]
        hub_total = len(hub_df)
        tech_in_hub = int((hub_df["is_technology_job"] == True).sum())

        # Top occupational titles
        top_titles = hub_df["normalized_title"].value_counts().head(8).to_dict()
        top_tech_categories = hub_df[hub_df["is_technology_job"] == True]["technology_category"].value_counts().head(5).to_dict()

        role_by_city[hub] = {
            "total_postings": hub_total,
            "tech_postings": tech_in_hub,
            "tech_percentage": round(tech_in_hub / max(hub_total, 1) * 100, 1),
            "top_job_titles": top_titles,
            "top_tech_categories": top_tech_categories,
        }

    return {
        "total_listings": total_listings,
        "pakistan_listings_count": len(pakistan_df),
        "total_mapped_pk_cities": total_mapped_cities,
        "unmapped_pk_city_count": unmapped_pk_city_count,
        "mapped_city_percentage_of_pk": round(total_mapped_cities / max(len(pakistan_df), 1) * 100, 2),
        "missing_city_percentage_of_pk": round(unmapped_pk_city_count / max(len(pakistan_df), 1) * 100, 2),
        "city_distribution": city_distribution,
        "foreign_listings": {
            "total_foreign_jobs": len(foreign_df),
            "percentage_of_total": round(len(foreign_df) / total_listings * 100, 2),
            "country_breakdown": foreign_countries,
        },
        "role_by_city": role_by_city,
    }

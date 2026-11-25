"""HireTrends Pakistani City and Location Normalizer.

Standardizes Pakistani tech hub names, validates geographical boundaries,
and strictly prevents foreign locations (Cairo, Turkey, etc.) from being classified as Pakistani cities.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

PAKISTAN_CITIES = {
    # Sindh
    "karachi": ("Karachi", "Sindh", "PK"),
    "khi": ("Karachi", "Sindh", "PK"),
    "karachi city": ("Karachi", "Sindh", "PK"),
    "hyderabad": ("Hyderabad", "Sindh", "PK"),
    "sukkur": ("Sukkur", "Sindh", "PK"),
    "larkana": ("Larkana", "Sindh", "PK"),
    
    # Punjab
    "lahore": ("Lahore", "Punjab", "PK"),
    "lhr": ("Lahore", "Punjab", "PK"),
    "rawalpindi": ("Rawalpindi", "Punjab", "PK"),
    "rwp": ("Rawalpindi", "Punjab", "PK"),
    "faisalabad": ("Faisalabad", "Punjab", "PK"),
    "fsd": ("Faisalabad", "Punjab", "PK"),
    "multan": ("Multan", "Punjab", "PK"),
    "gujranwala": ("Gujranwala", "Punjab", "PK"),
    "sialkot": ("Sialkot", "Punjab", "PK"),
    "bahawalpur": ("Bahawalpur", "Punjab", "PK"),
    "sargodha": ("Sargodha", "Punjab", "PK"),
    "gujrat": ("Gujrat", "Punjab", "PK"),
    "sheikhupura": ("Sheikhupura", "Punjab", "PK"),
    "sahiwal": ("Sahiwal", "Punjab", "PK"),
    
    # Federal Capital
    "islamabad": ("Islamabad", "Islamabad Capital Territory", "PK"),
    "isb": ("Islamabad", "Islamabad Capital Territory", "PK"),
    "islamabad capital territory": ("Islamabad", "Islamabad Capital Territory", "PK"),
    
    # Khyber Pakhtunkhwa
    "peshawar": ("Peshawar", "Khyber Pakhtunkhwa", "PK"),
    "pesh": ("Peshawar", "Khyber Pakhtunkhwa", "PK"),
    "abbottabad": ("Abbottabad", "Khyber Pakhtunkhwa", "PK"),
    "mardan": ("Mardan", "Khyber Pakhtunkhwa", "PK"),
    "swat": ("Swat", "Khyber Pakhtunkhwa", "PK"),
    "haripur": ("Haripur", "Khyber Pakhtunkhwa", "PK"),
    
    # Balochistan
    "quetta": ("Quetta", "Balochistan", "PK"),
    "gwadar": ("Gwadar", "Balochistan", "PK"),
    
    # Azad Jammu & Kashmir / Gilgit-Baltistan
    "muzaffarabad": ("Muzaffarabad", "Azad Jammu & Kashmir", "PK"),
    "mirpur": ("Mirpur", "Azad Jammu & Kashmir", "PK"),
    "gilgit": ("Gilgit", "Gilgit-Baltistan", "PK"),
    "skardu": ("Skardu", "Gilgit-Baltistan", "PK"),
}

# Explicitly foreign locations that may appear in global remote or mis-tagged listings
FOREIGN_LOCATIONS = {
    "cairo": ("Cairo", "Cairo Governorate", "EG"),
    "egypt": ("Cairo", "Cairo Governorate", "EG"),
    "turkey": ("Istanbul", "Turkey", "TR"),
    "istanbul": ("Istanbul", "Turkey", "TR"),
    "dubai": ("Dubai", "Dubai", "AE"),
    "uae": ("Dubai", "Dubai", "AE"),
    "london": ("London", "Greater London", "GB"),
    "uk": ("London", "Greater London", "GB"),
    "united kingdom": ("London", "Greater London", "GB"),
    "united states": ("United States", None, "US"),
    "usa": ("United States", None, "US"),
    "mclean": ("McLean", "Virginia", "US"),
    "new york": ("New York", "New York", "US"),
    "san francisco": ("San Francisco", "California", "US"),
    "sunnyvale": ("Sunnyvale", "California", "US"),
    "toronto": ("Toronto", "Ontario", "CA"),
    "riyadh": ("Riyadh", "Riyadh", "SA"),
    "jeddah": ("Jeddah", "Makkah", "SA"),
    "berlin": ("Berlin", "Berlin", "DE"),
    "singapore": ("Singapore", None, "SG"),
}


def _is_pk_country(raw_country: Optional[str]) -> bool:
    """Return True only if raw_country explicitly denotes Pakistan."""
    if not raw_country or not isinstance(raw_country, str):
        return False
    return raw_country.strip().upper() in ("PK", "PAK", "PAKISTAN")


def normalize_city_name(
    raw_city: Optional[str],
    raw_country: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """Normalize city string without defaulting missing countries to Pakistan.

    Returns:
        (normalized_city, region, country, is_pakistan)
    """
    norm_raw_country = raw_country.strip().upper() if isinstance(raw_country, str) and raw_country.strip() else None
    is_explicit_pk = _is_pk_country(norm_raw_country)

    if not raw_city or not isinstance(raw_city, str) or not raw_city.strip():
        return None, None, norm_raw_country, is_explicit_pk

    clean = raw_city.strip().lower()

    # Remote is not a city, and Remote alone does NOT prove Pakistan
    if clean in ("remote", "telecommute", "work from home", "wfh", "anywhere"):
        return None, None, norm_raw_country, is_explicit_pk

    # Check foreign locations (overrides noisy PK country tags if city is clearly foreign)
    if clean in FOREIGN_LOCATIONS:
        f_city, f_reg, f_cnt = FOREIGN_LOCATIONS[clean]
        return None, f_reg, f_cnt, False

    # Check Pakistani city mapping
    if clean in PAKISTAN_CITIES:
        norm_city, region, country = PAKISTAN_CITIES[clean]
        return norm_city, region, country, True

    # Strip prefixes/suffixes like "City", ", Pakistan", etc.
    clean_stripped = re.sub(r"[,]?\s*(pakistan|pk|city)\b", "", clean, flags=re.IGNORECASE).strip()
    if clean_stripped in PAKISTAN_CITIES:
        norm_city, region, country = PAKISTAN_CITIES[clean_stripped]
        return norm_city, region, country, True

    # Check if country is explicitly foreign
    if norm_raw_country and not is_explicit_pk:
        return None, None, norm_raw_country, False

    # Unknown city: preserve explicit country if provided, otherwise None (Unknown)
    return None, None, norm_raw_country, is_explicit_pk


def normalize_location(
    city: Optional[str],
    region: Optional[str] = None,
    country: Optional[str] = None,
    all_locations: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Comprehensive location normalizer preserving multi-location arrays.

    Multi-location rule:
    - Uses primary city/country first.
    - Classifies country as 'Pakistan', 'Foreign', or 'Unknown'.
    - Missing country or Remote-only location without country evidence -> 'Unknown'.

    Returns:
        {
            "original_city": str | None,
            "normalized_city": str | None,
            "normalized_region": str | None,
            "normalized_country": str | None,
            "is_pakistan": bool,
            "country_classification": "Pakistan" | "Foreign" | "Unknown",
            "all_locations": list
        }
    """
    norm_city, norm_reg, norm_country, is_pk = normalize_city_name(city, country)

    # Use provided region if unmapped by city table
    final_region = norm_reg or region

    if is_pk:
        country_classification = "Pakistan"
    elif norm_country:
        country_classification = "Foreign"
    else:
        country_classification = "Unknown"

    return {
        "original_city": city,
        "normalized_city": norm_city,
        "normalized_region": final_region,
        "normalized_country": norm_country,
        "is_pakistan": is_pk,
        "country_classification": country_classification,
        "all_locations": all_locations or [],
    }

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

# Explicitly foreign locations that may appear in global remote listings
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
}


def normalize_city_name(raw_city: Optional[str], raw_country: Optional[str] = "PK") -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """Normalize city string.

    Returns:
        (normalized_city, region, country, is_pakistan)
    """
    if not raw_city or not isinstance(raw_city, str):
        return None, None, raw_country or "PK", bool(raw_country == "PK")

    clean = raw_city.strip().lower()

    # Remote is not a city
    if clean in ("remote", "telecommute", "work from home", "wfh", "anywhere"):
        return None, None, raw_country or "PK", bool(raw_country == "PK")

    # Check foreign locations
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
    if raw_country and raw_country.upper() not in ("PK", "PAK", "PAKISTAN"):
        return None, None, raw_country.upper(), False

    # Unknown city: must remain unknown (None), not guessed
    return None, None, raw_country or "PK", bool(raw_country == "PK")


def normalize_location(
    city: Optional[str],
    region: Optional[str] = None,
    country: Optional[str] = "PK",
    all_locations: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Comprehensive location normalizer preserving multi-location arrays.

    Returns:
        {
            "original_city": str | None,
            "normalized_city": str | None,
            "normalized_region": str | None,
            "normalized_country": str,
            "is_pakistan": bool,
            "all_locations": list
        }
    """
    norm_city, norm_reg, norm_country, is_pk = normalize_city_name(city, country)

    # Use provided region if unmapped by city table
    final_region = norm_reg or region

    return {
        "original_city": city,
        "normalized_city": norm_city,
        "normalized_region": final_region,
        "normalized_country": norm_country or "PK",
        "is_pakistan": is_pk,
        "all_locations": all_locations or [],
    }

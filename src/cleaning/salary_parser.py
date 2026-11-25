"""HireTrends Salary and Compensation Normalizer.

Parses compensation figures, extracts currencies and intervals, and standardizes
amounts into monthly Pakistani Rupees (PKR) using documented official exchange rates.
"""

import re
from typing import Any, Dict, Optional, Tuple

# Documented official exchange rates as of November 20, 2026
# Source: State Bank of Pakistan (SBP) Mark-to-Market / Ready Reference Rates (20 November 2026)
# Reference: https://www.sbp.org.pk/assets/document/mark-to-market-revaluation-exchange-rate-20-november-2026.pdf
EXCHANGE_RATES_TO_PKR = {
    "PKR": (1.0, "State Bank of Pakistan (Base Currency)"),
    "USD": (276.5132, "State Bank of Pakistan Mark-to-Market / Ready Reference (2026-11-20)"),
    "EUR": (295.00, "State Bank of Pakistan Reference (2026-11-20)"),
    "GBP": (352.00, "State Bank of Pakistan Reference (2026-11-20)"),
    "AED": (75.80, "State Bank of Pakistan Reference (2026-11-20)"),
    "CAD": (202.50, "State Bank of Pakistan Reference (2026-11-20)"),
    "AUD": (181.00, "State Bank of Pakistan Reference (2026-11-20)"),
}

STANDARD_MONTHLY_HOURS = 176.0  # 8 hours/day * 22 working days/month

# Regex patterns for salary parsing
SALARY_PATTERNS = [
    # Explicit Range: "PKR 150,000 - 250,000 per month" or "$3,000 - $5,000 / month"
    re.compile(
        r"(?P<curr>PKR|Rs\.?|USD|\$|EUR|€|GBP|£|AED)\s*(?P<min>[\d,]+(?:\.\d+)?)\s*(?:-|to|–)\s*(?:(?P<curr2>PKR|Rs\.?|USD|\$|EUR|€|GBP|£|AED)\s*)?(?P<max>[\d,]+(?:\.\d+)?)\s*(?:per|\/|\ba\b)?\s*(?P<intv>month|monthly|year|annum|annual|annually|hour|hr|hourly)?",
        re.IGNORECASE,
    ),
    # Single figure with interval: "250,000 PKR / month", "$4,000 / month"
    re.compile(
        r"(?P<curr>PKR|Rs\.?|USD|\$|EUR|€|GBP|£|AED)\s*(?P<val>[\d,]+(?:\.\d+)?)\s*(?:per|\/|\ba\b)?\s*(?P<intv>month|monthly|year|annum|annual|annually|hour|hr|hourly)?",
        re.IGNORECASE,
    ),
]


def normalize_currency_code(raw_symbol: Optional[str]) -> Optional[str]:
    """Map currency symbols and aliases to standard ISO currency codes."""
    if not raw_symbol:
        return None
    sym = raw_symbol.strip().upper()
    if sym in ("PKR", "RS", "RS."):
        return "PKR"
    if sym in ("USD", "$"):
        return "USD"
    if sym in ("EUR", "€"):
        return "EUR"
    if sym in ("GBP", "£"):
        return "GBP"
    if sym in ("AED", "DIRHAM"):
        return "AED"
    return sym


def normalize_interval(raw_intv: Optional[str]) -> str:
    """Normalize interval string into month, year, or hour."""
    if not raw_intv:
        return "month"  # Default assumption for standard Pakistan postings if unspecified
    clean = raw_intv.strip().lower()
    if clean in ("year", "annum", "annual", "annually", "yr"):
        return "year"
    if clean in ("hour", "hr", "hourly"):
        return "hour"
    return "month"


def clean_num(val_str: Optional[str]) -> Optional[float]:
    """Convert comma-formatted numerical string to float."""
    if not val_str:
        return None
    try:
        clean = val_str.replace(",", "").strip()
        return float(clean)
    except ValueError:
        return None


def parse_salary(
    salary_text: Optional[str],
    structured_pay: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Parse salary information and normalize monthly PKR amounts.

    Returns:
        {
            "salary_text": str | None,
            "salary_currency": str | None,
            "salary_interval": str | None,
            "salary_min_original": float | None,
            "salary_max_original": float | None,
            "salary_min_pkr": float | None,
            "salary_max_pkr": float | None,
            "salary_is_converted": bool,
            "exchange_rate_used": float | None,
            "exchange_rate_source": str | None
        }
    """
    empty_result = {
        "salary_text": salary_text,
        "salary_currency": None,
        "salary_interval": None,
        "salary_min_original": None,
        "salary_max_original": None,
        "salary_min_pkr": None,
        "salary_max_pkr": None,
        "salary_is_converted": False,
        "exchange_rate_used": None,
        "exchange_rate_source": None,
    }

    # First evaluate structured_pay if provided by API
    if structured_pay and isinstance(structured_pay, dict):
        if structured_pay.get("state") == "known":
            val = structured_pay.get("value")
            if isinstance(val, dict):
                curr = normalize_currency_code(val.get("currency"))
                min_orig = clean_num(str(val.get("min_amount") or val.get("min") or ""))
                max_orig = clean_num(str(val.get("max_amount") or val.get("max") or ""))
                intv = normalize_interval(val.get("interval") or val.get("unit"))
                if min_orig is not None or max_orig is not None:
                    return _compute_monthly_pkr(
                        salary_text or f"{curr} {min_orig or ''} - {max_orig or ''} ({intv})",
                        curr,
                        intv,
                        min_orig,
                        max_orig,
                    )

    if not salary_text or not isinstance(salary_text, str) or not salary_text.strip():
        return empty_result

    text = salary_text.strip()

    # Match range pattern
    range_match = SALARY_PATTERNS[0].search(text)
    if range_match:
        curr = normalize_currency_code(range_match.group("curr"))
        min_val = clean_num(range_match.group("min"))
        max_val = clean_num(range_match.group("max"))
        intv = normalize_interval(range_match.group("intv"))
        return _compute_monthly_pkr(text, curr, intv, min_val, max_val)

    # Match single figure
    single_match = SALARY_PATTERNS[1].search(text)
    if single_match:
        curr = normalize_currency_code(single_match.group("curr"))
        val = clean_num(single_match.group("val"))
        intv = normalize_interval(single_match.group("intv"))
        return _compute_monthly_pkr(text, curr, intv, val, val)

    # If unparseable free text
    return empty_result


def _compute_monthly_pkr(
    raw_text: str,
    currency: Optional[str],
    interval: str,
    min_orig: Optional[float],
    max_orig: Optional[float],
) -> Dict[str, Any]:
    """Convert original currency & interval to monthly PKR."""
    if not currency or currency not in EXCHANGE_RATES_TO_PKR:
        # Currency unknown: do not guess conversion
        return {
            "salary_text": raw_text,
            "salary_currency": currency,
            "salary_interval": interval,
            "salary_min_original": min_orig,
            "salary_max_original": max_orig,
            "salary_min_pkr": None,
            "salary_max_pkr": None,
            "salary_is_converted": False,
            "exchange_rate_used": None,
            "exchange_rate_source": None,
        }

    rate, source = EXCHANGE_RATES_TO_PKR[currency]
    is_converted = currency != "PKR"

    # Multiplier to convert to monthly amount
    if interval == "year":
        intv_factor = 1.0 / 12.0
    elif interval == "hour":
        intv_factor = STANDARD_MONTHLY_HOURS
    else:
        intv_factor = 1.0

    min_monthly_pkr = round(min_orig * intv_factor * rate, 2) if min_orig is not None else None
    max_monthly_pkr = round(max_orig * intv_factor * rate, 2) if max_orig is not None else None

    # Sanity validation: min <= max
    if min_monthly_pkr is not None and max_monthly_pkr is not None and min_monthly_pkr > max_monthly_pkr:
        min_monthly_pkr, max_monthly_pkr = max_monthly_pkr, min_monthly_pkr

    return {
        "salary_text": raw_text,
        "salary_currency": currency,
        "salary_interval": interval,
        "salary_min_original": min_orig,
        "salary_max_original": max_orig,
        "salary_min_pkr": min_monthly_pkr,
        "salary_max_pkr": max_monthly_pkr,
        "salary_is_converted": is_converted,
        "exchange_rate_used": rate if is_converted else 1.0,
        "exchange_rate_source": source if is_converted else "Base Currency",
    }

"""HireTrends Data Cleaning Subsystem.

Provides text normalization, wage parsing, location standardization,
skill extraction, and data quality assurance.
"""

from .city_normalizer import normalize_location
from .experience_parser import parse_experience
from .quality_checks import perform_quality_checks
from .salary_parser import parse_salary
from .skill_extractor import SkillExtractor
from .title_normalizer import normalize_title
from .workplace_normalizer import normalize_workplace_type


def __getattr__(name):
    if name in ("clean_single_record", "run_cleaning_pipeline"):
        from .clean_jobs import clean_single_record, run_cleaning_pipeline
        return {"clean_single_record": clean_single_record, "run_cleaning_pipeline": run_cleaning_pipeline}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "normalize_title",
    "normalize_location",
    "normalize_workplace_type",
    "parse_experience",
    "parse_salary",
    "SkillExtractor",
    "perform_quality_checks",
    "clean_single_record",
    "run_cleaning_pipeline",
]

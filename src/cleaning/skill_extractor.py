"""HireTrends Technical Skill Extractor.

Extracts technical skills, libraries, frameworks, and cloud platforms from job descriptions
and titles using regex patterns and word boundary guards to prevent false-positive matches.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

DEFAULT_DICTIONARY_PATH = "config/skills_dictionary.json"


class SkillExtractor:
    """Regex-based technical skills extraction engine."""

    def __init__(self, dictionary_path: str = DEFAULT_DICTIONARY_PATH):
        self.dictionary_path = dictionary_path
        self.categories: Dict[str, str] = {}
        self.skill_matchers: List[Tuple[str, str, re.Pattern]] = []
        self._load_dictionary()

    def _compile_pattern(self, name: str, aliases: List[str]) -> re.Pattern:
        """Create a precision regex pattern for a skill and its aliases with word boundaries."""
        patterns = []

        # Special casing for ambiguous short names
        if name == "R":
            # Avoid matching lone letter "R", "R&D", etc.
            return re.compile(
                r"\b(r[\s\-]?programming|r[\s\-]?project|r[\s\-]?lang)\b|"
                r"(?:python|sql|sas|spss|matlab)[,\s\/]+R\b|\bR[,\s\/]+(?:python|sql|sas|spss|matlab)\b",
                re.IGNORECASE,
            )

        if name == "Go":
            # Avoid matching standard English verb "go"
            return re.compile(
                r"\b(golang|go[\s\-]?lang|go\s+programming|go\s+developer|go\s+backend)\b",
                re.IGNORECASE,
            )

        if name == "C":
            return re.compile(
                r"\b(c[\s\-]?programming|c[\s\-]?language)\b",
                re.IGNORECASE,
            )

        if name == "C++":
            return re.compile(r"\b(c\+\+|cpp|c\/c\+\+)\b", re.IGNORECASE)

        if name == "C#":
            return re.compile(r"\b(c\#|csharp|c\#\.net|\.net\s+c\#)\b", re.IGNORECASE)

        if name == "Java":
            # Must not match JavaScript
            return re.compile(r"\bJava\b(?!script)", re.IGNORECASE)

        if name == "Excel":
            # Avoid matching "excellent" or "excellence"
            return re.compile(r"\b(excel|ms[\s\-]?excel|advanced\s+excel|excel\s+vba)\b(?!lent|lence)", re.IGNORECASE)

        if name == "Git":
            return re.compile(r"\b(git|github|gitlab|git[\s\-]?vcs)\b(?!ing)", re.IGNORECASE)

        if name == "CI/CD":
            return re.compile(r"\b(ci[\s\/]cd|continuous\s+integration|jenkins|github\s+actions)\b", re.IGNORECASE)

        # Standard tokens
        escaped_name = re.escape(name)
        patterns.append(r"\b" + escaped_name + r"\b")

        for alias in aliases:
            escaped_alias = re.escape(alias)
            patterns.append(r"\b" + escaped_alias + r"\b")

        combined = "|".join(patterns)
        return re.compile(combined, re.IGNORECASE)

    def _load_dictionary(self) -> None:
        """Load skills taxonomy and compile matchers."""
        if not os.path.exists(self.dictionary_path):
            return

        with open(self.dictionary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_categories = data.get("categories", {})
        for cat_key, cat_data in raw_categories.items():
            cat_name = cat_data.get("name", cat_key)
            self.categories[cat_key] = cat_name

            for item in cat_data.get("skills", []):
                skill_name = item.get("name")
                aliases = item.get("aliases", [])
                if skill_name:
                    pattern = self._compile_pattern(skill_name, aliases)
                    self.skill_matchers.append((skill_name, cat_name, pattern))

    def extract_skills(self, text: Optional[str]) -> Dict[str, Any]:
        """Extract unique technical skills and their categories from input text.

        Args:
            text: Job title or description.

        Returns:
            {
                "skills": list[str],
                "skills_by_category": dict[str, list[str]],
                "skills_count": int
            }
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "skills": [],
                "skills_by_category": {},
                "skills_count": 0,
            }

        matched_skills: Set[str] = set()
        by_category: Dict[str, List[str]] = {}

        for skill_name, cat_name, pattern in self.skill_matchers:
            if pattern.search(text):
                matched_skills.add(skill_name)
                if cat_name not in by_category:
                    by_category[cat_name] = []
                by_category[cat_name].append(skill_name)

        sorted_skills = sorted(list(matched_skills))

        return {
            "skills": sorted_skills,
            "skills_by_category": by_category,
            "skills_count": len(sorted_skills),
        }

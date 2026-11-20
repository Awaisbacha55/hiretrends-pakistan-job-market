"""HireTrends Robots.txt and Source Permission Checker.

Audits whether a given URL is crawlable under robots.txt and verifies
that the source has explicit approval in config/sources.json.
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import urllib.robotparser

import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.SourceChecker")

DEFAULT_USER_AGENT = (
    "HireTrendsResearchBot/1.0 "
    "(+https://github.com/Awaisbacha55/hiretrends-pakistan-job-market; academic research)"
)
DEFAULT_TIMEOUT = 10


def is_valid_url(url: str) -> bool:
    """Validate that a URL has a scheme and netloc."""
    if not url or not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme in ("http", "https") and parsed.netloc)


def build_robots_url(base_url: str) -> str:
    """Construct the robots.txt URL for a given base URL."""
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def fetch_robots_txt(
    base_url: str,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Fetch robots.txt contents for a given base URL.

    Returns:
        (content, status_code, error_message)
    """
    if not is_valid_url(base_url):
        return None, None, f"Invalid base URL format: {base_url}"

    robots_url = build_robots_url(base_url)
    headers = {"User-Agent": user_agent}

    try:
        response = requests.get(robots_url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.text, 200, None
        if response.status_code == 404:
            # 404 means no robots.txt exists, by standard everything is allowed,
            # but we return status for transparent reporting.
            return "", 404, None
        return (
            None,
            response.status_code,
            f"HTTP {response.status_code} while fetching robots.txt",
        )
    except requests.exceptions.Timeout:
        return None, None, f"Timeout after {timeout} seconds fetching {robots_url}"
    except requests.exceptions.RequestException as exc:
        return None, None, f"Request error fetching {robots_url}: {str(exc)}"


def check_robots_txt(
    base_url: str,
    target_url: str,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Check whether a target URL is permitted under robots.txt.

    Implements fail-closed verification: if robots.txt cannot be verified due to
    network errors, HTTP 403 Forbidden, or server errors, access is disallowed.
    """
    result: Dict[str, Any] = {
        "base_url": base_url,
        "target_url": target_url,
        "robots_url": build_robots_url(base_url) if is_valid_url(base_url) else "",
        "user_agent": user_agent,
        "can_fetch": False,
        "crawl_delay": None,
        "status_code": None,
        "verified": False,
        "error": None,
        "disclaimer": (
            "IMPORTANT: robots.txt permission does NOT supersede, replace, "
            "or satisfy platform Terms of Service requirements."
        ),
    }

    if not is_valid_url(base_url):
        result["error"] = f"Invalid base URL: {base_url}"
        return result

    if not is_valid_url(target_url):
        result["error"] = f"Invalid target URL: {target_url}"
        return result

    content, status_code, error = fetch_robots_txt(base_url, user_agent, timeout)
    result["status_code"] = status_code

    if error:
        result["error"] = error
        result["can_fetch"] = False
        result["verified"] = False
        return result

    # Standard RobotFileParser
    parser = urllib.robotparser.RobotFileParser()
    robots_url = build_robots_url(base_url)
    parser.set_url(robots_url)

    if status_code == 404:
        # Standard: missing robots.txt implies unrestricted crawling
        result["can_fetch"] = True
        result["verified"] = True
        result["crawl_delay"] = None
        return result

    try:
        lines = content.splitlines() if content else []
        parser.parse(lines)
        can_fetch = parser.can_fetch(user_agent, target_url)
        crawl_delay = parser.crawl_delay(user_agent)

        result["can_fetch"] = bool(can_fetch)
        result["crawl_delay"] = crawl_delay
        result["verified"] = True
        return result
    except Exception as exc:
        result["error"] = f"Failed to parse robots.txt: {str(exc)}"
        result["can_fetch"] = False
        result["verified"] = False
        return result


def verify_source_permission(
    source_identifier: str,
    sources_config_path: str = "config/sources.json",
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Verify whether a source is marked explicitly APPROVED in configuration.

    Returns:
        (is_approved, source_dict, message)
    """
    if not os.path.exists(sources_config_path):
        return (
            False,
            None,
            f"Sources configuration file not found at: {sources_config_path}",
        )

    try:
        with open(sources_config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return False, None, f"Failed to load sources config: {str(exc)}"

    sources = data.get("sources", [])
    matched = None
    target_clean = source_identifier.strip().lower()

    for src in sources:
        sid = src.get("id", "").strip().lower()
        sname = src.get("name", "").strip().lower()
        sbase = src.get("base_url", "").strip().lower()
        if target_clean in (sid, sname, sbase) or sbase in target_clean:
            matched = src
            break

    if not matched:
        return (
            False,
            None,
            f"Source '{source_identifier}' was not found in sources configuration.",
        )

    status = matched.get("permission_status", "").upper()
    if status == "APPROVED":
        return True, matched, f"Source '{matched.get('name')}' is explicitly APPROVED."
    return (
        False,
        matched,
        f"Source '{matched.get('name')}' is NOT approved (status: {status}). Collection prohibited.",
    )


def format_report(check_result: Dict[str, Any]) -> str:
    """Format check result as human-readable text."""
    lines = [
        "=" * 70,
        "HIRETRENDS SOURCE COMPLIANCE REPORT",
        "=" * 70,
        f"Base URL:      {check_result['base_url']}",
        f"Target URL:    {check_result['target_url']}",
        f"Robots URL:    {check_result['robots_url']}",
        f"User Agent:    {check_result['user_agent']}",
        f"HTTP Status:   {check_result['status_code']}",
        f"Verified:      {'YES' if check_result['verified'] else 'NO (Failed closed)'}",
        f"Robots Allow:  {'PERMITTED' if check_result['can_fetch'] else 'DISALLOWED'}",
        f"Crawl Delay:   {check_result['crawl_delay']} seconds",
    ]
    if check_result.get("error"):
        lines.append(f"Error Details: {check_result['error']}")
    lines.append("-" * 70)
    lines.append(f"LEGAL NOTICE:  {check_result['disclaimer']}")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> int:
    """CLI entry point for checking robots.txt and source compliance."""
    parser = argparse.ArgumentParser(
        description="HireTrends Ethical Robots.txt and Source Compliance Checker",
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL of the target platform (e.g. https://example.com)",
    )
    parser.add_argument(
        "--target-url",
        required=True,
        help="Target page URL to check (e.g. https://example.com/jobs/123)",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Custom user-agent string for evaluation",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP request timeout in seconds",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    result = check_robots_txt(
        base_url=args.base_url,
        target_url=args.target_url,
        user_agent=args.user_agent,
        timeout=args.timeout,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))

    # Exit code: 0 if allowed & verified, 1 otherwise
    return 0 if (result["can_fetch"] and result["verified"]) else 1


if __name__ == "__main__":
    sys.exit(main())

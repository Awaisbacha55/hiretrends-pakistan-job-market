"""Headcount Labs API Connection and Health Verification Client.

Tests connectivity to Headcount Labs job-count endpoint for Pakistan (country=PK)
using credentials loaded securely from .env via python-dotenv.

SECURITY NOTICE:
The API key is loaded in memory and NEVER logged, printed, or exposed.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.HeadcountAPI")

API_BASE_URL = "https://api.headcountlabs.com"
JOB_COUNT_ENDPOINT = f"{API_BASE_URL}/v1/jobs/count"
DEFAULT_TIMEOUT = 15
COUNTRY_CODE = "PK"


def check_api_key_configuration(load_env: bool = True) -> Dict[str, Any]:
    """Load and verify HEADCOUNTLABS_API_KEY from environment.

    NEVER prints, logs, or returns the actual API key.
    """
    if load_env:
        load_dotenv()
    api_key = os.getenv("HEADCOUNTLABS_API_KEY")

    if not api_key:
        return {
            "configured": False,
            "message": "HEADCOUNTLABS_API_KEY is not set or empty in the environment / .env file.",
            "key_length": 0,
        }

    stripped = api_key.strip()
    if not stripped:
        return {
            "configured": False,
            "message": "HEADCOUNTLABS_API_KEY is empty or contains only whitespace.",
            "key_length": 0,
        }

    return {
        "configured": True,
        "message": "HEADCOUNTLABS_API_KEY successfully detected in environment.",
        "key_length": len(stripped),
    }


def verify_headcount_connection(
    country: str = COUNTRY_CODE,
    timeout: int = DEFAULT_TIMEOUT,
    load_env: bool = True,
) -> Dict[str, Any]:
    """Perform connection verification against Headcount Labs job-count endpoint.

    Returns structured status dictionary.
    """
    if load_env:
        load_dotenv()
    api_key = os.getenv("HEADCOUNTLABS_API_KEY")

    if not api_key or not api_key.strip():
        logger.error("Authentication check failed: HEADCOUNTLABS_API_KEY is missing.")
        return {
            "success": False,
            "status_code": None,
            "error_type": "MISSING_CREDENTIALS",
            "message": "HEADCOUNTLABS_API_KEY is missing from environment. Please check your .env file.",
            "data": None,
        }

    clean_key = api_key.strip()
    headers = {
        "Authorization": f"Bearer {clean_key}",
        "Accept": "application/json",
        "User-Agent": (
            "HireTrendsResearchBot/1.0 "
            "(+https://github.com/Awaisbacha55/hiretrends-pakistan-job-market; research project)"
        ),
    }
    params = {"country": country}

    logger.info("Initiating connection test to Headcount Labs API...")
    logger.info("Endpoint: %s | Filter: country=%s", JOB_COUNT_ENDPOINT, country)

    try:
        response = requests.get(
            JOB_COUNT_ENDPOINT,
            headers=headers,
            params=params,
            timeout=timeout,
        )

        logger.info("Received HTTP response status: %d", response.status_code)

        if response.status_code == 200:
            try:
                payload = response.json()
            except ValueError:
                payload = {"raw_text": response.text}

            logger.info("API Connection SUCCESSFUL! Payload received.")
            return {
                "success": True,
                "status_code": 200,
                "error_type": None,
                "message": "Successfully authenticated and retrieved job count.",
                "data": payload,
            }

        elif response.status_code == 401:
            logger.error("Authentication Error (401 Unauthorized): API key invalid or expired.")
            return {
                "success": False,
                "status_code": 401,
                "error_type": "AUTHENTICATION_ERROR",
                "message": "Authentication failed (HTTP 401). Please check that HEADCOUNTLABS_API_KEY is valid.",
                "data": None,
            }

        elif response.status_code == 403:
            logger.error("Access Forbidden (403 Forbidden): Permission denied for this endpoint.")
            return {
                "success": False,
                "status_code": 403,
                "error_type": "FORBIDDEN",
                "message": "Access forbidden (HTTP 403). The API key does not have access to this resource.",
                "data": None,
            }

        elif response.status_code == 429:
            logger.warning("Rate Limit Exceeded (429 Too Many Requests).")
            return {
                "success": False,
                "status_code": 429,
                "error_type": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded (HTTP 429). Please back off before retrying.",
                "data": None,
            }

        else:
            logger.error("Unexpected HTTP response: %d", response.status_code)
            return {
                "success": False,
                "status_code": response.status_code,
                "error_type": f"HTTP_{response.status_code}",
                "message": f"Server responded with unexpected status code {response.status_code}.",
                "data": None,
            }

    except requests.exceptions.Timeout:
        logger.error("Request timed out after %d seconds.", timeout)
        return {
            "success": False,
            "status_code": None,
            "error_type": "TIMEOUT",
            "message": f"Connection timed out after {timeout} seconds.",
            "data": None,
        }

    except requests.exceptions.ConnectionError as exc:
        logger.error("Network connection error: %s", str(exc))
        return {
            "success": False,
            "status_code": None,
            "error_type": "CONNECTION_ERROR",
            "message": "Failed to establish network connection to Headcount Labs API.",
            "data": None,
        }

    except requests.exceptions.RequestException as exc:
        logger.error("Request error occurred: %s", str(exc))
        return {
            "success": False,
            "status_code": None,
            "error_type": "REQUEST_EXCEPTION",
            "message": f"An error occurred while dispatching HTTP request: {str(exc)}",
            "data": None,
        }


def main() -> int:
    """CLI execution for connection check."""
    print("=" * 65)
    print("HIRETRENDS — HEADCOUNT LABS API CONNECTION VERIFICATION")
    print("=" * 65)

    config_info = check_api_key_configuration()
    print(f"Key Configured: {'YES' if config_info['configured'] else 'NO'}")
    print(f"Key Length:     {config_info['key_length']} characters (Key value is redacted)")
    print(f"Status Note:    {config_info['message']}")
    print("-" * 65)

    if not config_info["configured"]:
        print("[ABORT] Cannot test API connection without a configured API key.")
        print("=" * 65)
        return 1

    result = verify_headcount_connection()

    print("\nAPI CONNECTION TEST RESULTS:")
    print("-" * 65)
    print(f"Connection Success: {'YES' if result['success'] else 'NO'}")
    print(f"HTTP Status Code:   {result['status_code']}")
    print(f"Message:            {result['message']}")

    if result["data"]:
        print("\nResponse Payload:")
        print(json.dumps(result["data"], indent=2))

    print("=" * 65)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())

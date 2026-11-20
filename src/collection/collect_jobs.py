"""HireTrends Data Collection Entry Point.

Loads configured sources, validates permissions, and coordinates collection.
Fails safely when no sources are approved.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any, Dict, List

from .check_sources import verify_source_permission
from .scraper import EthicalScraper

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger("HireTrends.CollectJobs")


def load_all_sources(config_path: str = "config/sources.json") -> List[Dict[str, Any]]:
    """Load sources list from JSON configuration."""
    if not os.path.exists(config_path):
        logger.error("Configuration file not found: %s", config_path)
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("sources", [])
    except Exception as exc:
        logger.error("Error reading sources config: %s", exc)
        return []


def get_approved_sources(config_path: str = "config/sources.json") -> List[Dict[str, Any]]:
    """Filter sources list for those with explicit APPROVED status."""
    sources = load_all_sources(config_path)
    return [s for s in sources if s.get("permission_status", "").upper() == "APPROVED"]


def save_raw_dataset(
    records: List[Dict[str, Any]],
    source_id: str,
    output_dir: str = "data/raw",
) -> str:
    """Save collected records to disk in timestamped JSON format."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{source_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info("Saved %d records to %s", len(records), filepath)
    return filepath


def run_collection(
    source_id: str = "opendata_pakistan",
    config_path: str = "config/sources.json",
    output_dir: str = "data/raw",
) -> int:
    """Execute collection pipeline with ethical validation."""
    logger.info("=" * 60)
    logger.info("HIRETRENDS DATA COLLECTION PIPELINE")
    logger.info("=" * 60)

    # Validate permission status
    is_approved, source_meta, message = verify_source_permission(
        source_id,
        sources_config_path=config_path,
    )

    if not is_approved:
        logger.warning(
            "SAFE HALT: Collection cannot proceed for source '%s'.",
            source_id,
        )
        logger.warning("Reason: %s", message)
        logger.info(
            "To collect data, the target source must have permission_status == 'APPROVED' "
            "in %s, accompanied by documented terms approval.",
            config_path,
        )
        # Safe exit code 0 indicating clean intentional halt due to compliance
        return 0

    logger.info("Source '%s' is approved for collection.", source_id)
    # When an approved live source is configured with specific endpoints:
    # Scraper would be instantiated here.
    return 0


def main() -> int:
    """CLI entry point for data collection."""
    parser = argparse.ArgumentParser(
        description="HireTrends Ethical Data Collection Manager",
    )
    parser.add_argument(
        "--source-id",
        default="opendata_pakistan",
        help="Identifier of source to collect (default: opendata_pakistan)",
    )
    parser.add_argument(
        "--config",
        default="config/sources.json",
        help="Path to sources.json configuration",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory to store collected raw data",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List all configured sources and their permission statuses",
    )

    args = parser.parse_args()

    if args.list_sources:
        sources = load_all_sources(args.config)
        print(f"\n{'ID':<20} {'NAME':<30} {'STATUS':<20} {'METHOD':<25}")
        print("-" * 95)
        for s in sources:
            print(
                f"{s.get('id', ''):<20} "
                f"{s.get('name', ''):<30} "
                f"{s.get('permission_status', ''):<20} "
                f"{s.get('allowed_collection_method', ''):<25}"
            )
        return 0

    return run_collection(
        source_id=args.source_id,
        config_path=args.config,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
